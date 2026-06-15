# AI-Powered Order Management System

## Overview

The AI-Powered Order Management System is a full-stack application designed for eyewear order processing. It manages the complete order lifecycle, from order creation to delivery, while providing AI-driven insights for operations teams.

The system combines FastAPI, PostgreSQL, Streamlit, and Machine Learning to automate order tracking, inventory verification, risk prediction, SLA monitoring, and operational analytics.

---

## Business Problem Solved

Eyewear orders are more complex than standard e-commerce orders. Each order contains prescription details, lens configurations, coatings, frames, inventory dependencies, and SLA commitments.

Delays can occur due to:

* Inventory shortages
* Production bottlenecks
* Manufacturing delays
* SLA breaches

This system provides operational visibility through AI-powered monitoring, helping teams prioritize orders, predict risks, manage inventory, and improve fulfillment efficiency.

---

## Key Features

### Order Management

* Create eyewear orders using the dashboard intake form
* Update order status and log delay reasons
* Track complete order lifecycle (including custom stages: `QUALITY_CHECK`, `QC_FAILED`, `DISPATCHED`)
* Automatically trigger a re-order loop (child order spawned under `ORDER_PLACED` and linked via `parent_order_id` when parent is set to `QC_FAILED`)
* Store prescription details (Left OS / Right OD powers)
* Monitor fulfillment progress

### Inventory Management

* Inventory verification matching lens specifications: lens type, coating, thickness index, and power
* Validates stock for **both** left and right powers ($\ge 2$ units for identical left/right powers, $\ge 1$ unit per power for distinct powers)
* Real-time inventory availability tracking and stock depletion on order creation and child re-orders
* Low stock identification aggregated by specifications (lens type + coating + lens index combinations)
* Inventory intelligence recommendations

### AI & Machine Learning

* Random Forest-based delay prediction with runtime fallback protection for new stages
* Order prioritization engine
* Dynamic SLA breach prediction calculating elapsed days, remaining days, and stage-specific risk multipliers
* Real-time SMTP email and simulated WhatsApp warning notifications dispatched to the operational team **before** a breach occurs (on `MONITOR` or `BREACH` risk)
* Bottleneck analysis
* Operational insights dashboard

### Dashboard

* Real-time KPIs
* 📝 New Eyewear Order Intake Form to submit orders and see real-time in-house stock availability
* Interactive order table displaying parent/child order linkages, delay reasons, SLA remaining days, and risk levels
* Interactive row-by-row status and delay reason update forms
* Multi-dimensional filtering (filter by status, lens type, and store location)
* Status distribution charts
* ML prediction monitoring
* Inventory intelligence view
* SLA monitoring dashboard with a live simulated WhatsApp alerts log feed

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

### Frontend

* Streamlit

### Machine Learning

* Scikit-Learn
* Random Forest Classifier
* Pandas
* Joblib

### Database

* PostgreSQL

---

## System Architecture

```text
User
  │
  ▼
Streamlit Dashboard
  │
  ▼
FastAPI APIs
  │
  ▼
PostgreSQL Database
  │
  ▼
AI Services
  │
  ▼
Random Forest Model
```

---

## Project Structure

```text
AI_ORDER_MANAGEMENT/
│
├── backend/
│   │
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   │
│   ├── ai_service.py
│   ├── ml_predictor.py
│   ├── priority_service.py
│   ├── sla_service.py
│   ├── alert_service.py
│   ├── bottleneck_service.py
│   │
│   └── ml/
│       ├── generate_dataset.py
│       ├── train_model.py
│       ├── orders_training.csv
│       ├── model.pkl
│       ├── status_encoder.pkl
│       └── risk_encoder.pkl
│
├── frontend/
│   └── app.py
│
├── screenshots/
│   ├── image1.png
│   ├── image2.png
│   ├── image3.png
│   ├── image4.png
│   ├── image5.png
│   ├── image6.png
│   ├── image7.png
│   └── image8.png
│
├── scratch/
│   └── test_endpoints.py
│
├── requirements.txt
├── README.md
├── architecture_note.md
│
└── venv/
```
---

## Dashboard Screenshots

### Main Dashboard Header & Intake Form

![Main Dashboard Header](screenshots/image1.png)

Shows:

* Total Orders, Active Orders, Delivered Orders, and Inventory Available counts
* Real-Time order status status banner
* Expandable Eyewear Order Intake Form with automated default SLA values

---

### Filters & Main Orders Grid

![Main Orders Grid](screenshots/image2.png)

Shows:

* Customer Search and Filters by status, lens type, and store location
* Order Summary metrics
* Complete Orders grid displaying prescription details, remaining SLA days, and risk levels

---

### Update Status & Delay Reasons

![Update Panels](screenshots/image3.png)

Features:

* Direct drop-downs to change the lifecycle status of any active order
* Inline text input fields to record delay reasons (e.g. for re-orders)

---

### Order Status Distribution

![Order Analytics](screenshots/image4.png)

Provides a visual breakdown of order volumes across status categories.

---

### AI Insights & ML Predictions

#### Priority Orders

![Priority Orders](screenshots/image5.png)

Shows AI priority recommendations based on stock availability and production statuses.

