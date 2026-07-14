# Secrets are stored in Secrets Manager and injected into the ECS task at
# runtime (never baked into the image or committed). The placeholder version
# below lets `terraform apply` succeed; REPLACE the values immediately via:
#   aws secretsmanager put-secret-value \
#     --secret-id herbalai-prod-backend \
#     --secret-string '{"OPENROUTER_API_KEY":"...","DATABASE_URL":"postgresql+asyncpg://..."}'
#
# DATABASE_URL must use the asyncpg driver and force TLS, e.g.:
#   postgresql+asyncpg://USER:PASS@<rds-endpoint>:5432/herbalai?ssl=require
resource "aws_secretsmanager_secret" "this" {
  name                    = "${local.name}-backend"
  recovery_window_in_days = 7

  tags = merge(local.common_tags, { Name = "${local.name}-backend-secret" })
}

# The DATABASE_URL is assembled from the RDS endpoint + generated
# password so the value is correct end-to-end. Replace OPENROUTER_API_KEY
# via the console/CLI after apply.
resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  secret_string = jsonencode({
    OPENROUTER_API_KEY = "REPLACE_ME"
    DATABASE_URL       = "postgresql+asyncpg://${var.db_username}:${random_password.db.result}@${aws_db_instance.this.address}:5432/${var.db_name}?ssl=require"
  })
}
