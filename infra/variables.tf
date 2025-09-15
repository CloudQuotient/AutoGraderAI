variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "default"
}

variable "submissions_bucket_name" {
  description = "Name of the S3 bucket for submissions"
  type        = string
}

variable "cognito_user_pool_name" {
  description = "Name for Cognito User Pool"
  type        = string
}

variable "ecr_repository_name" {
  description = "Name for ECR repository"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name for ECS cluster"
  type        = string
}
