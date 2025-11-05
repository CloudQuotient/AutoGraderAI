
from beforeECS.evaluator import evaluation  # Import the correct function

def EvaluateECS(s3_filepath, jsonb):
    """
    Callable function to trigger the code evaluation.
    Args:
        s3_filepath (str): S3 path to the code file.
        jsonb (list): List of test cases, each as a dict with 'input' and 'output'.
    Returns:
        dict: Result of evaluation or error message.
    """
    if not s3_filepath or not jsonb:
        return {"error": "Missing 's3_filepath' or 'jsonb'."}

    try:
        # Call your imported evaluation function, setting local_run=False
        result = evaluation(s3_filepath, jsonb, local_run=False)
        return result
    except ValueError as e:
        # Handle the "Invalid S3 URI" error
        return {"error": str(e)}
    except Exception as e:
        # General error handler
        print(f"An unexpected error occurred: {e}")
        return {"error": f"An internal server error occurred: {e}"}