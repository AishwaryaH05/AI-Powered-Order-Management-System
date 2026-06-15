import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal
from backend.models import Order, Inventory
from backend.crud import create_order, get_orders, update_order_status
from backend.sla_service import predict_sla_breach
from backend.ai_service import inventory_recommendation
from backend.schemas import OrderCreate

def run_tests():
    db = SessionLocal()
    try:
        # Seed test inventory if needed, reset quantity to 10
        inv = db.query(Inventory).filter(
            Inventory.lens_type == "Progressive",
            Inventory.coating == "Anti-Reflective",
            Inventory.lens_index == "1.67",
            Inventory.power == "-2.00"
        ).first()
        if not inv:
            inv = Inventory(
                lens_type="Progressive",
                power="-2.00",
                quantity=10,
                coating="Anti-Reflective",
                lens_index="1.67"
            )
            db.add(inv)
        else:
            inv.quantity = 10
        db.commit()
        db.refresh(inv)
        print(f"Test inventory item seeded/reset successfully. Initial quantity: {inv.quantity}")

        # Test GAP 6: Create order matching coating + index
        # 1. Order matching exactly
        order_payload = OrderCreate(
            customer_name="Test Customer Direct",
            store_location="New York",
            lens_type="Progressive",
            lens_index="1.67",
            coating="Anti-Reflective",
            frame="Classic Black",
            left_power="-2.00",
            right_power="-2.00",
            sla_days=5
        )
        new_order = create_order(db, order_payload)
        print(f"Created order: {new_order.id}, inventory_available={new_order.inventory_available}")
        assert new_order.inventory_available is True, "Inventory should be available for matching specs"

        # Verify stock decrement (from 10 to 8 because identical left/right powers require 2 lenses)
        db.refresh(inv)
        print(f"Quantity after order: {inv.quantity}")
        assert inv.quantity == 8, f"Expected quantity to be 8, got {inv.quantity}"

        # 2. Order NOT matching specs (different coating)
        mismatch_payload = OrderCreate(
            customer_name="Test Customer Mismatch",
            store_location="New York",
            lens_type="Progressive",
            lens_index="1.67",
            coating="Blue Cut Mismatch",
            frame="Classic Black",
            left_power="-2.00",
            right_power="-2.00",
            sla_days=5
        )
        mismatch_order = create_order(db, mismatch_payload)
        assert mismatch_order.inventory_available is False, "Inventory should NOT be available for mismatched specs"
        # Verify no decrement occurred for failed check
        db.refresh(inv)
        assert inv.quantity == 8, f"Expected quantity to remain 8, got {inv.quantity}"
        print("GAP 6 (Inventory tracks coating + index & decrements correctly) verified successfully.")

        # Test GAP 2: Filters on get_orders
        all_nyc_progressive = get_orders(db, lens_type="Progressive", store_location="New York")
        assert len(all_nyc_progressive) >= 1
        for o in all_nyc_progressive:
            assert o.lens_type == "Progressive"
            assert o.store_location == "New York"
        print("GAP 2 (Dashboard filters) verified successfully.")

        # Test GAP 4: Dynamic SLA Prediction & Alerts
        sla_pred = predict_sla_breach(new_order)
        print(f"SLA Prediction details: {sla_pred}")
        assert "elapsed_days" in sla_pred
        assert "remaining_days" in sla_pred
        assert "adjusted_remaining" in sla_pred
        # It should trigger alerts and output status SAFE because elapsed days is 0 and remaining is 5.
        print("GAP 4 (Dynamic SLA prediction logic) verified successfully.")

        # Test simulated alert triggering on MONITOR
        monitor_order_payload = OrderCreate(
            customer_name="Test Alert Customer",
            store_location="New York",
            lens_type="Progressive",
            lens_index="1.67",
            coating="Anti-Reflective",
            frame="Classic Black",
            left_power="-2.00",
            right_power="-2.00",
            sla_days=1  # Remaining days = 1 -> MONITOR risk
        )
        monitor_order = create_order(db, monitor_order_payload)
        monitor_pred = predict_sla_breach(monitor_order)
        print(f"Monitor order prediction details: {monitor_pred}")
        assert monitor_pred["sla_risk"] == "MONITOR", f"Expected MONITOR risk, got {monitor_pred['sla_risk']}"
        
        # Verify that whatsapp_alerts.log file exists and contains the alert
        assert os.path.exists("whatsapp_alerts.log"), "WhatsApp alerts log file should have been created!"
        with open("whatsapp_alerts.log", "r", encoding="utf-8") as f:
            logs = f.read()
            assert "Test Alert Customer" in logs, "Simulated WhatsApp alert details should be written to logs"
        print("SLA Warning alerts (WhatsApp simulated log) verified successfully.")

        # Test GAP 1 & 3: update_order_status + QC_FAILED re-order loop
        order_id = new_order.id
        updated_order = update_order_status(db, order_id, "QC_FAILED", "Scratched lenses")
        assert updated_order.status == "QC_FAILED"
        assert updated_order.delay_reason == "Scratched lenses"

        # Verify parent-child relationship: there should be a new child order with ORDER_PLACED status
        orders_all = get_orders(db)
        child_order = None
        for o in orders_all:
            if o.parent_order_id == order_id:
                child_order = o
                break
        assert child_order is not None, "Child order should have been created"
        assert child_order.status == "ORDER_PLACED"
        assert child_order.customer_name == new_order.customer_name
        
        # Verify stock decrement for child order (from 10 to 4: 2 for main order, 2 for monitor order, 2 for child order)
        db.refresh(inv)
        print(f"Quantity after child order: {inv.quantity}")
        assert inv.quantity == 4, f"Expected quantity to be 4, got {inv.quantity}"
        
        print(f"Found child order spawned by QC_FAILED loop: {child_order.id}, parent={child_order.parent_order_id}")
        print("GAP 1 & 3 (Status updates, delay reason, and re-order loop with stock deduction) verified successfully.")

        print("--- ALL DIRECT BACKEND CRUD TESTS PASSED SUCCESSFULLY! ---")

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
