# HerbalAI — AWS Deployment Guide

Production deployment of HerbalAI on **AWS ECS Fargate** (backend) + **S3 / CloudFront** (frontend), fully driven by **GitHub Actions** (OIDC, no static keys) and **Terraform** (IaC).

```
GitHub (push main)
   ├─ HerbalAI CI      → lint, build, pytest smoke (uploads frontend-build artifact)
   ├─ HerbalAI Deploy  → build backend image → ECR (+ Trivy) → ECS rolling
   │                        update + S3 sync + CloudFront invalidation
   └─ HerbalAI IaC     → terraform plan (PR) / apply (main)

ECR → ECS Fargate → ALB (ACM + WAF) → api.<domain>
S3  → CloudFront (ACM + WAF) → <domain>
RDS PostgreSQL (private) · Secrets Manager · CloudWatch Logs
```

> The ECR build/push + Trivy scan are folded into the **Deploy** workflow
> (a `build` job the `deploy` job `needs`), so the `:sha` image is
> always present before the ECS task-def register step. No race.

---

## 1. Prerequisites

| Item | Needed for |
|---|---|
| AWS account + IAM admin creds (`aws` CLI configured) | one-time Terraform bootstrap/apply |
| GitHub repo with **Environments/Variables** + **id-token** permission | CI/CD |
| `OPENROUTER_API_KEY` | LLM clinical summaries (optional) |
| (Optional) a Route53 hosted zone + ACM cert in **us-east-1** covering `example.com` **and** `api.example.com` | custom domain + HTTPS |
| Terraform ≥ 1.5 (local, for `init`/`apply` of the bootstrap) | IaC |

> Region is pinned to **us-east-1** because CloudFront ACM certificates live only there.

---

## 2. One-time bootstrap (state backend)

```bash
# 1. (Optional) install Terraform, then:
./scripts/bootstrap-aws.sh        # creates S3 state bucket + DynamoDB lock

cd infra
terraform init                   # seeds state into the bucket above
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Copy `infra/terraform.tfvars.example` → `infra/terraform.tfvars` and fill it. **Never commit the real `.tfvars`.**

> The `apply` runs under your **admin** creds and creates *everything*, including the GitHub OIDC role. CI later assumes that role.

---

## 3. Configure GitHub

After `apply`, copy these outputs and set them as **repo Variables** (`Settings → Secrets and variables → Actions → Variables`):

| Variable | Value (from `terraform output`) |
|---|---|
| `AWS_ROLE_ARN` | `github_actions_role_arn` |
| `ECR_REPO` | `ecr_repository_url` (e.g. `123.dkr.ecr.us-east-1.amazonaws.com/herbalai-prod-backend`) |
| `S3_BUCKET` | `s3_frontend_bucket` |
| `CF_DIST_ID` | the CloudFront distribution id (from AWS console or `aws cloudfront list-distributions`) |
| `VITE_API_BASE_URL` | `api_url` (ALB DNS, or `https://api.<domain>`) — **baked into the frontend build** |
| `API_HEALTH_URL` | `http://<alb-dns>/health` (or `https://api.<domain>/health`) |

> **Chicken-and-egg:** `VITE_API_BASE_URL` must be known at *build* time. For the first deploy without a custom domain, use the ALB DNS from `terraform output alb_dns_name`. Once a domain is wired, update the variable and re-run CI to rebuild the frontend.

The workflows already request `id-token: write`, so OIDC works.

---

## 4. Populate secrets

Terraform creates the secret shell (`herbalai-prod-backend`) with a placeholder. Replace the OpenRouter key (the `DATABASE_URL` is assembled automatically from the RDS endpoint + generated password):

```bash
aws secretsmanager put-secret-value \
  --secret-id herbalai-prod-backend \
  --secret-string '{"OPENROUTER_API_KEY":"sk-or-...","DATABASE_URL":"REUSE_EXISTING"}'
```

> To keep the auto-built `DATABASE_URL`, fetch the current value first and only swap the key:
> `aws secretsmanager get-secret-value --secret-id herbalai-prod-backend --query SecretString`.

---

