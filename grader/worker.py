import os
import sys
import json
import tempfile
import time
import shutil
from typing import Dict, Any
from fastapi import FastAPI, Request
import docker

RESOURCE_LIMITS = {'mem_limit': '256m', 'cpu_period': 100000, 'cpu_quota': 100000}
TIMEOUT = 5
RUNTIME_IMAGES = {
    'python': 'autograderai-runtime-python:latest',
    'java': 'autograderai-runtime-java:latest',
    'cpp': 'autograderai-runtime-cpp:latest',
}

app = FastAPI()
client = docker.from_env()

def run_job(job: Dict[str, Any]) -> Dict[str, Any]:
    submission_id = job['submission_id']
    language = job['language']
    source_code = job['source_code']
    test_cases = job['test_cases']
    results = []
    error_message = None
    status = 'success'
    temp_dir = tempfile.mkdtemp()
    try:
        # Write source code to temp file
        if language == 'python':
            code_file = os.path.join(temp_dir, 'main.py')
        elif language == 'java':
            code_file = os.path.join(temp_dir, 'Main.java')
        elif language == 'cpp':
            code_file = os.path.join(temp_dir, 'main.cpp')
        else:
            raise ValueError('Unsupported language')
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(source_code)
        for tc in test_cases:
            input_data = tc['input']
            expected = tc['expected']
            container = None
            try:
                start = time.time()
                container = client.containers.run(
                    RUNTIME_IMAGES[language],
                    volumes={temp_dir: {'bind': '/app', 'mode': 'rw'}},
                    stdin_open=True,
                    mem_limit=RESOURCE_LIMITS['mem_limit'],
                    cpu_period=RESOURCE_LIMITS['cpu_period'],
                    cpu_quota=RESOURCE_LIMITS['cpu_quota'],
                    detach=True
                )
                exec_log = container.exec_run(
                    cmd=['/app/run.sh', os.path.basename(code_file)],
                    stdin=True,
                    socket=True
                )
                sock = exec_log.output
                sock.send(input_data.encode('utf-8'))
                sock.shutdown(socket.SHUT_WR)
                output = b''
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    output += chunk
                sock.close()
                container.reload()
                exit_code = container.attrs['State']['ExitCode']
                end = time.time()
                time_ms = int((end - start) * 1000)
                stdout = output.decode('utf-8').strip()
                stderr = container.logs(stderr=True).decode('utf-8').strip()
                pass_case = stdout.strip() == expected.strip()
                results.append({
                    'input': input_data,
                    'expected': expected,
                    'output': stdout,
                    'pass': pass_case,
                    'time_ms': time_ms,
                    'stderr': stderr,
                    'exit_code': exit_code
                })
            except Exception as e:
                results.append({
                    'input': input_data,
                    'expected': expected,
                    'output': '',
                    'pass': False,
                    'time_ms': 0,
                    'stderr': str(e),
                    'exit_code': None
                })
                status = 'error'
                error_message = str(e)
            finally:
                if container:
                    container.remove(force=True)
        shutil.rmtree(temp_dir)
    except Exception as e:
        status = 'error'
        error_message = str(e)
        shutil.rmtree(temp_dir)
    return {
        'submission_id': submission_id,
        'results': results,
        'status': status,
        'error_message': error_message
    }

if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            job = json.load(f)
        result = run_job(job)
        print(json.dumps(result, indent=2))
    else:
        import uvicorn
        uvicorn.run(app, host='0.0.0.0', port=8000)

@app.post('/run')
async def run_endpoint(request: Request):
    job = await request.json()
    return run_job(job)
