import os
import requests


EVAL_SERVICE_URL = os.getenv("EVAL_SERVICE_URL", "http://54.84.174.169:5000/evaluate")
EVAL_TIMEOUT_SECONDS = int(os.getenv("EVAL_SERVICE_TIMEOUT", "180"))


def EvaluateECS(s3_filepath, jsonb):
    """
    Callable function to trigger the remote code evaluation service.
    Args:
        s3_filepath (str): S3 path to the code file.
        jsonb (list): List of test cases, each as a dict with 'input' and 'output'.
    Returns:
        dict: Result of evaluation or error message.
    """
    if not s3_filepath or not jsonb:
        return {"error": "Missing 's3_filepath' or 'jsonb'.", "output": s3_file_path, "output2": jsonb}

    payload = {
        # Provide multiple alias keys for compatibility with different backends
        "s3_filepath": s3_filepath,
        "s3_path": s3_filepath,
        "jsonb": jsonb,
        "testcases": jsonb,
    }

    try:
        resp = requests.post(
            EVAL_SERVICE_URL,
            json=payload,
            timeout=EVAL_TIMEOUT_SECONDS,
        )
        if resp.status_code != 200:
            return {
                "error": f"Evaluation service returned {resp.status_code}",
                "body": resp.text,
            }
        return resp.json()
    except requests.Timeout:
        return {"error": "Evaluation service timeout"}
    except Exception as e:
        return {"error": f"Evaluation service call failed: {e}"}