## 5. First deploy

```bash
git push origin main
```

This triggers `CI` → `Deploy` (Deploy's `build` job builds/pushes the image,
then the `deploy` job runs — ordering is guaranteed):
1. CI lints/builds, runs the pytest smoke suite, and uploads the `frontend-build` artifact.
2. Deploy `build` job builds the backend image (tagged `:sha` + `:latest`) and **Trivy-scans** it (fails on HIGH/CRITICAL) before pushing to ECR.
3. Deploy `deploy` job registers a new ECS task-def revision pinned to `:sha`, rolls the service (ALB health gate = zero downtime), syncs `dist/` to S3, and invalidates CloudFront.

Verify:
```bash
curl -fsS "$(terraform output -raw api_url)/health"     # → {"status":"ok"}
curl -fsS "$(terraform output -raw frontend_url)"         # → HTML
```

---

## 6. Custom domain + HTTPS (recommended)

1. Request an **ACM cert in us-east-1** with SANs `example.com` and `api.example.com` (DNS validation).
2. In `terraform.tfvars`: set `domain_name = "example.com"`, `acm_cert_arn = "<cert-arn>"`, `route53_zone_id = "<zone-id>"`.
3. `terraform apply` → creates Route53 A-records (`@`→CloudFront, `api`→ALB) and switches ALB to HTTPS (HTTP→HTTPS redirect).
4. Update GitHub var `VITE_API_BASE_URL = https://api.example.com` and re-run CI to rebuild the frontend.

Demo mode (no domain) serves the API over **HTTP** on the ALB DNS — fine for testing, not for production.

---

## 7. Rollback

| Layer | Action |
|---|---|
| Backend | `aws ecs update-service --cluster herbalai-prod-cluster --service herbalai-prod-backend --task-definition <prev-revision-arn>` |
| Frontend | S3 versioning restore + `aws cloudfront create-invalidation --paths "/*"` (or re-sync a prior `frontend-build` artifact) |
| Database | RDS point-in-time restore from an automated snapshot |

ECS rolling deploys are themselves zero-downtime; the above are for bad releases.

---

## 8. Cost estimate (us-east-1, single-AZ)

| Service | Approx/mo |
|---|---|
| ECS Fargate 2 vCPU / 4 GiB ×2 tasks | ~$50 |
| RDS db.t3.micro (Single-AZ, 20 GB) | ~$15 |
| ALB | ~$18 |
| NAT Gateway | ~$32 |
| S3 + CloudFront (low traffic) | a few $ |
| Route53 hosted zone | $0.50 |
| ACM | free |
| **Total** | **~$115–150** |

**Levers:** VPC endpoints (already configured) remove NAT egress; Fargate **Spot** for non-prod; upsize RDS later; CloudFront caching cuts backend hits.

---

## 9. Useful commands

```bash
# Watch the ECS rollout
aws ecs describe-services --cluster herbalai-prod-cluster --services herbalai-prod-backend

# Tail logs
aws logs tail /ecs/herbalai-prod-backend --follow

# Re-run only the frontend deploy (after a build fix)
# → Actions → HerbalAI Deploy → Run workflow

# Tear down (destroys RDS — final snapshot is taken)
terraform destroy -var-file=terraform.tfvars
```

## 10. Notes / future

- **Model artifacts** are baked into the image (`backend/models`). For frequent retraining without image rebuilds, mount **EFS** at `/app/models` or download from S3 in the task `lifespan`.
- **GPU**: ECS EC2 with a GPU AMI, or SageMaker async inference / Bedrock for the LLM part.
- **Monitoring**: CloudWatch Container Insights is the baseline; add Managed Prometheus + Grafana for the full brief.
- **Blue/green**: stricter zero-downtime via CodeDeploy (currently rolling).
- **JWT/RBAC, React→TypeScript, 80% coverage, ONNX/PyTorch** are tracked separately as application-modernization work, not part of this deploy.
- **Smaller images:** swap `tensorflow` → `tensorflow-cpu` in `backend/requirements.txt` to trim ~300 MB off the ECR image (Fargate is CPU-only today; rebuild + re-push).
