# RDS PostgreSQL in private subnets, TLS enforced (asyncpg ssl=require).
# Single-AZ db.t3.micro for cost; flip Multi-AZ / upsize later.

resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.name}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, { Name = "${local.name}-db-subnet" })
}

resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "Allow PostgreSQL from the ECS tasks only."
  vpc_id      = aws_vpc.this.id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, { Name = "${local.name}-rds-sg" })
}

resource "aws_db_instance" "this" {
  identifier                = "${local.name}-db"
  engine                    = "postgres"
  engine_version            = "16.3"
  instance_class            = var.db_instance_class
  allocated_storage         = var.db_allocated_storage
  db_name                   = var.db_name
  username                  = var.db_username
  password                  = random_password.db.result
  db_subnet_group_name      = aws_db_subnet_group.this.name
  vpc_security_group_ids    = [aws_security_group.rds.id]
  multi_az                  = false
  storage_encrypted         = true
  publicly_accessible       = false
  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.name}-db-final"
  backup_retention_period   = 7
  deletion_protection       = true

  # Force TLS: clients must connect with ssl=require (asyncpg).
  apply_immediately = false

  tags = merge(local.common_tags, { Name = "${local.name}-db" })
}
