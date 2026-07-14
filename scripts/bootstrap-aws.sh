#!/usr/bin/env bash
# bootstrap-aws.sh — one-time prep for the Terraform backend state.
#
# Creates the S3 bucket + DynamoDB lock table that `infra/backend.tf`
# references. Idempotent. Requires the AWS CLI configured with an
# account that can create S3/DynamoDB in us-east-1.
#
# Usage:
#   ./scripts/bootstrap-aws.sh            # uses us-east-1
#   AWS_REGION=us-east-1 ./scripts/bootstrap-aws.sh
#
# After this, run `terraform -chdir=infra init` to seed the state.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
BUCKET="herbalai-tf-state"
TABLE="herbalai-tf-lock"

echo ">> Using region: $REGION"

# --- S3 bucket (versioned, encrypted, public-access blocked) ---
if aws s3api head-bucket --bucket "$BUCKET" --region "$REGION" >/dev/null 2>&1; then
  echo ">> S3 bucket '$BUCKET' already exists — skipping."
else
  echo ">> Creating S3 bucket '$BUCKET'..."
  # us-east-1 needs the create-bucket call without LocationConstraint.
  if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
  else
    aws s3api create-bucket --bucket "$BUCKET" \
      --region "$REGION" --create-bucket-configuration "LocationConstraint=$REGION"
  fi
  aws s3api put-bucket-versioning \
    --bucket "$BUCKET" --versioning-configuration Status=Enabled --region "$REGION"
  aws s3api put-bucket-encryption \
    --bucket "$BUCKET" \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}' \
    --region "$REGION"
  aws s3api put-public-access-block \
    --bucket "$BUCKET" \
    --public-access-block-configuration '{"BlockPublicAcls":true,"BlockPublicPolicy":true,"IgnorePublicAcls":true,"RestrictPublicBuckets":true}' \
    --region "$REGION"
  echo ">> S3 bucket created."
fi

# --- DynamoDB lock table ---
if aws dynamodb describe-table --table-name "$TABLE" --region "$REGION" >/dev/null 2>&1; then
  echo ">> DynamoDB table '$TABLE' already exists — skipping."
else
  echo ">> Creating DynamoDB table '$TABLE'..."
  aws dynamodb create-table \
    --table-name "$TABLE" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION" >/dev/null
  echo ">> DynamoDB table created."
fi

echo ">> Bootstrap complete. Next: terraform -chdir=infra init && terraform -chdir=infra apply"
