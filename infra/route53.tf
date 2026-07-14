# Route53 records (only when a custom domain is supplied).
# apex -> CloudFront, api -> ALB. Requires the hosted zone to pre-exist.

data "aws_route53_zone" "this" {
  count   = var.domain_name == null ? 0 : 1
  zone_id = var.route53_zone_id
}

resource "aws_route53_record" "apex" {
  count   = var.domain_name == null ? 0 : 1
  zone_id = data.aws_route53_zone.this[0].zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.this.domain_name
    zone_id                = local.cf_hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "api" {
  count   = var.domain_name == null ? 0 : 1
  zone_id = data.aws_route53_zone.this[0].zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.this.dns_name
    zone_id                = aws_lb.this.zone_id
    evaluate_target_health = false
  }
}
