# HerbalAI — Client Manual & Delivery Guide

**Delivery date:** 2026-07-11
**Repository:** https://github.com/yashalluri3467/HerbalAI-prototype
**Status:** ✅ **LIVE / DEPLOYED** — frontend and backend are running in production.

---

## 0. Access the live system (start here — no install needed)

| What | URL |
|------|-----|
| 🌐 **Web app (frontend)** | https://herbal-ai-prototype-g2pk.vercel.app/ |
| 🔧 **Backend API (JSON)** | https://herbalai-backend.onrender.com/ |
| 📖 **Backend API docs (Swagger UI)** | https://herbalai-backend.onrender.com/docs |
| 💓 **Backend health check** | https://herbalai-backend.onrender.com/health |

Open the **web app URL** in any modern browser. That is the finished product — upload
images, read diagnoses and herbal recommendations, and toggle features from the UI. No
setup, account, or install required.

> **Cold-start note:** the backend runs on Render's free tier and spins down after a period
> of inactivity. The *first* request after it has been idle can take ~10–30 s while TensorFlow
> loads; subsequent requests are fast. This is normal.

---

## 1. What HerbalAI does

HerbalAI is a clinical decision-support platform that combines Computer Vision, an Ayurvedic
herbal knowledge base, a recommendation engine, and an optional LLM clinical summary to
diagnose skin conditions and suggest herbal remedies.

- **AI Skin Diagnosis** — CNN detects **22 dermatology conditions** (Acne, Eczema, Psoriasis,
  Rosacea, Vitiligo, Tinea, Skin Cancer, etc.). `POST /api/predict/skin`
- **Ayurvedic Knowledge Base** — 18 herbs (Neem, Aloe Vera, Turmeric, Tulsi, Amla, …) with
  constituents, applications, recipes, side effects, and contraindications. `GET /api/herbs`
- **Herb / Leaf Identification** — upload a leaf image to recognize the plant
  (`medicinal_leaves`, 200+ classes). `POST /api/predict/leaf`
- **Joint Skin + Herb Evaluation** — upload a skin image **and** a leaf image to score how
  compatible a specific herb is for the diagnosed condition. `POST /api/predict/joint`
- **Raw TensorFlow Prediction** — pick any served model dataset and run an image through it.
  `GET /api/tf/datasets` lists them; `POST /api/tf/predict/{datasetName}` runs one.
- **LLM Clinical Reference** — grounded clinical summary for the detected condition + herbs
  (requires an OpenRouter key; silently disabled without one).

---

## 2. Method 1 — Use the live web app (recommended for end users)

1. Go to **https://herbal-ai-prototype-g2pk.vercel.app/**.
2. Use the tabs:
   - **Skin Diagnosis** — click *upload*, choose a skin photo, submit → top condition + confidence + herbal suggestions.
   - **Identify Herb** — upload a leaf photo → recognized herb + constituents.
   - **Joint Evaluation** — upload a skin photo **and** a leaf photo → compatibility / efficacy score.
   - **TF Prediction** — choose a model dataset from the dropdown, upload an image → raw model output.
   - **Settings** — toggle *Knowledge Base*, *LLM Suggestions*, and *Image Enhancement* on/off (applies live).
   - **Diagnostic Session History** — list of past diagnoses.
3. Results appear in the dashboard; herbal remedies and (if enabled) an LLM summary are shown.
4. Session History on the live site: because the database is not enabled in production, history
   falls back to a **local in-browser log** (cleared when you clear browser storage). To get a
   shared, persistent history across devices, enable the database — see §8.

---

## 3. Method 2 — Use the REST API directly (developers / integrations)

The backend is a public FastAPI service. Every UI action is just an HTTP call you can make
yourself with `curl`, Postman, or any language.

**Base URL:** `https://herbalai-backend.onrender.com`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Service status (`{"status":"online",...}`) |
| GET | `/health` | Health probe (`{"status":"ok"}`) |
| GET | `/api/settings` | Current feature toggles |
| PUT | `/api/settings` | Update toggles (JSON body) |
| GET | `/api/herbs` | Ayurvedic knowledge base (18 herbs) |
| GET | `/api/tf/datasets` | List of served TF model datasets |
| POST | `/api/predict/skin` | Skin image → 22-class diagnosis (multipart `file`) |
| POST | `/api/predict/leaf` | Leaf image → herb ID (multipart `file`) |
| POST | `/api/predict/joint` | Skin + leaf images → joint eval (multipart `skin_file`,`leaf_file`) |
| POST | `/api/tf/predict/{datasetName}` | Raw TF prediction for a dataset (multipart `file`) |
| GET | `/api/sessions?limit=&offset=` | Diagnosis history (empty unless DB enabled) |

**Interactive docs:** open **https://herbalai-backend.onrender.com/docs** — try any endpoint
from the browser with the "Try it out" button.

**Example — diagnose a skin image:**
```bash
curl -F "file=@skin.jpg" https://herbalai-backend.onrender.com/api/predict/skin
```

**Example — list knowledge-base herbs:**
```bash
curl https://herbalai-backend.onrender.com/api/herbs
```

