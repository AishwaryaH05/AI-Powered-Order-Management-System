import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_breach_alert(order):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    alert_to_email = os.environ.get("ALERT_TO_EMAIL")

    if not all([smtp_host, smtp_port, smtp_user, smtp_password, alert_to_email]):
        print("SLA Breach Alert skipped: Environment variables SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and ALERT_TO_EMAIL must be set.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = alert_to_email
        msg['Subject'] = f"ALERT: SLA Breach Warning for Order #{order.id}"

        body = f"""
        Dear Operations Team,

        Order ID #{order.id} is predicted to breach its SLA.

        Details:
        - Customer Name: {order.customer_name}
        - Store Location: {order.store_location}
        - Lens Type: {order.lens_type}
        - Coating: {order.coating}
        - Lens Index: {order.lens_index}
        - Current Status: {order.status}
        - SLA Days: {order.sla_days}

        Please process this order with high priority.

        Regards,
        AI OMS Engine
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect and send
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Breach alert email successfully sent for Order #{order.id} to {alert_to_email}")
    except Exception as e:
        # Re-raise exception so parent try/except in sla_service can catch it, or handle it cleanly
        raise e


def send_whatsapp_alert(order, risk_type="BREACH"):
    whatsapp_log_path = "whatsapp_alerts.log"
    try:
        with open(whatsapp_log_path, "a", encoding="utf-8") as f:
            f.write(f"--- WHATSAPP ALERT DISPATCHED ({risk_type.upper()}) ---\n")
            f.write(f"Recipient: Eyewear Operations Team\n")
            f.write(f"Message: SLA Alert for Order #{order.id}!\n")
            f.write(f"Customer: {order.customer_name}\n")
            f.write(f"Store Location: {order.store_location}\n")
            f.write(f"Lens specs: {order.lens_type} | Coating: {order.coating} | Index: {order.lens_index}\n")
            f.write(f"Status: {order.status}\n")
            f.write(f"SLA Days: {order.sla_days}\n")
            f.write(f"----------------------------------------------------\n\n")
        print(f"Simulated WhatsApp {risk_type} alert written to {whatsapp_log_path} for Order #{order.id}")
    except Exception as e:
        print(f"Error writing simulated WhatsApp alert: {e}")
