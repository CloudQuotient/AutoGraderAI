import json
import boto3
import os

runtime = boto3.client("sagemaker-runtime")

def lambda_handler(event, context):
    """
    Lambda receives event:
    {
        "s3_embedding_urls": [...],
        "filenames": [...],
        "bucket": "autograder-dummy",
        "threshold": 0.85
    }
    and forwards it directly to the SageMaker endpoint.
    """

    # Validate required keys
    required_keys = ["s3_embedding_urls", "filenames", "bucket", "threshold"]
    for key in required_keys:
        if key not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Missing required key: {key}"})
            }

    # Forward event directly as payload
    payload = json.dumps(event)

    response = runtime.invoke_endpoint(
        EndpointName=os.environ["SAGEMAKER_ENDPOINT"],
        ContentType="application/json",
        Body=payload
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
