from datetime import datetime
from backend.alert_service import send_breach_alert, send_whatsapp_alert

def predict_sla_breach(order):
    # Calculate elapsed_days
    today = datetime.utcnow()
    # Handle if created_at is None
    created_at = order.created_at or today
    elapsed_days = (today - created_at).days

    # Calculate remaining_days
    remaining_days = order.sla_days - elapsed_days

    # Apply stage multipliers
    multipliers = {
        "ORDER_PLACED": 1.0,
        "LENS_CUTTING": 1.3,
        "QUALITY_CHECK": 1.5,
        "QC_FAILED": 2.0,
        "DISPATCHED": 0.8
    }
    stage_multiplier = multipliers.get(order.status, 1.0)

    # Calculate adjusted_remaining
    adjusted_remaining = remaining_days / stage_multiplier if stage_multiplier != 0 else remaining_days

    # Classify risk
    if adjusted_remaining <= 0:
        sla_risk = "BREACH"
        message = "SLA has been breached"
    elif adjusted_remaining <= 1:
        sla_risk = "MONITOR"
        message = "Monitor closely (Likely to breach)"
    else:
        sla_risk = "SAFE"
        message = "Within SLA"

    # Send alerts before breach (on MONITOR or BREACH status)
    if sla_risk in ["BREACH", "MONITOR"]:
        # Simulated WhatsApp Alert
        try:
            send_whatsapp_alert(order, risk_type=sla_risk)
        except Exception as e:
            print(f"Error sending simulated WhatsApp alert: {e}")

        # SMTP Email Alert
        try:
            send_breach_alert(order)
        except Exception as e:
            print(f"Email alert skipped/failed for Order #{order.id}: {e}")

    return {
        "sla_risk": sla_risk,
        "message": message,
        "elapsed_days": elapsed_days,
        "remaining_days": remaining_days,
        "adjusted_remaining": round(adjusted_remaining, 2)
    }