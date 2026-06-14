import streamlit as st
import requests
import pandas as pd

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="AI Order Management Dashboard",
    page_icon="🤖",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        135deg,
        #EEF2FF,
        #FFFFFF,
        #E0F2FE
    );
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.kpi-card{
    padding:20px;
    border-radius:18px;
    text-align:center;
    box-shadow:0px 8px 20px rgba(0,0,0,0.12);
    transition:0.3s;
}

.kpi-card:hover{
    transform:translateY(-5px);
}

</style>
""", unsafe_allow_html=True)

# =====================================
# GET DATA FROM FASTAPI
# =====================================

dashboard = requests.get(
    "http://127.0.0.1:8000/dashboard"
).json()

orders = requests.get(
    "http://127.0.0.1:8000/orders"
).json()

df = pd.DataFrame(orders)

predictions = requests.get(
    "http://127.0.0.1:8000/ai/predictions"
).json()

pred_df = pd.DataFrame(predictions)

inventory_recommendations = requests.get(
    "http://127.0.0.1:8000/ai/inventory-recommendations"
).json()

inventory_ai_df = pd.DataFrame(
    inventory_recommendations
)

sla_predictions = requests.get(
    "http://127.0.0.1:8000/ai/sla-predictions"
).json()

sla_df = pd.DataFrame(sla_predictions)

bottleneck = requests.get(
    "http://127.0.0.1:8000/ai/bottlenecks"
).json()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("🤖 AI OMS")

st.sidebar.success("🟢 System Online")

st.sidebar.markdown("---")

st.sidebar.metric(
    "Total Orders",
    dashboard["total_orders"]
)

st.sidebar.metric(
    "Inventory Matches",
    dashboard["inventory_available_orders"]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "FastAPI + PostgreSQL + Streamlit"
)

# =====================================
# HEADER
# =====================================

st.markdown("""
<h1 style='text-align:center;
color:#1E40AF;
font-size:60px;'>
🤖 AI Order Management Dashboard
</h1>

<h3 style='text-align:center;
color:gray;'>
Real-Time Order Tracking • Inventory Intelligence • AI Predictions
</h3>