> CORS is open (`*`) and the API sends no cookies, so browser and server-to-server calls both
> work from any origin. The Vercel frontend reaches the API through a same-origin `/api` proxy.

---

## 4. Method 3 — Run locally (for development)

Requires Python 3.11 (pinned for TensorFlow) and Node.js 18+.

```bash
# Terminal 1 — Backend
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows  (or: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
cp .env.example .env                                 # optional; edit keys if needed
uvicorn main:app --reload                            # http://127.0.0.1:8000  (Swagger at /docs)

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev                                          # http://localhost:5173
```

Without `DATABASE_URL`, predictions work and history is kept in the browser only. The Vite dev
server proxies `/api` → `http://127.0.0.1:8000`, so the UI "just works" with no env config.

---

## 5. Method 4 — Docker Compose (single-machine deploy)

```bash
# optional: enable persistence
export DATABASE_URL="postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require"

docker compose up --build -d
# frontend UI -> http://localhost:8080
# backend API  -> http://localhost:8000/docs
```

Frontend is served by nginx (config in `frontend/nginx.conf`); backend by uvicorn.

---

## 6. Method 5 — Kubernetes (cluster deploy)

```bash
kubectl apply -f k8s/secret.yaml
# optional: kubectl create secret generic herbalai-secrets \
#   --from-literal=database-url="$DATABASE_URL" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/backend-deployment.yaml -f k8s/backend-service.yaml \
             -f k8s/frontend-deployment.yaml -f k8s/frontend-service.yaml
# frontend exposed via LoadBalancer on localhost:80
```

---

## 7. Live deployment architecture

```
 Browser
   │  https://herbal-ai-prototype-g2pk.vercel.app/
   ▼
 ┌──────────────────────────┐         /api/*  (proxied, same-origin)
 │  Vercel  (React + Vite)  │ ───────────────────────────────┐
 │  frontend/vercel.json    │                                  ▼
 └──────────────────────────┘                    ┌──────────────────────────┐
                                                 │  Render  (FastAPI + TF)  │
                                                 │  https://herbalai-…onrender.com
                                                 │  port from $PORT, /health │
                                                 └──────────────────────────┘
```

- **Frontend:** static React+Vite SPA built by Vercel from the `frontend/` directory.
- **Backend:** FastAPI+uvicorn container on Render, binding Render's injected `$PORT`.
- **Glue:** `frontend/vercel.json` rewrites `/api/*` → the Render backend, so the browser
  talks same-origin and no CORS configuration is needed by the client.
- **CORS:** backend allows all origins (`*`) and sends no credentials; safe for the proxy and
  for direct API calls.

---

## 8. Enable the session-history database (optional, recommended for shared history)

The live backend currently has `DATABASE_URL` **unset**, so history is empty/shared-off.

1. Provision a Postgres instance (Render Postgres, Neon, etc.). Copy its **async** string:
   `postgresql+asyncpg://USER:PASS@HOST/DBNAME?ssl=require`.
2. In the **Render** dashboard, add `DATABASE_URL` to the backend service's environment, then
   redeploy. The `sessions` table auto-creates on startup.
3. Verify: `GET /api/sessions` returns `{"db_enabled": true, "sessions": [...]}`.

> ⚠️ Before enabling the DB, harden `backend/database/db.py`: add `pool_pre_ping`, a connect
> timeout, and fix the `ssl=require` handling (asyncpg ignores libpq `sslmode`). Without this,
> a cold Postgres can hang startup and re-trigger the earlier wakeup-loop symptom.

---

## 9. Health & verification

- [x] `GET /health` → `{"status":"ok"}` (backend alive on Render).
- [x] `GET /api/settings` → returns current toggles.
- [x] `GET /api/tf/datasets` → lists the 4 served model datasets.
- [x] Web app loads at the Vercel URL and reaches the backend through the `/api` proxy.
- [ ] (Optional) Enable `DATABASE_URL` → `GET /api/sessions` shows `db_enabled: true`.
- Local check: `cd backend && python verify_backend.py` confirms deps, knowledge base, models.

---

## 10. Known limitations / next steps

- **Persistence** uses `create_all` (no Alembic migrations yet) — fine for v1; add migrations
  if the `SessionRecord` schema evolves.
- History images are stored as base64 in the DB; for high volume consider object storage.
- **LLM summaries** require an OpenRouter key; without it the feature silently disables.
- **Cold starts** on Render's free tier add latency to the first request after idle.
- **Session history is empty on the live site** until a `DATABASE_URL` is configured (see §8).

---

## 11. Credits

**HerbalAI** was developed by **@sunnexussolutions**.

Special recognition goes to **Charitha Reddy** for her contributions to the design,
development, and delivery of this project — from the AI skin-diagnosis and herbal
recommendation pipelines to the React/Vite frontend and the cloud deployment on Vercel
and Render.

Thank you for bringing the HerbalAI platform to life.

---

*Delivered and verified live on 2026-07-11. Web app: https://herbal-ai-prototype-g2pk.vercel.app/
Backend: https://herbalai-backend.onrender.com/ — docs at /docs.*
