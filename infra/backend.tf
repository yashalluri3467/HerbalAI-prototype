# Remote state for the production infrastructure.
#
# The S3 bucket + DynamoDB lock MUST exist before `terraform init`.
# Create them once with `scripts/bootstrap-aws.sh` (or the AWS console).
# Bucket/key/table names are intentionally hard-coded here because Terraform
# backend blocks cannot reference variables.
terraform {
  backend "s3" {
    bucket         = "herbalai-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "herbalai-tf-lock"
    encrypt        = true
  }
}
