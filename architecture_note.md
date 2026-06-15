# 1-Page Architecture Note: AI-Powered Eyewear Order Management System

This document outlines the architecture, data flows, and prediction engines of the Eyewear Order Management System (OMS).

---

## 🏛️ System Architecture Overview

The system follows a three-tier decoupled architecture designed for clean separation of concerns and high maintainability:

```text
  [ Operations Team ]  <───>  [ Streamlit Frontend ]  <── (Presentation Layer)
                                       │
                                       ▼ (HTTP API Requests)
                              [ FastAPI Backend ]     <── (Application Service Layer)
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             [ Database ]      [ SLA Predictor ]   [ Machine Learning ]  <─ (Storage & Analytics)
```

1.  **Presentation Layer (Streamlit Frontend)**: A web dashboard where operations teams submit new orders, filter listings by status/store, change fulfillment stages, and monitor live alerts.
2.  **Application Service Layer (FastAPI Backend)**: A RESTful API server that processes incoming requests, enforces inventory allocation rules, runs machine learning models, and coordinates alerting.
3.  **Database Persistence Layer (PostgreSQL Database)**: Stores all persistent records across three tables: `orders` (fulfillment metadata), `inventory` (raw lens stock counts), and `order_history` (audit logs).

---

## 🧠 Core Predictive & Algorithmic Modules

The system integrates two prediction services to optimize fulfillment flows:

### 1. Delay Risk Classifier (Machine Learning)
*   **Purpose**: Classifies whether an active order is at **HIGH**, **MEDIUM**, or **LOW** risk of being delayed.
*   **Methodology**: Uses a Scikit-Learn **Random Forest Classifier** model. The model was trained on historical orders to identify risk patterns based on three input features:
    1.  `inventory_available` (0 or 1)
    2.  `status` (current manufacturing stage)
    3.  `sla_days` (total promised lead time)

### 2. SLA Breach Predictor & Alerting Engine
*   **Purpose**: Calculates remaining fulfillment time and dispatches warnings **before** a breach happens.
*   **Methodology**: To handle operational edge cases, the engine applies stage-specific risk multipliers based on manufacturing bottlenecks:
    *   `ORDER_PLACED` (1.0x multiplier)
    *   `LENS_CUTTING` (1.3x multiplier - high delay potential)
    *   `QUALITY_CHECK` (1.5x multiplier - precision bottleneck)
    *   `QC_FAILED` (2.0x multiplier - loop back re-order penalty)
    *   `DISPATCHED` (0.8x multiplier)
*   **Calculation**: $\text{Remaining Adjusted Days} = \frac{\text{SLA Days} - \text{Elapsed Days}}{\text{Stage Multiplier}}$
    *   If Adjusted Days is $\le 1.0$, the order enters **`MONITOR`** status, which immediately triggers the notification pipeline.

---

## 📦 Fulfillment Safeguards & Alerts

### 1. Multi-Power Inventory Verification
During order creation or re-order loops:
*   Queries stock availability for **both** left (OS) and right (OD) prescription powers.
*   Enforces quantity thresholds ($\ge 2$ units for identical left/right powers, $\ge 1$ unit per power for distinct powers).
*   Decrements the matching database stock counts upon confirmation.

### 2. Multi-Channel Alert Dispatch
When an order is flagged with a `MONITOR` or `BREACH` SLA status, the backend dispatches notifications through two channels:
*   **SMTP Email**: Emails warning alerts directly to the operations team inbox.
*   **WhatsApp**: Appends formatted simulated message alerts to `whatsapp_alerts.log` (displayed live on the dashboard).
