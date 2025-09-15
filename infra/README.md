# Infrastructure (Terraform)

This folder contains Terraform code to provision core AWS resources for AutoGrader.AI.

## Usage

1. Install [Terraform](https://www.terraform.io/downloads.html) v1.5+
2. Configure your AWS credentials (see [docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#authentication)).
3. Initialize Terraform:
   ```sh
   terraform init
   ```
4. Plan/apply as needed:
   ```sh
   terraform plan
   terraform apply
   ```

## Modules
- `modules/s3`: S3 bucket for submissions
- `modules/cognito`: Cognito User Pool for authentication
- `modules/ecr`: ECR repository for container images
- `modules/ecs`: ECS cluster and Fargate task definition

## Placeholders
- Fill in AWS account ID, region, and other required values in `variables.tf` before applying.
