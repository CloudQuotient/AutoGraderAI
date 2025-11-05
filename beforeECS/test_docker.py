# test_evaluate_ecs.py

from app_ECS import EvaluateECS  # Replace with actual module name

def test_evaluate_ecs():
    # Example fake S3 path (replace with a real one if you have it)
    s3_filepath = "s3://autograder-dummy/submissions/code1.py"
    
    # Example test cases — input/output pairs your evaluator should use
    jsonb = [
        {"input": "2 3", "output": "5"},   # e.g. tests addition
        {"input": "10 -5", "output": "5"}  # another test case
    ]

    # Call the function
    result = EvaluateECS(s3_filepath, jsonb)

    # Print the result so you can see what happened
    print("Evaluation result:")
    print(result)


if __name__ == "__main__":
    test_evaluate_ecs()
