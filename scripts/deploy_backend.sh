#!/bin/bash
set -e
# Deploy backend to ECS Fargate
aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment
