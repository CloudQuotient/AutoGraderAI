import json
import boto3

runtime = boto3.client("sagemaker-runtime")

def lambda_handler(event, context):
    """
    Lambda receives event with:
    {
        "s3_urls": ["s3://bucket/code1.py", "s3://bucket/code2.py"]
    }
    """
    s3_urls = event.get("s3_urls", [])
    payload = json.dumps({"s3_urls": s3_urls})

    response = runtime.invoke_endpoint(
        EndpointName="graphcodebert-plagiarism-endpoint",  # same as deployed
        ContentType="application/json",
        Body=payload
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
