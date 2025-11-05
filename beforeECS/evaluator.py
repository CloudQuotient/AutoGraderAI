import os
import json
import subprocess
import tempfile
import boto3
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---

# NEW: Added Java image
DOCKER_IMAGES = {
    "py": "python:3.10-slim",
    "c": "gcc:latest",
    "cpp": "gcc:latest",
    "java": "openjdk:17-slim"
}
EXEC_TIMEOUT = 30


# --- 2. Secure Code Execution ---

# UPDATED: This function now handles execution logic for all 4 languages
def _run_test_case(code_file_path: str, test_input: str) -> Dict[str, str]:
    """
    Runs a single test case inside an isolated Docker container.
    """
    abs_path = os.path.abspath(code_file_path)
    code_dir = os.path.dirname(abs_path)
    filename = os.path.basename(abs_path)
    # NEW: Java needs the name *without* extension for execution
    filename_no_ext = os.path.splitext(filename)[0] 
    lang = filename.split('.')[-1]

    if lang not in DOCKER_IMAGES:
        return {"stdout": "", "stderr": f"Unsupported language: {lang}"}

    image = DOCKER_IMAGES[lang]
    
    # NEW: Updated command logic
    if lang == 'py':
        command = ['python', f'/app/{filename}']
    elif lang == 'c' or lang == 'cpp':
        # Assumes file was compiled to /app/a.out in the compile step
        command = ['/app/a.out']
    elif lang == 'java':
        # Assumes file was compiled to /app/Main.class (or similar)
        # The 'java' command needs the class name, not the filename
        command = ['java', filename_no_ext] 
    else:
        return {"stdout": "", "stderr": f"Execution logic not defined for: {lang}"}

    docker_cmd = [
        'docker', 'run', '-i', '--rm',
        '-v', f'{code_dir}:/app:rw',
        '-w', '/app',
        image
    ] + command

    try:
        result = subprocess.run(
            docker_cmd,
            input=test_input.encode('utf-8'),
            capture_output=True,
            timeout=EXEC_TIMEOUT
        )
        return {
            "stdout": result.stdout.decode('utf-8').strip(),
            "stderr": result.stderr.decode('utf-8').strip()
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out."}
    except Exception as e:
        return {"stdout": "", "stderr": f"Docker execution failed: {e}"}

# --- 3. Main Evaluation Function ---

# UPDATED: This function now handles compilation for C, C++, and Java
def evaluation(s3_filepath: str, jsonb: List[Dict], local_run: bool = True) -> Dict[str, Any]:
    """
    Downloads a code file, runs it against test cases, and returns feedback.
    """
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # --- Step 1: Get the Code File ---
        if local_run:
            if not os.path.exists(s3_filepath):
                return {"error": f"Local file not found: {s3_filepath}"}
            filename = os.path.basename(s3_filepath)
            local_code_path = os.path.join(temp_dir, filename)
            from shutil import copy
            copy(s3_filepath, local_code_path)
            print(f"[Local Mode] Using code from: {s3_filepath}")
        
        else:
            print(f"[AWS Mode] Downloading from: {s3_filepath}")
            # boto3 will automatically use AWS credentials and region from environment variables
            # (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_DEFAULT_REGION')
            )
            try:
                if not s3_filepath.startswith('s3://'):
                    raise ValueError("Invalid S3 path format. Must be 's3://bucket/key'.")
                bucket, key = s3_filepath[5:].split('/', 1)
                filename = os.path.basename(key)
                local_code_path = os.path.join(temp_dir, filename)
                s3_client.download_file(bucket, key, local_code_path)
            except Exception as e:
                return {"error": f"Failed to download S3 file: {e}"}

        try:
            with open(local_code_path, 'r') as f:
                code_content = f.read()
        except Exception as e:
            code_content = f"Error reading code file: {e}"

        # --- Step 2: Compile (if necessary) ---
        lang = local_code_path.split('.')[-1]
        
        # NEW: Added 'c' and 'java' compile logic
        if lang == 'c' or lang == 'cpp':
            print(f"Compiling {lang} code...")
            compiler = 'g++' if lang == 'cpp' else 'gcc'
            compile_cmd = [
                'docker', 'run', '--rm',
                '-v', f'{temp_dir}:/app:rw', # rw for compiler output
                '-w', '/app',
                DOCKER_IMAGES[lang],
                compiler, f'{filename}', '-o', 'a.out'
            ]
        
        elif lang == 'java':
            print("Compiling Java code...")
            compile_cmd = [
                'docker', 'run', '--rm',
                '-v', f'{temp_dir}:/app:rw', # rw for compiler output
                '-w', '/app',
                DOCKER_IMAGES[lang],
                'javac', f'{filename}'
            ]
        
        else:
            compile_cmd = None # Python doesn't need compilation

        if compile_cmd:
            compile_result = subprocess.run(compile_cmd, capture_output=True, timeout=120)
            if compile_result.returncode != 0:
                error_msg = compile_result.stderr.decode('utf-8')
                results.append({
                    "test_case": 0,
                    "status": "Compile Error",
                    "error": error_msg
                })
                return {"results": results}

        # --- Step 3: Run Test Cases ---
        print(f"Running {len(jsonb)} test cases...")
        for i, item in enumerate(jsonb):
            # ... (rest of the function is unchanged) ...
            test_input = item['input']
            expected_output = item['output']
            
            run_output = _run_test_case(local_code_path, test_input)
            stdout = run_output['stdout']
            stderr = run_output['stderr']

            case_result = {
                "test_case": i + 1,
                "input": test_input,
                "expected": expected_output
            }

            if stderr:
                case_result["status"] = "Error"
                # Check if it's just a Docker image pull message
                if "Pulling from library" in stderr or "Downloaded newer image" in stderr:
                    case_result["error"] = "Docker image pull in progress"
                else:
                    case_result["error"] = stderr
            elif stdout == expected_output:
                case_result["status"] = "Passed"
                case_result["actual"] = stdout
            else:
                case_result["status"] = "Failed"
                case_result["actual"] = stdout
            
            results.append(case_result)

        # --- Step 4: Return Results ---
        print("Test execution complete.")
        return {"results": results}

# --- 4. Example Local Execution ---

if __name__ == "__main__":
    
    # 1. Create dummy files
    with open("smth.py", "w") as f:
        f.write("a, b = map(int, input().split()); print(a + b)")

    with open("smth.cpp", "w") as f:
        f.write("#include <iostream>\nint main() { int a, b; std::cin >> a >> b; std::cout << (a + b); return 0; }")
    
    with open("smth.c", "w") as f:
        f.write("#include <stdio.h>\nint main() { int a, b; scanf(\"%d %d\", &a, &b); printf(\"%d\", a + b); return 0; }")

    # IMPORTANT: For Java, the filename MUST match the class name.
    # We will name the file "Main.java"
    with open("Main.java", "w") as f:
        f.write("import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        System.out.print(a + b);\n    }\n}")

    # 3. Define the test cases
    test_cases = [
        {"input": "2 3", "output": "5"},
        {"input": "10 30", "output": "40"}
    ]
    
    print("--- Testing Python (smth.py) ---")
    py_result = evaluation(s3_filepath="smth.py", jsonb=test_cases, local_run=True)
    print(json.dumps(py_result, indent=2))
    
    print("\n--- Testing C++ (smth.cpp) ---")
    cpp_result = evaluation(s3_filepath="smth.cpp", jsonb=test_cases, local_run=True)
    print(json.dumps(cpp_result, indent=2))

    print("\n--- Testing C (smth.c) ---")
    c_result = evaluation(s3_filepath="smth.c", jsonb=test_cases, local_run=True)
    print(json.dumps(c_result, indent=2))
    
    print("\n--- Testing Java (Main.java) ---")
    java_result = evaluation(s3_filepath="Main.java", jsonb=test_cases, local_run=True)
    print(json.dumps(java_result, indent=2))
    
    # Clean up dummy files
    os.remove("smth.py")
    os.remove("smth.cpp")
    os.remove("smth.c")
    os.remove("Main.java")