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
  region  = var.aws_region
  profile = var.aws_profile
}

module "s3" {
  source = "./modules/s3"
  bucket_name = var.submissions_bucket_name
}

module "cognito" {
  source = "./modules/cognito"
  user_pool_name = var.cognito_user_pool_name
}

module "ecr" {
  source = "./modules/ecr"
  repository_name = var.ecr_repository_name
}

module "ecs" {
  source = "./modules/ecs"
  cluster_name = var.ecs_cluster_name
}
