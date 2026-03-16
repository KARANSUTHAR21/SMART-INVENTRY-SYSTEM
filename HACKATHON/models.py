from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('inventory_items', lazy=True))
    
    def __repr__(self):
        return f'<InventoryItem {self.name}>'

class Operation(db.Model):
    __tablename__ = 'operations'
    
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'sale', 'transfer', 'adjustment'
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100))  # Invoice number, order ID, etc.
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('InventoryItem', backref=db.backref('operations', lazy=True))
    user = db.relationship('User', backref=db.backref('operations', lazy=True))
    
    def __repr__(self):
        return f'<Operation {self.operation_type}>'

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'in', 'out', 'transfer'
    quantity = db.Column(db.Integer, nullable=False)
    from_location = db.Column(db.String(100))
    to_location = db.Column(db.String(100))
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('InventoryItem', backref=db.backref('stock_movements', lazy=True))
    operation = db.relationship('Operation', backref=db.backref('stock_movements', lazy=True))
    user = db.relationship('User', backref=db.backref('stock_movements', lazy=True))
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type}>'

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(100))
    low_stock_threshold = db.Column(db.Integer, default=10)
    email_notifications = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(20), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('settings', uselist=False))
    
    def __repr__(self):
        return f'<UserSettings for user {self.user_id}>'

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)  # Format: WH/IN/001
    from_entity = db.Column(db.String(100), nullable=False)  # vendor name
    to_location = db.Column(db.String(100), nullable=False)  # warehouse location
    contact = db.Column(db.String(100), nullable=False)  # contact person/company
    schedule_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Ready')  # Ready, In Progress, Completed, Cancelled
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('receipts', lazy=True))
    items = db.relationship('ReceiptItem', backref='receipt', lazy=True, cascade='all, delete-orphan')
    
    def generate_reference(self, warehouse_id='WH'):
        """Generate reference number in format: WH/IN/001"""
        last_receipt = Receipt.query.filter(
            Receipt.reference.like(f'{warehouse_id}/IN/%')
        ).order_by(Receipt.id.desc()).first()
        
        if last_receipt:
            last_id = int(last_receipt.reference.split('/')[-1])
            new_id = last_id + 1
        else:
            new_id = 1
            
        self.reference = f'{warehouse_id}/IN/{new_id:03d}'
        return self.reference
    
    def __repr__(self):
        return f'<Receipt {self.reference}>'

class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    
    item = db.relationship('InventoryItem', backref=db.backref('receipt_items', lazy=True))
    
    def __repr__(self):
        return f'<ReceiptItem {self.id}>'
