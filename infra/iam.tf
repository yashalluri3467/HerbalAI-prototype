# --- ECS task execution role (pulls image, reads secrets, writes logs) ---
resource "aws_iam_role" "ecs_execution" {
  name = "${local.name}-ecs-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_ecr" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy" "ecs_execution_inline" {
  name = "${local.name}-ecs-exec-inline"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Read the backend secret (OPENROUTER_API_KEY, DATABASE_URL).
        Action   = ["secretsmanager:GetSecretValue"]
        Effect   = "Allow"
        Resource = aws_secretsmanager_secret.this.arn
      },
      {
        # Write container logs to CloudWatch.
        Action = [
          "logs:CreateLogStream",
          "logs:CreateLogGroup",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.this.arn}:*"
      }
    ]
  })
}

# --- ECS task role (runtime permissions for the container process) ---
# Minimal by default. Add SSM/externals as needed; no broad perms granted.
resource "aws_iam_role" "ecs_task" {
  name = "${local.name}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

# --- GitHub OIDC provider + role for passwordless CI/CD ---
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [var.github_oidc_thumbprint]
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "github_actions" {
  name = "${local.name}-github-actions"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRoleWithWebIdentity"
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:ref:refs/heads/main"
        }
      }
    }]
  })

  tags = local.common_tags
}

# CI/CD + Terraform permissions. For full `terraform apply` coverage this is
# necessarily broad; tighten per-resource once the stack is stable.
resource "aws_iam_role_policy" "github_actions_inline" {
  name = "${local.name}-github-actions-inline"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # ECR auth + image push.
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
        ]
        Effect   = "Allow"
        Resource = aws_ecr_repository.this.arn
      },
      {
        # ECS rolling deploy.
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:ListTaskDefinitions",
          "ecs:TagResource",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        # Frontend deploy (S3 sync) + CloudFront invalidation.
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "cloudfront:CreateInvalidation",
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.this.arn,
          "${aws_s3_bucket.this.arn}/*",
          aws_cloudfront_distribution.this.arn,
        ]
      },
      {
        # Terraform-managed services (VPC/IAM/RDS/CF/WAF/Route53/ALB/logs).
        # Broadened for the prototype bootstrap; TIGHTEN to per-resource
        # policies once the stack is stable.
        Action = [
          "ec2:Describe*", "ec2:CreateVpc", "ec2:DeleteVpc",
          "ec2:CreateSubnet", "ec2:DeleteSubnet", "ec2:ModifySubnetAttribute",
          "ec2:CreateInternetGateway", "ec2:AttachInternetGateway", "ec2:DeleteInternetGateway",
          "ec2:CreateNatGateway", "ec2:DeleteNatGateway", "ec2:CreateEip", "ec2:DeleteEip",
          "ec2:CreateRouteTable", "ec2:DeleteRouteTable", "ec2:CreateRoute", "ec2:ReplaceRoute", "ec2:DeleteRoute",
          "ec2:AssociateRouteTable", "ec2:DisassociateRouteTable",
          "ec2:CreateSecurityGroup", "ec2:DeleteSecurityGroup", "ec2:AuthorizeSecurityGroupIngress", "ec2:RevokeSecurityGroupIngress",
          "ec2:CreateVpcEndpoint", "ec2:DeleteVpcEndpoint", "ec2:ModifyVpcEndpoint", "ec2:CreateVpcEndpointServiceConfiguration",
          "ec2:CreateTags", "ec2:DeleteTags",
          "iam:CreateRole", "iam:DeleteRole", "iam:GetRole", "iam:ListRoles",
          "iam:CreatePolicy", "iam:DeletePolicy", "iam:GetPolicy",
          "iam:AttachRolePolicy", "iam:DetachRolePolicy",
          "iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:GetRolePolicy",
          "iam:PassRole", "iam:CreateOpenIDConnectProvider", "iam:DeleteOpenIDConnectProvider",
          "rds:CreateDBInstance", "rds:DeleteDBInstance", "rds:ModifyDBInstance", "rds:CreateDBSnapshot",
          "rds:CreateDBSubnetGroup", "rds:DeleteDBSubnetGroup", "rds:AddTagsToResource",
          "rds:Describe*", "rds:List*", "rds:RestoreDBInstanceFromDBSnapshot",
          "cloudfront:CreateDistribution", "cloudfront:UpdateDistribution", "cloudfront:DeleteDistribution",
          "cloudfront:GetDistribution", "cloudfront:GetDistributionConfig", "cloudfront:ListDistributions",
          "cloudfront:CreateCloudFrontOriginAccessControl", "cloudfront:GetCloudFrontOriginAccessControl",
          "cloudfront:TagResource", "cloudfront:ListTagsForResource",
          "wafv2:CreateWebACL", "wafv2:UpdateWebACL", "wafv2:DeleteWebACL", "wafv2:GetWebACL",
          "wafv2:AssociateWebACL", "wafv2:DisassociateWebACL", "wafv2:TagResource", "wafv2:ListWebACLs",
          "route53:ChangeResourceRecordSets", "route53:ListResourceRecordSets",
          "route53:GetHostedZone", "route53:ListHostedZones", "route53:GetHealthCheck", "route53:ListHealthChecks",
          "elasticloadbalancing:CreateLoadBalancer", "elasticloadbalancing:DeleteLoadBalancer",
          "elasticloadbalancing:ModifyLoadBalancerAttributes", "elasticloadbalancing:AddTags",
          "elasticloadbalancing:CreateTargetGroup", "elasticloadbalancing:DeleteTargetGroup", "elasticloadbalancing:ModifyTargetGroup",
          "elasticloadbalancing:RegisterTargets", "elasticloadbalancing:DeregisterTargets",
          "elasticloadbalancing:CreateListener", "elasticloadbalancing:DeleteListener", "elasticloadbalancing:ModifyListener",
          "elasticloadbalancing:Describe*", "elasticloadbalancing:AddTags",
          "logs:CreateLogGroup", "logs:DeleteLogGroup", "logs:DescribeLogGroups",
          "logs:PutRetentionPolicy", "logs:TagLogGroup", "logs:TagResource",
          "s3:CreateBucket", "s3:DeleteBucket", "s3:GetBucket*", "s3:ListAllMyBuckets",
          "s3:PutBucketVersioning", "s3:PutBucketPolicy", "s3:PutBucketPublicAccessBlock",
          "s3:PutBucketEncryption", "s3:PutBucketTagging",
          "dynamodb:CreateTable", "dynamodb:DeleteTable", "dynamodb:DescribeTable", "dynamodb:TagResource"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
