terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "autograder-vpc"
  cidr   = "10.0.0.0/16"
}

module "ecs" {
  source = "../modules/ecs"
  cluster_name = var.ecs_cluster_name
}

module "api_gateway" {
  source = "../modules/api_gateway"
}

module "cognito" {
  source = "../modules/cognito"
}

module "s3_submissions" {
  source = "../modules/s3"
  bucket_name = var.submissions_bucket_name
}

module "s3_frontend" {
  source = "../modules/s3"
  bucket_name = var.frontend_bucket_name
}

resource "aws_cloudwatch_log_group" "main" {
  name = "/autograderai/main"
  retention_in_days = 30
}
