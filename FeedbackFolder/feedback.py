import boto3
import json
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# This has a cooldown of around a minute before sending continous requests after filling up a form related to usage information in the AWS Console

def get_code_feedback_from_bedrock(s3_uri: str, model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
    """
    Downloads code from an S3 URI and sends it to Amazon Bedrock (Claude 3 Sonnet) 
    for short, structured feedback (<10 lines).
    """

    if not s3_uri.startswith("s3://"):
        raise ValueError("Invalid S3 URI. Must start with 's3://'")

    bucket_name, key = s3_uri.replace("s3://", "").split("/", 1)

    print(f"Downloading code from: s3://{bucket_name}/{key}")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    code_content = obj["Body"].read().decode("utf-8")
    print(f"Code file downloaded successfully. Size: {len(code_content)} bytes")

    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    prompt = f"""
    You are an expert software reviewer.
    Analyze the code below and return feedback strictly in 5 short bullet points only.
    Each section must be a single concise line — no explanations, no paragraphs.
    Keep total feedback under 10 lines.

    Format exactly like this:
    1. Time Complexity:
    2. Space Complexity:
    3. Logic Optimization:
    4. Code Style:
    5. Security/Robustness:

    Code:
    ```
    {code_content}
    ```
    """

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 400,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    })

    print("Sending request to Claude 3 Sonnet on Amazon Bedrock...")

    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        feedback = result["content"][0]["text"].strip()

        print("\nShort Structured Feedback:\n")
        print(feedback)
        return feedback

    except Exception as e:
        print(f"Error during Bedrock model call: {e}")
        return None