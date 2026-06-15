import streamlit as st
import requests
import pandas as pd
import os

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
# GET DATA FROM FASTAPI (INITIAL RETRIEVAL FOR FILTERS)
# =====================================

dashboard = requests.get(
    "http://127.0.0.1:8000/dashboard"
).json()

try:
    all_orders = requests.get("http://127.0.0.1:8000/orders").json()
    all_df = pd.DataFrame(all_orders)
except Exception:
    all_df = pd.DataFrame()

if not all_df.empty:
    unique_lens_types = ["All"] + sorted(list(all_df["lens_type"].dropna().unique()))
    unique_locations = ["All"] + sorted(list(all_df["store_location"].dropna().unique()))
else:
    unique_lens_types = ["All"]
    unique_locations = ["All"]

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
# ORDER INTAKE FORM (NEW)
# =====================================

if "intake_msg" in st.session_state:
    msg = st.session_state["intake_msg"]
    if "⚠️" in msg:
        st.warning(msg)
    else:
        st.success(msg)
    del st.session_state["intake_msg"]

with st.expander("📝 New Eyewear Order Intake Form", expanded=False):
    with st.form("intake_form", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            customer_name = st.text_input("Customer Name", placeholder="e.g. John Doe")
            store_location = st.text_input("Store Location", placeholder="e.g. Bangalore, Karnataka, New York")
            frame = st.text_input("Frame Model", placeholder="e.g. Classic Black Aviator")
        with col_c2:
            lens_type = st.selectbox("Lens Type", ["Single Vision", "Progressive", "Bifocal"])
            lens_index = st.selectbox("Lens Index (Thickness)", ["1.50", "1.56", "1.60", "1.67", "1.74"])
            coating = st.selectbox("Coating", ["Anti-Reflective", "Blue Cut", "Photochromic", "None"])
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            left_power = st.text_input("Left Power (OS)", value="-0.00")
        with col_p2:
            right_power = st.text_input("Right Power (OD)", value="-0.00")
        with col_p3:
            # Populating default SLA days depending on type:
            default_sla = 3
            if lens_type == "Bifocal":
                default_sla = 4
            elif lens_type == "Progressive":
                default_sla = 5
            sla_days = st.number_input("SLA Commitment (Days)", min_value=1, max_value=30, value=default_sla)

        submitted = st.form_submit_button("Submit Order Intake")
        if submitted:
            if not customer_name.strip():
                st.error("Customer Name is required!")
            elif not store_location.strip():
                st.error("Store Location is required!")
            else:
                payload = {
                    "customer_name": customer_name,
                    "store_location": store_location,
                    "lens_type": lens_type,
                    "lens_index": lens_index,
                    "coating": coating,
                    "frame": frame,
                    "left_power": left_power,
                    "right_power": right_power,
                    "sla_days": int(sla_days)
                }
                try:
                    resp = requests.post("http://127.0.0.1:8000/orders", json=payload)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        inv_msg = "✅ Lenses are in-house! Order scheduled for immediate cutting." if res_data.get("inventory_available") else "⚠️ Lenses NOT in-house! Scheduled for replenishment."
                        st.session_state["intake_msg"] = f"Order #{res_data.get('id')} placed successfully! {inv_msg}"
                        st.rerun()
                    else:
                        st.error(f"Error submitting order: {resp.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

# =====================================
# SEARCH + FILTERS
# =====================================

st.markdown("## 🔍 Search & Filters")

search_customer = st.text_input(
    "Search Customer"
)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    status_filter = st.selectbox(
        "Filter by Status",
        [
            "All",
            "ORDER_PLACED",
            "LENS_CUTTING",
            "QUALITY_CHECK",
            "QC_FAILED",
            "DELIVERED",
            "DISPATCHED"
        ]
    )
with col_f2:
    lens_type_filter = st.selectbox(
        "Filter by Lens Type",
        unique_lens_types
    )
with col_f3:
    store_location_filter = st.selectbox(
        "Filter by Store Location",
        unique_locations
    )

# Prepare API query params based on filters
query_params = {}
if status_filter != "All":
    query_params["status"] = status_filter
if lens_type_filter != "All":
    query_params["lens_type"] = lens_type_filter
if store_location_filter != "All":
    query_params["store_location"] = store_location_filter

# Fetch filtered order data from API
orders = requests.get(
    "http://127.0.0.1:8000/orders",
    params=query_params
).json()
df = pd.DataFrame(orders)
if df.empty:
    df = pd.DataFrame(columns=[
        "id", "customer_name", "store_location", "lens_type", "status", 
        "inventory_available", "sla_days", "parent_order_id", "delay_reason",
        "remaining_days", "sla_risk"
    ])

# Apply client-side text search filter if provided
if search_customer and not df.empty:
    df = df[
        df["customer_name"].str.contains(
            search_customer,
            case=False,
            na=False
        )
    ]

# Fetch remaining API data and filter in-memory where applicable
predictions = requests.get("http://127.0.0.1:8000/ai/predictions").json()
pred_df = pd.DataFrame(predictions)
if pred_df.empty:
    pred_df = pd.DataFrame(columns=["order_id", "customer_name", "status", "predicted_risk"])
if not df.empty and not pred_df.empty:
    pred_df = pred_df[pred_df["order_id"].isin(df["id"])]

inventory_recommendations = requests.get("http://127.0.0.1:8000/ai/inventory-recommendations").json()
inventory_ai_df = pd.DataFrame(inventory_recommendations)

sla_predictions = requests.get("http://127.0.0.1:8000/ai/sla-predictions").json()
sla_df = pd.DataFrame(sla_predictions)
if sla_df.empty:
    sla_df = pd.DataFrame(columns=["order_id", "customer_name", "status", "sla_days", "sla_risk", "message", "elapsed_days", "remaining_days", "adjusted_remaining"])
if not df.empty and not sla_df.empty:
    sla_df = sla_df[sla_df["order_id"].isin(df["id"])]

# Merge SLA predictions directly into the main orders dataframe for comprehensive view
if not df.empty and not sla_df.empty:
    df = pd.merge(
        df,
        sla_df[["order_id", "remaining_days", "adjusted_remaining", "sla_risk"]],
        left_on="id",
        right_on="order_id",
        how="left"
    )
    # Fill defaults for display
    df["sla_risk"] = df["sla_risk"].fillna("SAFE")
    df["remaining_days"] = df["remaining_days"].fillna(df["sla_days"])

bottleneck = requests.get("http://127.0.0.1:8000/ai/bottlenecks").json()

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
        return "background-color:#FDE047"
    elif val == "QUALITY_CHECK":
        return "background-color:#C084FC"
    elif val == "QC_FAILED":
        return "background-color:#FCA5A5"
    elif val == "DELIVERED":
        return "background-color:#86EFAC"
    elif val == "DISPATCHED":
        return "background-color:#6EE7B7"
    return ""

def color_sla_risk(val):
    if val == "BREACH":
        return "background-color:#FCA5A5; color:#7F1D1D; font-weight:bold"
    elif val == "MONITOR":
        return "background-color:#FEF08A; color:#713F12; font-weight:bold"
    elif val == "SAFE":
        return "background-color:#BBF7D0; color:#14532D"
    return ""

# =====================================
# ORDERS TABLE
# =====================================

st.markdown("## 📋 Orders")

columns_to_show = ["id", "customer_name", "store_location", "lens_type", "status", "inventory_available", "sla_days"]
if not df.empty:
    if "remaining_days" in df.columns:
        columns_to_show.append("remaining_days")
    if "sla_risk" in df.columns:
        columns_to_show.append("sla_risk")
    if "parent_order_id" in df.columns:
        columns_to_show.append("parent_order_id")
    if "delay_reason" in df.columns:
        columns_to_show.append("delay_reason")

display_df = df[columns_to_show] if not df.empty else pd.DataFrame(columns=columns_to_show)

styled_df = display_df.style.map(
    color_status,
    subset=["status"]
)
if "sla_risk" in display_df.columns:
    styled_df = styled_df.map(
        color_sla_risk,
        subset=["sla_risk"]
    )

st.dataframe(
    styled_df,
    width="stretch"
)

# =====================================
# INTERACTIVE ORDER ACTIONS (CONSOLIDATED)
# =====================================

st.markdown("### ✏️ Update Order Status & Delay Reason")
if not df.empty:
    active_rows = df[df["status"] != "DELIVERED"]
    if not active_rows.empty:
        # Create list of choices like "Order #3 - Abhijeet (Bangalore)"
        order_options = {}
        for _, r in active_rows.iterrows():
            label = f"Order #{r['id']} - {r['customer_name']} ({r['store_location']}) [Current: {r['status']}]"
            order_options[label] = r
            
        uc1, uc2, uc3, uc4 = st.columns([3, 2, 4, 1.5])
        with uc1:
            selected_label = st.selectbox("Select Order to Update", list(order_options.keys()))
        
        # Retrieve currently selected order details
        selected_order = order_options[selected_label]
        
        statuses = ["ORDER_PLACED", "LENS_CUTTING", "QUALITY_CHECK", "QC_FAILED", "DELIVERED", "DISPATCHED"]
        try:
            default_idx = statuses.index(selected_order["status"])
        except ValueError:
            default_idx = 0
            
        with uc2:
            new_status = st.selectbox("New Status", statuses, index=default_idx)
        with uc3:
            delay_val = selected_order.get("delay_reason", "") or ""
            if pd.isna(delay_val) or not delay_val:
                delay_val = ""
            reason = st.text_input("Delay Reason (optional)", value=delay_val, placeholder="e.g. Scratched lens")
            
        with uc4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # spacer
            submit_update = st.button("Update Order", width="stretch")
            
        if submit_update:
            payload = {
                "new_status": new_status,
                "delay_reason": reason if reason.strip() else None
            }
            resp = requests.patch(f"http://127.0.0.1:8000/orders/{selected_order['id']}/status", json=payload)
            if resp.status_code == 200:
                st.toast(f"Order #{selected_order['id']} updated successfully!")
                st.rerun()
            else:
                st.error(f"Failed to update Order #{selected_order['id']}: {resp.text}")
    else:
        st.info("No active orders available to update.")
else:
    st.info("No active orders to update.")

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
    width="stretch"
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
    width="stretch"
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
        width="stretch"
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
    width="stretch"
)

breach_count = len(
    sla_df[sla_df["sla_risk"] == "BREACH"]
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
        f"🚨 Breach : {breach_count}"
    )

with c2:
    st.warning(
        f"⚠️ Monitor : {monitor_count}"
    )

with c3:
    st.success(
        f"✅ Safe : {safe_count}"
    )

# =====================================
# WHATSAPP ALERT LOGS (NEW)
# =====================================
st.markdown("---")
st.markdown("## 💬 Simulated WhatsApp Alert Logs")
whatsapp_log_file = "whatsapp_alerts.log"
try:
    if os.path.exists(whatsapp_log_file):
        with open(whatsapp_log_file, "r", encoding="utf-8") as f:
            logs = f.read()
        st.text_area("Live WhatsApp Alerts Dispatched", value=logs, height=250)
    else:
        st.info("No WhatsApp alerts dispatched yet.")
except Exception as e:
    st.error(f"Error reading WhatsApp logs: {e}")