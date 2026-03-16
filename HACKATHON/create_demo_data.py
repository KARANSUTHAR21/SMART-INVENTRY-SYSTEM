from app import app
from models import db, User, InventoryItem, Operation, StockMovement, UserSettings, Receipt, ReceiptItem
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create demo data for prototyping"""
    
    with app.app_context():
        print("Clearing existing demo data...")
        db.drop_all()
        db.create_all()
        
        print("Creating demo user...")
        demo_user = User(
            full_name="Demo Manager",
            email="demo@wareflow.com",
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()
        
        print("Creating user settings...")
        settings = UserSettings(
            user_id=demo_user.id,
            company_name="Demo Warehouse Inc.",
            low_stock_threshold=10,
            email_notifications=True,
            theme="light"
        )
        db.session.add(settings)
        
        print("Creating demo inventory items...")
        demo_items = [
            InventoryItem(
                name="Laptop Dell XPS 15",
                sku="LAP-001",
                quantity=15,
                price=1299.99 * 83, 
                category="Electronics",
                location="Warehouse A",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=25)
            ),
            InventoryItem(
                name="Office Chair Ergonomic",
                sku="CHR-002",
                quantity=8,
                price=349.99 * 83,
                category="Furniture",
                location="Warehouse B",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=20)
            ),
            InventoryItem(
                name="Wireless Mouse Logitech",
                sku="MOU-003",
                quantity=45,
                price=29.99 * 83,
                category="Electronics",
                location="Warehouse A",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=15)
            ),
            InventoryItem(
                name="Standing Desk 120cm",
                sku="DSK-004",
                quantity=5,
                price=599.99 * 83,
                category="Furniture",
                location="Warehouse C",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=10)
            ),
            InventoryItem(
                name="USB-C Hub 7-in-1",
                sku="HUB-005",
                quantity=32,
                price=49.99 * 83,
                category="Electronics",
                location="Warehouse A",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=5)
            ),
            InventoryItem(
                name="Monitor 27 inch 4K",
                sku="MON-006",
                quantity=12,
                price=449.99 * 83,
                category="Electronics",
                location="Warehouse B",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=2)
            )
        ]
        
        for item in demo_items:
            db.session.add(item)
        db.session.commit()
        
        print("Creating demo operations...")
        demo_operations = [
            Operation(
                operation_type="purchase",
                item_id=demo_items[0].id,
                quantity=10,
                reference="PO-2024-001",
                notes="Initial stock purchase from Dell supplier",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=24)
            ),
            Operation(
                operation_type="sale",
                item_id=demo_items[0].id,
                quantity=3,
                reference="SO-2024-015",
                notes="Sold to Tech Corp",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=18)
            ),
            Operation(
                operation_type="purchase",
                item_id=demo_items[1].id, 
                quantity=15,
                reference="PO-2024-002",
                notes="Bulk order from Office Furniture Co",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=19)
            ),
            Operation(
                operation_type="transfer",
                item_id=demo_items[2].id,
                quantity=20,
                reference="TRF-2024-003",
                notes="Moved from Warehouse A to B",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=12)
            ),
            Operation(
                operation_type="adjustment_in",
                item_id=demo_items[3].id, 
                quantity=2,
                reference="ADJ-2024-001",
                notes="Stock count adjustment - found missing items",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=8)
            ),
            Operation(
                operation_type="sale",
                item_id=demo_items[4].id,
                quantity=15,
                reference="SO-2024-028",
                notes="Bulk order to Startup Inc",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            Operation(
                operation_type="purchase",
                item_id=demo_items[5].id,
                quantity=25,
                reference="PO-2024-008",
                notes="New monitor stock for Q2",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=1)
            )
        ]
        
        for op in demo_operations:
            db.session.add(op)
        db.session.commit()
        
        print("Creating demo stock movements...")
        demo_movements = [
            StockMovement(
                item_id=demo_items[0].id,  
                movement_type="in",
                quantity=10,
                operation_id=demo_operations[0].id,
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=24)
            ),
            StockMovement(
                item_id=demo_items[0].id,  
                movement_type="out",
                quantity=3,
                operation_id=demo_operations[1].id,
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=18)
            ),
            StockMovement(
                item_id=demo_items[1].id,  
                movement_type="in",
                quantity=15,
                operation_id=demo_operations[2].id,
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=19)
            ),
            StockMovement(
                item_id=demo_items[2].id,  
                movement_type="transfer",
                quantity=20,
                from_location="Warehouse A",
                to_location="Warehouse B",
                operation_id=demo_operations[3].id,
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=12)
            )
        ]
        
        for movement in demo_movements:
            db.session.add(movement)
        db.session.commit()
        
        print("Creating demo receipts...")
        demo_receipts = [
            Receipt(
                from_entity="Azure Interior",
                to_location="WH/Stock1",
                contact="Azure Interior",
                schedule_date=datetime.utcnow().date() + timedelta(days=2),
                status="Ready",
                notes="Furniture order for office renovation",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=5)
            ),
            Receipt(
                from_entity="Tech Supplies Co",
                to_location="WH/Stock2",
                contact="Tech Supplies Co",
                schedule_date=datetime.utcnow().date() + timedelta(days=1),
                status="In Progress",
                notes="Electronic components delivery",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            Receipt(
                from_entity="Office Depot",
                to_location="WH/Stock3",
                contact="Office Depot",
                schedule_date=datetime.utcnow().date() - timedelta(days=1),
                status="Completed",
                notes="Stationery and office supplies",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=7)
            ),
            Receipt(
                from_entity="Furniture Plus",
                to_location="WH/Stock1",
                contact="Furniture Plus",
                schedule_date=datetime.utcnow().date() - timedelta(days=3),
                status="Cancelled",
                notes="Cancelled due to quality issues",
                user_id=demo_user.id,
                created_at=datetime.utcnow() - timedelta(days=10)
            )
        ]
        
        for receipt in demo_receipts:
            receipt.generate_reference()
            db.session.add(receipt)
        db.session.commit()
        
        print("Creating demo receipt items...")
        demo_receipt_items = [
            ReceiptItem(
                receipt_id=demo_receipts[0].id,
                item_id=demo_items[1].id,  
                quantity=5,
                unit_price=349.99 * 83,
                total_price=5 * (349.99 * 83),
                notes="Ergonomic office chairs"
            ),
            ReceiptItem(
                receipt_id=demo_receipts[0].id,
                item_id=demo_items[3].id, 
                quantity=3,
                unit_price=599.99 * 83,
                total_price=3 * (599.99 * 83),
                notes="Standing desks for renovation"
            ),
            
            ReceiptItem(
                receipt_id=demo_receipts[1].id,
                item_id=demo_items[0].id,  
                quantity=2,
                unit_price=1299.99 * 83,
                total_price=2 * (1299.99 * 83),
                notes="Dell laptops for new employees"
            ),
            ReceiptItem(
                receipt_id=demo_receipts[1].id,
                item_id=demo_items[5].id,  
                quantity=4,
                unit_price=449.99 * 83,
                total_price=4 * (449.99 * 83),
                notes="4K monitors"
            ),
            
            ReceiptItem(
                receipt_id=demo_receipts[2].id,
                item_id=demo_items[4].id,  
                quantity=10,
                unit_price=49.99 * 83,
                total_price=10 * (49.99 * 83),
                notes="USB-C hubs for office"
            ),
            ReceiptItem(
                receipt_id=demo_receipts[2].id,
                item_id=demo_items[2].id,  
                quantity=15,
                unit_price=29.99 * 83,
                total_price=15 * (29.99 * 83),
                notes="Wireless mice"
            )
        ]
        
        for item in demo_receipt_items:
            db.session.add(item)
        db.session.commit()
        
        print("\n✅ Demo data created successfully!")
        print("📧 Demo Login: demo@wareflow.com / demo123")
        print("📊 Dashboard Summary:")
        print(f"   • Total Items: {len(demo_items)}")
        print(f"   • Total Operations: {len(demo_operations)}")
        print(f"   • Total Stock Movements: {len(demo_movements)}")
        print(f"   • Total Receipts: {len(demo_receipts)}")
        print(f"   • Total Receipt Items: {len(demo_receipt_items)}")
        print(f"   • Low Stock Items: {sum(1 for item in demo_items if item.quantity < 10)}")

if __name__ == "__main__":
    create_demo_data()
