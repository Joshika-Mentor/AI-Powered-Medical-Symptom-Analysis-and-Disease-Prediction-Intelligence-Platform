# 🏥 MedAssist AI — AI-Powered Medical Symptom Analysis & Disease Prediction Platform

> An intelligent clinical decision-support system that leverages machine learning to analyse patient symptoms, predict diseases, assess health risks, and recommend personalised treatments.

---

## 📌 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [ML Models](#ml-models)
- [Screenshots](#screenshots)
- [Future Scope](#future-scope)
- [Contributors](#contributors)
- [License](#license)

---

## 🧠 Overview

**MedAssist AI** (also branded as **HealthSight AI**) is a full-stack web application designed to assist healthcare professionals in making faster, data-driven clinical decisions. The platform accepts patient symptoms as input, runs them through trained machine-learning models, and returns:

- **Disease predictions** with confidence scores
- **Risk-level assessments** (Low / Medium / High / Critical)
- **Personalised treatment recommendations**
- **Visual health reports & analytics dashboards**

The system is built with a modern microservice-inspired architecture — a **Python FastAPI** backend for ML inference and a **Next.js (React)** frontend for a responsive, animated user interface.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Authentication** | Login/Signup with animated pill-mascot UI and session management |
| 🩺 **Symptom Assessment** | Multi-step questionnaire that collects patient symptoms, vitals, and medical history |
| 🤖 **Disease Prediction** | ML model predicts the most likely disease based on symptom vectors |
| ⚠️ **Risk Assessment** | Calculates a risk score (Low → Critical) using patient age, vitals, and symptom severity |
| 💊 **Treatment Recommendations** | Context-aware suggestions including medications, lifestyle changes, and specialist referrals |
| 📊 **Analytics Dashboard** | Visual charts (bar, pie, line) summarising patient trends and prediction accuracy |
| 📄 **Health Reports** | Downloadable patient reports with diagnosis summaries |
| 🧪 **Integration Testing** | Built-in testing panel to verify backend connectivity and model responses |
| 📖 **Documentation** | In-app docs explaining each module for easy onboarding |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core language |
| **FastAPI** | High-performance async REST API framework |
| **Uvicorn** | ASGI server |
| **scikit-learn** | ML model training and inference |
| **SQLite** | Lightweight database for user and patient data |
| **JWT (PyJWT)** | Token-based authentication |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React-based SSR/CSR framework |
| **TypeScript** | Type-safe JavaScript |
| **Tailwind CSS** | Utility-first styling |
| **Framer Motion** | Smooth animations and transitions |
| **Lucide React** | Modern icon library |
| **canvas-confetti** | Fun confetti effects on login |
| **Recharts** | Data visualisation (charts & graphs) |

### DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerisation for both services |
| **Docker Compose** | Multi-container orchestration |

---

## 📁 Project Structure

```
MedAssistAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py              # Authentication endpoints (login/signup)
│   │   │   └── medical.py           # Medical prediction endpoints
│   │   ├── core/
│   │   │   └── security.py          # JWT token handling
│   │   ├── db/
│   │   │   └── database.py          # SQLite database setup
│   │   ├── ml_engine/
│   │   │   ├── disease_prediction.py    # Disease prediction logic
│   │   │   ├── feature_engineering.py   # Symptom feature extraction
│   │   │   ├── recommendation_engine.py # Treatment recommendation engine
│   │   │   ├── risk_assessment.py       # Risk score calculation
│   │   │   ├── symptom_understanding.py # NLP symptom parsing
│   │   │   ├── train_model.py           # Model training script
│   │   │   └── disease_model.pkl        # Trained ML model (serialised)
│   │   └── main.py                  # FastAPI app entry point
│   ├── medassist.db                 # SQLite database file
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile                   # Backend Docker config
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Main page (Login + Dashboard)
│   │   │   ├── layout.tsx           # Root layout
│   │   │   └── globals.css          # Global styles
│   │   ├── components/
│   │   │   ├── Assessment.tsx       # Patient assessment form
│   │   │   ├── TreatmentRecs.tsx    # Treatment recommendations view
│   │   │   ├── HealthReports.tsx    # Health reports view
│   │   │   ├── AnalyticsDashboard.tsx # Analytics charts
│   │   │   ├── IntegrationTesting.tsx # Testing panel
│   │   │   └── Documentation.tsx    # In-app documentation
│   │   └── context/
│   │       └── PatientContext.tsx    # Global patient state management
│   ├── package.json                 # Node.js dependencies
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   ├── tsconfig.json                # TypeScript configuration
│   └── Dockerfile                   # Frontend Docker config
├── docker-compose.yml               # Multi-service orchestration
├── start.ps1                        # PowerShell start script
├── START_MEDASSIST.bat              # One-click Windows launcher
└── README.md                        # This file
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** and **npm** installed
- **Git** installed

### Option 1: One-Click Launch (Windows)
1. Double-click **`START_MEDASSIST.bat`** on your Desktop.
2. Two terminal windows will open (backend + frontend).
3. Your browser will automatically open to the login page.

### Option 2: Manual Setup

#### 1. Clone the repository
```bash
git clone https://github.com/Joshika-Mentor/AI-Powered-Medical-Symptom-Analysis-and-Disease-Prediction-Intelligence-Platform.git
cd AI-Powered-Medical-Symptom-Analysis-and-Disease-Prediction-Intelligence-Platform
git checkout V-Swetha
```

#### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

#### 4. Open in browser
Navigate to **http://localhost:3000**

### Option 3: Docker Compose
```bash
docker-compose up --build
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT token |
| `POST` | `/api/medical/predict` | Submit symptoms and get disease prediction |
| `GET`  | `/api/medical/history` | Retrieve patient prediction history |
| `GET`  | `/docs` | Interactive Swagger API documentation |

---

## 🤖 ML Models

### Disease Prediction Model
- **Algorithm**: scikit-learn classifier (serialised as `disease_model.pkl`)
- **Input**: Encoded symptom vectors, patient age, vitals
- **Output**: Predicted disease label + confidence score

### Risk Assessment Engine
- **Rule-based + ML hybrid** approach
- Factors: symptom severity, patient age, vital signs, pre-existing conditions
- Output: Risk level (Low / Medium / High / Critical)

### Recommendation Engine
- Maps predicted diseases to evidence-based treatment protocols
- Generates personalised suggestions including medications, lifestyle changes, and specialist referrals

---

## 🖼️ Screenshots

| Login Page | Dashboard |
|------------|-----------|
| Animated pill mascot with secure login form | Modern sidebar navigation with overview cards |

| Patient Assessment | Analytics |
|-------------------|-----------|
| Multi-step symptom questionnaire | Interactive charts and trend visualisations |

---

## 🔮 Future Scope

- 🌐 **Cloud Deployment** — Deploy to AWS/GCP/Azure for remote access
- 📱 **Mobile App** — React Native version for on-the-go access
- 🧬 **Advanced ML Models** — Deep learning models trained on larger medical datasets
- 🏥 **EHR Integration** — Connect with Electronic Health Record systems
- 🗣️ **Voice Input** — Allow doctors to describe symptoms via speech
- 📧 **Email Alerts** — Automated notifications for high-risk patients

---

## 👥 Contributors

| Name | Role | Branch |
|------|------|--------|
| **V. Swetha** | Developer | `V-Swetha` |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for Infosys Springboard Internship
</p>
