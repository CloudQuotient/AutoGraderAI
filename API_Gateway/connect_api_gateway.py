import boto3
import json
import os
from dotenv import load_dotenv

# -----------------------------
# Load environment
# -----------------------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

LAMBDA_NAME = "plagiarism-lambda"
REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

api_client = boto3.client("apigatewayv2", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)
sts = boto3.client("sts")
ACCOUNT_ID = sts.get_caller_identity()["Account"]

# -----------------------------
# Step 1: Create API
# -----------------------------
print("🌐 Creating HTTP API...")
api_name = "plagiarism-api"
api = api_client.create_api(
    Name=api_name,
    ProtocolType="HTTP",
    Description="API Gateway for plagiarism Lambda"
)
api_id = api["ApiId"]
print(f"✅ Created API: {api_name} (ID: {api_id})")

# -----------------------------
# Step 2: Create Lambda integration
# -----------------------------
lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{LAMBDA_NAME}"

integration = api_client.create_integration(
    ApiId=api_id,
    IntegrationType="AWS_PROXY",
    IntegrationUri=lambda_arn,
    PayloadFormatVersion="2.0"
)
integration_id = integration["IntegrationId"]
print(f"🔗 Integration created (ID: {integration_id})")

# -----------------------------
# Step 3: Create POST route
# -----------------------------
route = api_client.create_route(
    ApiId=api_id,
    RouteKey="POST /run",
    Target=f"integrations/{integration_id}"
)
print(f"🚦 Route created: POST /run")

# -----------------------------
# Step 4: Create deployment + stage
# -----------------------------
deployment = api_client.create_deployment(ApiId=api_id, Description="Initial deployment")
api_client.create_stage(
    ApiId=api_id,
    StageName="prod",
    DeploymentId=deployment["DeploymentId"],
    AutoDeploy=True
)
print(f"🚀 Deployed stage: prod")

# -----------------------------
# Step 5: Allow API Gateway to invoke Lambda
# -----------------------------
try:
    lambda_client.add_permission(
        FunctionName=LAMBDA_NAME,
        StatementId="ApiGatewayInvokePermission",
        Action="lambda:InvokeFunction",
        Principal="apigateway.amazonaws.com",
        SourceArn=f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{api_id}/*/*/run"
    )
    print("🔐 Added permission for API Gateway to invoke Lambda.")
except lambda_client.exceptions.ResourceConflictException:
    print("⚠️ Permission already exists — skipping add_permission.")

# -----------------------------
# Step 6: Print invoke URL
# -----------------------------
invoke_url = f"https://{api_id}.execute-api.{REGION}.amazonaws.com/prod/run"
print(f"\n✅ API Gateway connected successfully!")
print(f"🌍 Invoke URL: {invoke_url}")