<hr>
""", unsafe_allow_html=True)

# =====================================
# KPI CARDS
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card"
             style="background:#DBEAFE;">
            <h4>📦 Total Orders</h4>
            <h1>{dashboard['total_orders']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card"
             style="background:#FEF3C7;">
            <h4>⚙️ Active Orders</h4>
            <h1>{dashboard['active_orders']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card"
             style="background:#DCFCE7;">
            <h4>🚚 Delivered Orders</h4>
            <h1>{dashboard['delivered_orders']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card"
             style="background:#E0E7FF;">
            <h4>✅ Inventory Available</h4>
            <h1>{dashboard['inventory_available_orders']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================
# AI STATUS
# =====================================

st.success("🟢 AI Engine Active")

if st.button("🔄 Refresh Dashboard"):
    st.rerun()

# =====================================
# SEARCH + FILTERS
# =====================================

st.markdown("## 🔍 Search & Filters")

search_customer = st.text_input(
    "Search Customer"
)

if search_customer:
    df = df[
        df["customer_name"].str.contains(
            search_customer,
            case=False,
            na=False
        )
    ]

status_filter = st.selectbox(
    "Filter by Status",
    [
        "All",
        "ORDER_PLACED",
        "LENS_CUTTING",
        "DELIVERED"
    ]
)

if status_filter != "All":
    df = df[
        df["status"] == status_filter
    ]

# =====================================
# STATUS SUMMARY
# =====================================

st.markdown("### 📈 Order Summary")

placed_count = len(
    df[df["status"] == "ORDER_PLACED"]
)

cutting_count = len(
    df[df["status"] == "LENS_CUTTING"]
)

delivered_count = len(
    df[df["status"] == "DELIVERED"]
)

s1, s2, s3 = st.columns(3)

with s1:
    st.info(
        f"📦 ORDER_PLACED : {placed_count}"
    )

with s2:
    st.warning(
        f"✂️ LENS_CUTTING : {cutting_count}"
    )

with s3:
    st.success(
        f"🚚 DELIVERED : {delivered_count}"
    )

# =====================================
# TABLE COLORING
# =====================================

def color_status(val):

    if val == "ORDER_PLACED":
        return "background-color:#BFDBFE"

    elif val == "LENS_CUTTING":
        return "background-color:#FBBF24"

    elif val == "DELIVERED":
        return "background-color:#86EFAC"

    return ""

# =====================================
# ORDERS TABLE
# =====================================

st.markdown("## 📋 Orders")

display_df = df[
    [
        "id",
        "customer_name",
        "store_location",
        "lens_type",
        "status",
        "inventory_available",
        "sla_days"
    ]
]

styled_df = display_df.style.map(
    color_status,
    subset=["status"]
)

st.dataframe(
    styled_df,
    use_container_width=True
)

# =====================================
# STATUS DISTRIBUTION
# =====================================

st.markdown("## 📊 Order Status Distribution")

status_counts = df["status"].value_counts()

st.bar_chart(status_counts)

# =====================================
# AI INSIGHTS
# =====================================

st.markdown("## 🤖 AI Insights")

priority_orders = requests.get(
    "http://127.0.0.1:8000/ai/priorities"
).json()

priority_df = pd.DataFrame(priority_orders)

st.markdown("### 🚨 Priority Orders")

st.dataframe(
    priority_df,
    use_container_width=True
)


# =====================================
# ML DELAY PREDICTIONS
# =====================================

st.markdown("### 🧠 Machine Learning Predictions")

def color_prediction(val):

    if val == "HIGH":
        return "background-color:#FECACA"

    elif val == "MEDIUM":
        return "background-color:#FEF3C7"

    elif val == "LOW":
        return "background-color:#BBF7D0"

    return ""

styled_pred_df = pred_df.style.map(
    color_prediction,
    subset=["predicted_risk"]
)

st.dataframe(
    styled_pred_df,
    use_container_width=True
)

high_count = len(
    pred_df[
        pred_df["predicted_risk"] == "HIGH"
    ]
)

medium_count = len(
    pred_df[
        pred_df["predicted_risk"] == "MEDIUM"
    ]
)

low_count = len(
    pred_df[
        pred_df["predicted_risk"] == "LOW"
    ]
)

m1, m2, m3 = st.columns(3)

with m1:
    st.error(
        f"🔴 High Risk Predictions : {high_count}"
    )

with m2:
    st.warning(
        f"🟡 Medium Risk Predictions : {medium_count}"
    )

with m3:
    st.success(
        f"🟢 Low Risk Predictions : {low_count}"
    )
    
st.success("""
AI Modules Enabled

✓ ML Delay Prediction
✓ SLA Breach Detection
✓ Inventory Intelligence
✓ Bottleneck Analysis
""")

# =====================================
# AI OPERATIONAL INSIGHTS
# =====================================

st.markdown("## 🧠 AI Operational Insights")

st.error(
    f"⚠ Bottleneck Stage: {bottleneck['bottleneck_stage']}"
)

st.info(
    f"{bottleneck['orders']} out of {dashboard['total_orders']} orders are waiting in {bottleneck['bottleneck_stage']}"
)

st.success(
    f"Recommendation: {bottleneck['recommendation']}"
)

# =====================================
# INVENTORY INTELLIGENCE
# =====================================

st.markdown("## 📦 AI Inventory Intelligence")

if len(inventory_ai_df) > 0:

    st.warning(
        f"⚠️ {len(inventory_ai_df)} inventory items require attention"
    )

    st.dataframe(
        inventory_ai_df,
        use_container_width=True
    )

else:

    st.success(
        "✅ Inventory levels are healthy"
    )
# =====================================
# SLA BREACH PREDICTIONS
# =====================================

st.markdown("## ⏰ SLA Breach Predictions")

st.dataframe(
    sla_df,
    use_container_width=True
)

breach_count = len(
    sla_df[sla_df["sla_risk"] == "BREACH_RISK"]
)

monitor_count = len(
    sla_df[sla_df["sla_risk"] == "MONITOR"]
)

safe_count = len(
    sla_df[sla_df["sla_risk"] == "SAFE"]
)

c1, c2, c3 = st.columns(3)

with c1:
    st.error(
        f"🚨 Breach Risk : {breach_count}"
    )

with c2:
    st.warning(
        f"⚠️ Monitor : {monitor_count}"
    )

with c3:
    st.success(
        f"✅ Safe : {safe_count}"
    )