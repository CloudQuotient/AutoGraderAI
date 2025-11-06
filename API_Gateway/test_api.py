import json
import requests

# Replace this with your API Gateway invoke URL
API_URL = "https://ydag0mhwq4.execute-api.ap-south-1.amazonaws.com/prod/run"

# Sample payload (same format as your Lambda test event)
payload = {
    "s3_embedding_urls": [
        "s3://autograder-dummy/embeddings/code1.py.npy",
        "s3://autograder-dummy/embeddings/code2.py.npy",
        "s3://autograder-dummy/embeddings/code3.py.npy"
    ],
    "filenames": ["code1.py", "code2.py", "code3.py"],
    "bucket": "autograder-dummy",
    "threshold": 0.85
}

# Send POST request
print("🚀 Sending request to API Gateway...")
response = requests.post(API_URL, json=payload)

# Parse and display the response
if response.status_code == 200:
    try:
        data = response.json()
        print("✅ Response from API Gateway (Lambda output):")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print("⚠️ Non-JSON response:")
        print(response.text)
else:
    print(f"❌ Error {response.status_code}: {response.text}")