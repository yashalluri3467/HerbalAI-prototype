# HerbalAI - AI-Based Herbal Recommendation & Skin Diagnosis Platform

HerbalAI is a next-generation clinical decision support system that merges **Computer Vision**, a rich **Ayurvedic Herbal Knowledge Base**, a **DNN-powered Recommendation Engine**, and **Explainable AI (Grad-CAM)** to diagnose skin conditions and suggest precise herbal remedies.

---

## 🌟 Key Features

1. **AI Skin Diagnosis**:
   - Analyzes skin images using a calibrated CNN (MobileNetV3 small) to detect conditions like **Acne, Eczema, Pigmentation, Dry Skin, Wrinkles, Psoriasis, Rosacea, and Healthy Skin**.
   - Applies advanced image preprocessing: bilateral denoising and CLAHE contrast enhancement (LAB color space) to draw out diagnostic skin textures.

2. **Ayurvedic Knowledge Base**:
   - Integrates 18 essential Ayurvedic herbs: Neem, Aloe Vera, Turmeric, Tulsi, Amla, Harra, Bahera, Giloy, Mahua, Karanj, Palash, Moringa, Hibiscus, Ashwagandha, Bael, Arjun, Chironji, Bhringraj.
   - Categorizes botanical classifications, active chemical constituents, evidence-based skincare applications, preparation recipes, side effects, and strict contraindications.

3. **Multi-Modal Herb & Leaf Evaluator**:
   - **Identify Herb**: Upload a leaf image to recognize the herbal plant and check its chemical constituents.
   - **Skin + Herb Joint Evaluation**: Upload both skin and leaf images to evaluate how compatible a specific herb is for a diagnosed skin condition, rendering expected efficacy metrics.

4. **Explainable AI (XAI)**:
   - Implements **Grad-CAM** (Gradient-weighted Class Activation Mapping) directly in PyTorch, projecting visual attention heatmaps over the original skin/leaf images to reveal the exact features the AI model focused on.
   - Generates structured, clinical-style text justifications explaining the pharmacological reasons why a herb is recommended.

---

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, PyTorch (Deep Learning), OpenCV (Image Preprocessing), NumPy, Uvicorn.
- **Frontend**: React.js, Vite, Lucide React (Icons), Vanilla CSS (Custom properties, Modern dark-mode layout, Glassmorphic variables).

---

## 🚀 Running the Platform

### 1. Set Up the Backend
First, ensure you have Python 3.10+ installed. Navigate to the `backend` folder:

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
# This will automatically run utils/setup_models.py to pre-train the synthetic models on startup if weights are missing!
uvicorn main:app --reload --port 8000
```
The backend API will run on `http://127.0.0.1:8000`. You can inspect the interactive docs at `http://127.0.0.1:8000/docs`.

### 2. Set Up the Frontend
Open a new terminal window and navigate to the `frontend` folder:

```bash
cd frontend
# Install dependencies
npm install

# Run the development server
npm run dev
```
The React dashboard will launch at `http://localhost:5173`. Open this URL in your web browser.

---

## 📊 Dataset & Production Scale

- For initial demo and local execution, this project automatically generates synthetic skin texture maps (e.g., pustules for acne, scales for psoriasis, lines for wrinkles) and leaf structures to pre-train the classification models. This ensures **zero setup** and immediate usability.
- **Production Dataset Recommendation**: For real-world deployment, we recommend training the models on the Kaggle [Skin Disease Dataset by pacificrm](https://www.kaggle.com/datasets/pacificrm/skindiseasedataset) or the ISIC Archive database, mapping them to the multi-label outputs configured in `models/classifiers.py`.
