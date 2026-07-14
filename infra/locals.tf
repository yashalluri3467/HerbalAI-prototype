locals {
  name = "${var.project_name}-prod"

  # Single VPC CIDR; split into public (ALB/NAT) and private (ECS/RDS) subnets.
  vpc_cidr = "10.0.0.0/16"

  # Two AZs for multi-AZ ALB + RDS + Fargate spread.
  azs = slice(data.aws_availability_zones.available.names, 0, 2)

  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]

  # Frontend origin URL advertised to the backend via CORS (FRONTEND_URL).
  frontend_url = var.domain_name == null ? "https://${aws_cloudfront_distribution.this.domain_name}" : "https://${var.domain_name}"

  # API base URL baked into the frontend build (VITE_API_BASE_URL).
  api_url = var.domain_name == null ? "http://${aws_lb.this.dns_name}" : "https://api.${var.domain_name}"

  common_tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
    Tier      = "prod"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
