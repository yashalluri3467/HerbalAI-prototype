# HerbalAI — Client Delivery Checklist

**Delivery date:** 2026-07-11
**Repository:** https://github.com/yashalluri3467/HerbalAI-prototype
**Deployment status:** ✅ Configs ready — ⏸️ **NOT yet deployed (standby)**. No `docker-compose up`
or `kubectl apply` has been run. Activate on the client's signal.

---

## 1. What's in this delivery

- [x] **Full source code** pushed to the GitHub repo (main branch, latest commit).
- [x] **Backend (FastAPI + TensorFlow)**: skin-disease (22 classes) & medicinal-leaf classifiers,
      Ayurvedic knowledge base, DNN recommender, optional OpenRouter LLM clinical summaries.
- [x] **Frontend (React + Vite)**: glassmorphic dashboard with skin / leaf / joint / TF prediction
      tabs and a **Diagnostic Session History** view.
- [x] **Session-history database**: async SQLAlchemy persistence (`backend/database/`).
      Tables auto-create on startup; degrades gracefully when `DATABASE_URL` is unset.
- [x] **Containers**: `backend/Dockerfile`, `frontend/Dockerfile` (+ `nginx.conf`), `.dockerignore`s.
- [x] **Docker Compose**: `docker-compose.yml` (backend :8000, frontend :8080).
- [x] **Kubernetes manifests**: `k8s/` (backend + frontend Deployments/Services, Secrets).
- [x] **Docs**: `README.md`, `PRODUCTION_GUIDE.md`, and this checklist.

---

## 2. How to run locally (no DB required)

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate      # or: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                 # optional; edit keys if needed
uvicorn main:app --reload                            # http://127.0.0.1:8000  (docs at /docs)

# Frontend (new terminal)
cd frontend
npm install
npm run dev                                          # http://localhost:5173
```

Without `DATABASE_URL`, predictions work and history is kept in the browser only.

---

## 3. Enable the database (optional but recommended for production)

1. Provision a Postgres instance (e.g. Neon). Copy its **async** connection string:
   `postgresql+asyncpg://USER:PASS@HOST/DBNAME?ssl=require`.
2. Set it as `DATABASE_URL` in `backend/.env` (local) **or** the `database-url` key of the
   `herbalai-secrets` Kubernetes Secret.
3. Restart the backend. On startup it creates the `sessions` table and the
   **Diagnostic Session History** tab switches from local log → shared DB.
4. Verify: `GET /api/sessions` returns `{"db_enabled": true, "sessions": [...]}`.

---

## 4. Deployment — READY, on standby

**Docker Compose** (`docker-compose.yml`):
```bash
export DATABASE_URL="postgresql+asyncpg://..."   # optional
docker compose up --build -d
# frontend -> http://localhost:8080 , backend API -> http://localhost:8000/docs
```

**Kubernetes** (`k8s/`):
```bash
kubectl apply -f k8s/secret.yaml
# (optional) kubectl create secret generic herbalai-secrets \
#   --from-literal=database-url="$DATABASE_URL" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/backend-deployment.yaml -f k8s/backend-service.yaml \
             -f k8s/frontend-deployment.yaml -f k8s/frontend-service.yaml
# frontend exposed via LoadBalancer on localhost:80
```

> Nothing above has been executed yet — configs are validated and committed, deployment is
> paused pending client go-ahead.

---

## 5. Health & verification

- [ ] `GET /` → `{"status": "online", ...}` (backend alive).
- [ ] `GET /api/sessions` → `db_enabled` flag reflects whether `DATABASE_URL` is set.
- [ ] `cd backend && python verify_backend.py` → confirms deps, modules, knowledge base, models.
- [ ] Run a skin prediction in the UI → row appears in **Diagnostic Session History**.

---

## 6. Pre-handoff checklist

- [x] Code reviewed and committed.
- [x] `git push origin main` completed; repo is current.
- [x] Deployment manifests present and syntactically valid.
- [x] Database wiring (Compose + K8s) added as optional/empty → safe standby.
- [x] Documentation updated (README, PRODUCTION_GUIDE, this checklist).
- [ ] Client confirms deployment window → then run Compose/K8s apply (out of scope until then).

---

## 7. Known limitations / next steps

- Persistence uses `create_all` (no Alembic migrations yet) — fine for v1; add migrations if
  the `SessionRecord` schema evolves.
- History images are stored as base64 in the DB; for high volume consider object storage.
- LLM summaries require an OpenRouter key; without it the feature silently disables.
