output "frontend_url" {
  description = "URL users visit (CloudFront domain or custom apex)."
  value       = local.frontend_url
}

output "api_url" {
  description = "Backend API base URL (baked into the frontend build)."
  value       = local.api_url
}

output "alb_dns_name" {
  description = "ALB DNS name (used for api.<domain> alias / health checks)."
  value       = aws_lb.this.dns_name
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain."
  value       = aws_cloudfront_distribution.this.domain_name
}

output "ecr_repository_url" {
  description = "ECR repo URL the CI pushes the backend image to."
  value       = aws_ecr_repository.this.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  value = aws_ecs_service.this.name
}

output "rds_endpoint" {
  description = "RDS endpoint (embedded in the DATABASE_URL secret)."
  value       = aws_db_instance.this.address
  sensitive   = true
}

output "s3_frontend_bucket" {
  value = aws_s3_bucket.this.bucket
}

output "github_actions_role_arn" {
  description = "IAM role ARN to set as AWS_ROLE_ARN in GitHub repo Variables."
  value       = aws_iam_role.github_actions.arn
}

output "secret_arn" {
  description = "Secrets Manager ARN holding OPENROUTER_API_KEY / DATABASE_URL."
  value       = aws_secretsmanager_secret.this.arn
  sensitive   = true
}
