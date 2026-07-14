# WAF WebACLs: a rate-limit + managed rules on both the ALB (regional)
# and CloudFront (cloudfront scope). The ALB association lives in alb.tf.

locals {
  rate_limit = 2000 # requests per 5-min window per IP
}

resource "aws_wafv2_web_acl" "regional" {
  name        = "${local.name}-alb-waf"
  scope       = "REGIONAL"
  description = "Rate-limit + managed rules for the ALB."

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitPerIP"
    priority = 1
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = local.rate_limit
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitPerIP"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "CommonRuleSet"
    priority = 2
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "IpReputation"
    priority = 3
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "IpReputation"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.name}-alb-waf"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl" "cloudfront" {
  name        = "${local.name}-cf-waf"
  scope       = "CLOUDFRONT"
  description = "Rate-limit + managed rules for CloudFront."

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitPerIP"
    priority = 1
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = local.rate_limit
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitPerIP"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "CommonRuleSet"
    priority = 2
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.name}-cf-waf"
    sampled_requests_enabled   = true
  }
}
