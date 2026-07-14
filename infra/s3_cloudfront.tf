# Frontend: private S3 bucket served exclusively through CloudFront (OAC).
# Vite content-hashes assets, so long-TTL caching is safe; we invalidate
# "/*" on each deploy. SPA deep-links fall back to index.html (200).

resource "aws_s3_bucket" "this" {
  # Globally-unique name: prefix + account id.
  bucket = "${local.name}-frontend-${data.aws_caller_identity.current.account_id}"

  tags = merge(local.common_tags, { Name = "${local.name}-frontend" })
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Allow ONLY the CloudFront distribution (OAC) to read objects.
data "aws_iam_policy_document" "cf_oac" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.this.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.this.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.this.id
  policy = data.aws_iam_policy_document.cf_oac.json
}

resource "aws_cloudfront_origin_access_control" "this" {
  name                              = "${local.name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

locals {
  # Managed cache policy: CachingOptimized.
  cf_cache_policy_id = "658327ea-f89d-4fab-a63f-7afc9a57f430"
  # CloudFront's fixed hosted-zone id (for Route53 alias records).
  cf_hosted_zone_id = "Z2FDTNDATAQYW2"
}

resource "aws_cloudfront_distribution" "this" {
  enabled             = true
  default_root_object = "index.html"
  comment             = "${local.name} frontend"
  price_class         = "PriceClass_100"
  http_version        = "http2"

  origin {
    domain_name              = aws_s3_bucket.this.bucket_regional_domain_name
    origin_id                = "s3-frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.this.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-frontend"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    cache_policy_id        = local.cf_cache_policy_id
  }

  # SPA fallback: missing paths serve index.html with 200.
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  # Custom cert when a domain is supplied; else CloudFront's default *.cloudfront.net cert.
  dynamic "viewer_certificate" {
    for_each = var.domain_name == null ? [] : [1]
    content {
      acm_certificate_arn      = var.acm_cert_arn
      ssl_support_method       = "sni-only"
      minimum_protocol_version = "TLSv1.2_2021"
    }
  }
  dynamic "viewer_certificate" {
    for_each = var.domain_name == null ? [1] : []
    content {
      cloudfront_default_certificate = true
    }
  }

  aliases = var.domain_name == null ? [] : [var.domain_name]

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  web_acl_id = aws_wafv2_web_acl.cloudfront.arn

  tags = local.common_tags
}
