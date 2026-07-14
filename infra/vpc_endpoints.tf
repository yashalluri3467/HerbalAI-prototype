# VPC endpoints keep ECS <-> ECR / S3 / CloudWatch Logs / Secrets Manager
# traffic off the public internet and off the NAT gateway (cost + latency).

resource "aws_security_group" "vpce" {
  name        = "${local.name}-vpce-sg"
  description = "Allow HTTPS from within the VPC to interface VPC endpoints."
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.this.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, { Name = "${local.name}-vpce-sg" })
}

# Gateway endpoint for S3 (no cost, attached to route tables).
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = [
    aws_route_table.public.id,
    aws_route_table.private.id,
  ]

  tags = merge(local.common_tags, { Name = "${local.name}-s3-endpoint" })
}

# Interface endpoints (hourly + data-processing charge, but cheaper than NAT egress).
locals {
  interface_endpoints = {
    ecr_api        = "com.amazonaws.${var.region}.ecr.api"
    ecr_dkr        = "com.amazonaws.${var.region}.ecr.dkr"
    logs           = "com.amazonaws.${var.region}.logs"
    secretsmanager = "com.amazonaws.${var.region}.secretsmanager"
  }
}

resource "aws_vpc_endpoint" "interface" {
  for_each = local.interface_endpoints

  vpc_id              = aws_vpc.this.id
  service_name        = each.value
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpce.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, { Name = "${local.name}-${each.key}-endpoint" })
}
