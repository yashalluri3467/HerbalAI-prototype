# HerbalAI Skincare – Production Deployment & Model Training Guide

This guide details how to train, evaluate, and deploy the HerbalAI machine-learning models
for a production-grade clinical decision support product.

---

## 🌟 Production System Architecture

HerbalAI's machine-learning engine is built with **TensorFlow / Keras** using ImageNet
transfer learning. The default backbone is **MobileNetV2** (fast on CPU, strong accuracy);
**EfficientNetB0** is trained as an alternative and the better validation macro-F1 model is
deployed. Both skin and herb classifiers share one generic trainer
(`backend/utils/train_tf_models.py`) and one predictor (`backend/services/tf_predictor.py`).

```
                   +---------------------------+
                   |    Client API Request     |
                   +-------------+-------------+
                                 | (Raw Image)
                                 v
                   +---------------------------+
                   |  tf_predictor.py          |
                   |  (Decode + Resize +       |
                   |   Rescale 1/255)          |
                   +-------------+-------------+
                                 | (Normalized tensor)
                                 v
                   +---------------------------+
                   |  Keras Model (.keras)     |
                   |  MobileNetV2 / EfficientNetB0
                   +-------------+-------------+
                                 | (Class probabilities)
                                 v
                   +---------------------------+
                   |  Recommender + LLM Summary|
                   |       API Response        |
                   +---------------------------+
```

The deployed models live under `backend/models/<dataset>/model.keras` with a companion
`class_names.txt`. No quantization, TorchScript, or ONNX step is required — Keras SavedModels
load and run directly on CPU (Render) or GPU.

---

## 🚀 Step 1: Prepare the Datasets

Images are arranged one folder per class under `backend/data/<dataset>/prepared`.

### Skin (`skin_disease`, 22 classes)
Merge the six sources under `D:\skin datasets` into the canonical 22-class taxonomy
(dataset 6), augmenting only clearly-matching classes from the other sets:

```bash
cd backend
python -m utils.merge_skin_datasets --source "D:\skin datasets"
```

### Herb (`medicinal_leaves`)
```bash
cd backend
python -m utils.merge_leaf_datasets
```

---

## 🚀 Step 2: Train & Select the Best Backbone

```bash
cd backend

# Skin: train MobileNetV2 + EfficientNetB0, deploy the best by val macro-F1
python -m utils.train_tf_models --dataset skin_disease --train-both

# Herb: train MobileNetV2 (CPU-friendly default)
python -m utils.train_tf_models --dataset medicinal_leaves --epochs 15 --batch-size 32
```

Training highlights:
- **Two-phase transfer learning**: frozen backbone (head only) → fine-tune top third.
- **Class weights** correct for label imbalance after merging heterogeneous sources.
- **ModelCheckpoint + EarlyStopping + ReduceLROnPlateau** avoid over-fitting.
- **GPU auto-detection**: uses all visible CUDA devices when present, else CPU.
- A per-class **benchmark report** (`benchmark_report.md`) and confusion matrix are written
  next to each model; the skin run also writes `backend/skin_benchmark_report.md`.

---

## 📊 Step 3: Verify the Deployment

Run the verification utility to confirm every expected model is present and loadable:

```bash
cd backend
python verify_backend.py
```

---

## 🛠️ Step 4: Configure FastAPI for Production

Deploy the backend with the `.env` configuration in `backend/` (copy from `.env.example`):

```env
# OpenRouter LLM API Details (optional – enables clinical summaries)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/auto

# Session-history database (OPTIONAL — leave empty to disable persistence)
# Async SQLAlchemy URL, e.g. postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require
DATABASE_URL=

# Feature toggles
KNOWLEDGE_BASE_ENABLED=true
LLM_SUGGESTIONS_ENABLED=true
IMAGE_ENHANCEMENT_ENABLED=true
```

> The session-history store (`backend/database/`) records every diagnosis to Postgres.
> Tables are created automatically on startup. If `DATABASE_URL` is empty the app runs
> without persistence and predictions are unaffected. In Kubernetes the same value is fed
> via the `herbalai-secrets` `database-url` key (see `k8s/secret.yaml`).

Start the server (e.g. on Render, CPU instances):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

> [!TIP]
> MobileNetV2 is recommended for low-cost CPU cloud deployments (Render, AWS t3.medium,
> DigitalOcean Basic). If you have dedicated GPU hardware (CUDA), EfficientNetB0 is selected
> automatically when it wins on validation macro-F1.

---

## 🧑‍💻 Developer Quick Reference

### Module Reference
- Dataset merge (skin): `backend/utils/merge_skin_datasets.py`
- Dataset merge (herb): `backend/utils/merge_leaf_datasets.py`
- Dataset prep / preprocessing: `backend/utils/tf_preprocess.py`
- Trainer + backbone selection: `backend/utils/train_tf_models.py`
- Predictor / inference: `backend/services/tf_predictor.py`
- Recommender: `backend/services/recommender.py`
- LLM summary: `backend/services/llm_service.py`
- Knowledge base: `backend/database/knowledge_base.py`
- Deployment verification: `backend/verify_backend.py`

---

## ☁️ Deploy on AWS (ECS Fargate + S3 / CloudFront)

For production hosting, HerbalAI ships a complete AWS deployment (not Render/Vercel):

- **Backend** → ECR image → **ECS Fargate** service behind an ALB (ACM TLS + WAF rate-limiting) → RDS PostgreSQL (private subnets, TLS) + Secrets Manager.
- **Frontend** → static build in **S3**, served via **CloudFront** (ACM TLS, OAC).
- **CI/CD** → GitHub Actions (OIDC) + **Terraform** in `infra/` (state in S3 + DynamoDB lock).
- **Zero-downtime** rolling deploys; **Trivy** image scans in CI; **CloudWatch** logs.

Step-by-step (bootstrap, GitHub variables, secrets, domain/TLS, rollback, cost):
see **[docs/aws-deployment.md](docs/aws-deployment.md)**.

> The `k8s/` manifests remain valid for **local** Kind/Docker-Desktop development only;
> the production path is ECS/Fargate per the above.
