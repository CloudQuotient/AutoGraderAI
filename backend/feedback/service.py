import boto3
from typing import Dict

BEDROCK_ENDPOINT = 'bedrock-llm-endpoint'  # Replace with your endpoint name

PROMPT_TEMPLATE = '''
Summarize the following code for clarity, style, and efficiency.

Code:
{code}

Instructions:
- Summarize code clarity.
- Suggest style improvements.
- Estimate time and space complexity.
Return JSON with keys: clarity, style, efficiency.
'''

def generate_feedback(submission_id: str, code: str) -> Dict:
    client = boto3.client('sagemaker-runtime')
    prompt = PROMPT_TEMPLATE.format(code=code)
    response = client.invoke_endpoint(
        EndpointName=BEDROCK_ENDPOINT,
        ContentType='application/json',
        Body=f'{{"prompt": "{prompt}"}}'
    )
    feedback = response['Body'].read().decode('utf-8')
    # Assume model returns valid JSON
    import json
    feedback_json = json.loads(feedback)
    return {
        'submission_id': submission_id,
        'feedback': feedback_json
    }
