variable "project_name" {
  description = "Short, lower-case project identifier used to prefix all resource names."
  type        = string
  default     = "herbalai"
}

variable "region" {
  description = "AWS region. MUST be us-east-1 because CloudFront ACM certs live only there."
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Custom domain (e.g. 'example.com'). When null, the stack uses default AWS DNS and serves the API over HTTP only (demo mode)."
  type        = string
  default     = null
}

variable "acm_cert_arn" {
  description = "ACM certificate ARN (must be in us-east-1) for api.<domain_name>. Required only when domain_name is set and you want HTTPS on the ALB."
  type        = string
  default     = null
}

variable "route53_zone_id" {
  description = "Route53 hosted-zone ID for domain_name (used for apex + api A-alias records). Required only when domain_name is set."
  type        = string
  default     = null
}

variable "github_repo" {
  description = "GitHub 'owner/repo' used to scope the OIDC trust policy for CI/CD."
  type        = string
}

variable "db_name" {
  description = "RDS PostgreSQL database name."
  type        = string
  default     = "herbalai"
}

variable "db_username" {
  description = "RDS PostgreSQL master username."
  type        = string
  default     = "herbalai"
}

variable "db_instance_class" {
  description = "RDS instance class. db.t3.micro is the free-tier-eligible, low-cost default."
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GiB."
  type        = number
  default     = 20
}

variable "fargate_cpu" {
  description = "Fargate task CPU units (2048 = 2 vCPU)."
  type        = number
  default     = 2048
}

variable "fargate_memory" {
  description = "Fargate task memory in MiB (must be valid for the chosen CPU)."
  type        = number
  default     = 4096
}

variable "desired_count" {
  description = "Initial desired count of Fargate tasks."
  type        = number
  default     = 2
}

variable "max_count" {
  description = "Maximum tasks for autoscaling."
  type        = number
  default     = 6
}

variable "github_oidc_thumbprint" {
  description = "SHA1 thumbprint of the GitHub OIDC server root CA (DigiCert Global Root G2). Verify at https://github.com/actions/oidc-provider-bug; change if GitHub rotates its CA."
  type        = string
  default     = "6938fd4d98bab03faadb97b34396831e3780aea1"
}
