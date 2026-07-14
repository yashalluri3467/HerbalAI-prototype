# HerbalAI - AI-Based Herbal Recommendation & Skin Diagnosis Platform

HerbalAI is a clinical decision support system that merges **Computer Vision**, a rich
**Ayurvedic Herbal Knowledge Base**, a **DNN-powered Recommendation Engine**, and an
**LLM-generated Clinical Reference Summary** to diagnose skin conditions and suggest precise
herbal remedies.

The models are built with **TensorFlow / Keras** using ImageNet transfer learning
(MobileNetV2, optionally EfficientNetB0). There is no PyTorch, no synthetic pre-training, and
no Grad-CAM in the current pipeline.

---

## 🌟 Key Features

1. **AI Skin Diagnosis**:
   - Analyzes skin images with a calibrated CNN to detect **22 dermatology conditions**
     (Acne, Eczema, Psoriasis, Rosacea, Vitiligo, Tinea, SkinCancer, etc.).
   - The skin model is trained from real datasets under `D:\skin datasets` (see below) and
     served by `POST /api/predict/skin`.

2. **Ayurvedic Knowledge Base**:
   - Integrates 18 Ayurvedic herbs: Neem, Aloe Vera, Turmeric, Tulsi, Amla, Harra, Bahera,
     Giloy, Mahua, Karanj, Palash, Moringa, Hibiscus, Ashwagandha, Bael, Arjun, Chironji,
     Bhringraj.
   - Categorizes botanical classifications, active chemical constituents, evidence-based
     skincare applications, preparation recipes, side effects, and strict contraindications.

3. **Multi-Modal Herb & Leaf Evaluator**:
   - **Identify Herb**: Upload a leaf image to recognize the herbal plant and check its
     chemical constituents. (Model: `medicinal_leaves`, 200+ leaf classes.)
   - **Skin + Herb Joint Evaluation**: Upload both skin and leaf images to evaluate how
     compatible a specific herb is for a diagnosed skin condition, rendering expected
     efficacy metrics.

4. **LLM Clinical Reference**:
   - Generates a grounded, knowledge-base-backed clinical summary for the detected condition
     and recommended herbs via the OpenRouter LLM (no fabrication — it refuses when no KB
     entry exists).

---

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, TensorFlow / Keras (Deep Learning), OpenCV (Image
  Preprocessing), NumPy, Uvicorn.
- **Frontend**: React.js, Vite, Lucide React (Icons), Vanilla CSS (custom properties,
  modern dark-mode glassmorphic layout).

---

## 🗄️ Session History & Database

Every diagnosis (skin, leaf, joint, or raw TF prediction) can be **persisted** to a database
so the history survives refreshes and is shared across sessions. The UI's
**Diagnostic Session History** tab (`/api/sessions`) reads from it automatically.

- **Backend**: `backend/database/db.py` (async SQLAlchemy engine) + `backend/database/models.py`
  (`SessionRecord`). Tables are created idempotently on startup — no migration tooling needed.
- **Graceful degradation**: if `DATABASE_URL` is unset, persistence is **disabled** and
  predictions still succeed; the frontend falls back to a local in-browser log.
- **Enable it**: set `DATABASE_URL` to an async SQLAlchemy URL, e.g.
  `postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require` (managed Postgres / Neon). See
  `backend/.env.example`.

## 🚀 Running the Platform

### 1. Set Up the Backend
Ensure you have Python 3.11 installed (pinned for TensorFlow compatibility). Navigate to the
`backend` folder:

```bash
cd backend
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```

The backend API runs on `http://127.0.0.1:8000`. Interactive docs: `http://127.0.0.1:8000/docs`.

> Note: trained models must exist under `backend/models/<dataset>/`. If missing, run the
> training steps below (or `python verify_backend.py` to check what is present).

### 2. Set Up the Frontend
Open a new terminal and navigate to the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

The React dashboard launches at `http://localhost:5173`.

---

## 📊 Training the Models

Both models share one trainer (`backend/utils/train_tf_models.py`) and one predictor
(`backend/services/tf_predictor.py`). Data is assembled into a class-per-folder layout under
`backend/data/<dataset>/prepared`.

### Skin model (`skin_disease`, 22 classes)
1. Merge the six sources under `D:\skin datasets` into the canonical 22-class taxonomy:
   ```bash
   python -m utils.merge_skin_datasets --source "D:\skin datasets"
   ```
2. Train both candidate backbones and deploy the best by validation macro-F1:
   ```bash
   python -m utils.train_tf_models --dataset skin_disease --train-both
   ```
   This writes `backend/models/skin_disease/{model.keras, class_names.txt}`.

### Herb model (`medicinal_leaves`)
1. Merge the leaf datasets, then train:
   ```bash
   python -m utils.merge_leaf_datasets
   python -m utils.train_tf_models --dataset medicinal_leaves
   ```

Training uses ImageNet transfer learning with a frozen-then-fine-tuned backbone, class
weights for imbalance, early stopping, and a learning-rate plateau reducer. A per-class
benchmark report is written next to each model.

---

## ☁️ Deploy on AWS (ECS Fargate + S3 / CloudFront)

HerbalAI deploys to AWS as: the **backend on ECS Fargate** (image in ECR, fronted by an
ALB with ACM + WAF, talking to **RDS PostgreSQL** and **Secrets Manager**, logging to CloudWatch) and
the **frontend as a static SPA on S3 + CloudFront**. CI/CD is **GitHub Actions** (OIDC, no static
keys) driven by **Terraform** (IaC under `infra/`).

Runtime env (injected by ECS, not committed): `PORT` (8000), `FRONTEND_URL`
(CORS allow-list for the CloudFront domain), and `OPENROUTER_API_KEY` + `DATABASE_URL`
(from Secrets Manager).

Full step-by-step, cost estimate, rollback, and troubleshooting:
**[docs/aws-deployment.md](docs/aws-deployment.md)**.