#### Machine Learning Predictions

![ML Predictions](screenshots/image6.png)

Machine Learning model predicts delay risks (High/Medium/Low) using Random Forest features.

---

### AI Operational Insights & Inventory Low Stock Warnings

![Operational & Inventory Insights](screenshots/image7.png)

Identifies operational bottlenecks and lists inventory items requiring replenishment.

---

### SLA Monitoring & Simulated WhatsApp Alert Logs

![SLA Monitoring & WhatsApp Alert Logs](screenshots/image8.png)

Detects orders that:

* Are within SLA or approaching breach (`MONITOR`)
* Displays live simulated WhatsApp alerts dispatched to operations teams


## AI Features

### Delay Prediction

Predicts whether an order is at:

* HIGH Risk
* MEDIUM Risk
* LOW Risk

using a Random Forest machine learning model.

Features used:

* Inventory Availability
* Order Status
* SLA Days

---

### Inventory Intelligence

Identifies inventory shortages and recommends replenishment actions.

Example:

```text
Progressive Lens (-4.0)
Current Stock: 3
Recommendation: Reorder Soon
```

---

### SLA Monitoring

Detects orders at risk of breaching SLA commitments by calculating elapsed days, remaining days, and applying stage-based risk multipliers:
* `ORDER_PLACED`: 1.0x
* `LENS_CUTTING`: 1.3x
* `QUALITY_CHECK`: 1.5x
* `QC_FAILED`: 2.0x
* `DISPATCHED`: 0.8x

Outputs:
* **SAFE**: Within standard commitment window.
* **MONITOR** (Likely to breach): Dispatches **pre-breach alerts** (SMTP email + simulated WhatsApp logs) to notify the operations team *before* a breach happens.
* **BREACH** (SLA has been violated): Dispatches urgent breach alerts (SMTP email + simulated WhatsApp logs).

---

### Bottleneck Analysis

Identifies workflow stages where orders are accumulating.

Example:

```text
6 out of 7 orders are waiting in ORDER_PLACED
```

Recommendation:

```text
Prioritize order processing and inventory allocation.
```

---

### Priority Engine

Automatically highlights orders requiring immediate operational attention.

Priority Levels:

* HIGH
* MEDIUM
* LOW

---

## Machine Learning Pipeline

### Dataset

* 5000 Synthetic Training Records

### Model

* Random Forest Classifier

### Workflow

```text
Dataset Generation
        │
        ▼
Model Training
        │
        ▼
Model Serialization (model.pkl)
        │
        ▼
FastAPI Prediction API
        │
        ▼
Streamlit Dashboard
```

---

## Installation & Setup

### Clone Repository

```bash
git clone <repository-url>
cd ai_order_management
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start FastAPI Server

```bash
uvicorn backend.main:app --reload
```

FastAPI Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit Dashboard

```bash
streamlit run frontend/app.py
```

Dashboard URL:

```text
http://localhost:8501
```

---


## API Endpoints

### Order APIs

```http
POST /orders
```

Create a new order. Matches both left and right lens powers against inhouse stock (ensuring quantity >= 2 for identical powers and quantity >= 1 for distinct powers) and depletes stock.

```http
GET /orders
```

Retrieve orders. Supports query parameters `status`, `lens_type`, and `store_location` to dynamically filter search results.

```http
PUT /orders/{id}/status
```

Update order status.

```http
PATCH /orders/{id}/status
```

Surgically update order status and log a delay reason. Spawns child re-order loop if updated to `QC_FAILED`.

```http
PUT /orders/{id}/inventory
```

Update inventory availability.

---

### Dashboard APIs

```http
GET /dashboard
```

Retrieve dashboard KPIs.

---

### AI APIs

```http
GET /ai/predictions
```

Machine Learning risk predictions.

```http
GET /ai/priorities
```

Priority order recommendations.

```http
GET /ai/inventory-recommendations
```

Inventory intelligence insights.

```http
GET /ai/sla-predictions
```

SLA monitoring results.

```http
GET /ai/bottlenecks
```

Operational bottleneck analysis.

---

## Future Enhancements

### Advanced Machine Learning

- XGBoost-based Delay Prediction Model
- Model Performance Comparison (Random Forest vs XGBoost)
- Automated Hyperparameter Tuning
- Demand Forecasting using Time Series Models

### Generative AI Features

- GenAI-powered Order Support Assistant
- RAG (Retrieval-Augmented Generation) Chatbot for Order Queries
- Natural Language Search for Orders and Inventory
- AI-generated Operational Summaries

### Vector Database Integration

- Store Order Knowledge Base using Vector Embeddings
- Semantic Search across Orders, Inventory, and SOP Documents
- Integration with ChromaDB, Pinecone, or FAISS
- Similar Order Retrieval using Embedding Search

### Operations & Analytics

- Real-Time Notifications
- Advanced SLA Forecasting
- Production Scheduling Optimization
- Inventory Demand Prediction

### Platform Enhancements

- Docker Deployment
- User Authentication & Role-Based Access
- Cloud Deployment (AWS/GCP/Azure)
- CI/CD Pipeline Integration

## Author

**Aishwarya Hosurmath**
