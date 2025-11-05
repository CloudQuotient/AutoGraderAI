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
    or (via API Gateway)
    {
        "body": "{\"s3_embedding_urls\": [...], ...}"
    }
    """

    try:
        # 🔹 Handle both direct Lambda invoke and API Gateway invoke
        if "body" in event and isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event

        # Validate required keys
        required_keys = ["s3_embedding_urls", "filenames", "bucket", "threshold"]
        for key in required_keys:
            if key not in body:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Missing required key: {key}"})
                }

        # Forward payload to SageMaker endpoint
        payload = json.dumps(body)
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

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }