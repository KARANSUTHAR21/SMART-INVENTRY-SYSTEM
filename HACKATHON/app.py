import os
import random
import smtplib
from datetime import datetime
from email.message import EmailMessage
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, InventoryItem, Operation, StockMovement, UserSettings, Receipt, ReceiptItem
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = "wareflow-otp-secret-key-change-in-production"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wareflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

SENDER_EMAIL = os.environ.get("EMAIL")
SENDER_PASSWORD = os.environ.get("PASSWORD")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/login/forgot-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        pass
    return render_template('forgot-password.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not full_name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        new_user = User(full_name=full_name,
                        email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data  = request.get_json()
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'})

    otp = str(random.randint(1000, 9999))
    session['otp']       = otp
    session['otp_email'] = email

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your OTP Code - WareFlow'
        msg['From']    = SENDER_EMAIL
        msg['To']      = email
        msg.set_content(
            f"Hi,\n\nYour OTP for password reset is: {otp}\n\n"
            f"This code is valid for this session only.\n\n- WareFlow Team"
        )

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data    = request.get_json()
    entered = data.get('otp', '').strip()

    if entered == session.get('otp'):
        session['otp_verified'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Incorrect OTP. Try again.'})

@app.route('/update-password', methods=['POST'])
def update_password():
    """Update password after OTP verification"""
    data = request.get_json()
    email = data.get('email', '').strip()
    new_password = data.get('new_password', '')
    
    if not email or not new_password:
        return jsonify({'success': False, 'message': 'Email and password are required.'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'})
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'})
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password updated successfully.'})

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard after login"""
    return render_template('dashboard.html', user=current_user)

@app.route('/dashboard/operations')
@login_required
def operations():
    """Operations page"""
    return render_template('operations.html', user=current_user)

@app.route('/dashboard/stock')
@login_required
def stock():
    """Stock management page"""
    return render_template('stock.html', user=current_user)

@app.route('/dashboard/history')
@login_required
def history():
    """History page"""
    return render_template('history.html', user=current_user)

@app.route('/dashboard/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html', user=current_user)

@app.route('/receipts')
@login_required
def receipts():
    """Receipts page"""
    return render_template('receipts.html', user=current_user)

@app.route('/dashboard/deliveries')
@login_required
def deliveries():
    """Deliveries page"""
    return render_template('deliveries.html', user=current_user)

@app.route('/api/inventory', methods=['GET', 'POST'])
@login_required
def inventory_api():
    if request.method == 'GET':
        items = InventoryItem.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': item.id,
            'name': item.name,
            'sku': item.sku,
            'quantity': item.quantity,
            'price': item.price,
            'category': item.category,
            'location': item.location
        } for item in items])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        new_item = InventoryItem(
            name=data.get('name'),
            sku=data.get('sku'),
            quantity=data.get('quantity', 0),
            price=data.get('price', 0.0),
            category=data.get('category', ''),
            location=data.get('location', ''),
            user_id=current_user.id
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({'success': True, 'id': new_item.id})

@app.route('/api/inventory/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def inventory_item(item_id):
    item = InventoryItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    if request.method == 'PUT':
        data = request.get_json()
        item.name = data.get('name', item.name)
        item.sku = data.get('sku', item.sku)
        item.quantity = data.get('quantity', item.quantity)
        item.price = data.get('price', item.price)
        item.category = data.get('category', item.category)
        item.location = data.get('location', item.location)
        
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/operations', methods=['GET', 'POST'])
@login_required
def operations_api():
    if request.method == 'GET':
        operations = Operation.query.filter_by(user_id=current_user.id).order_by(Operation.created_at.desc()).all()
        return jsonify([{
            'id': op.id,
            'operation_type': op.operation_type,
            'item_name': op.item.name if op.item else 'Unknown',
            'quantity': op.quantity,
            'reference': op.reference,
            'notes': op.notes,
            'created_at': op.created_at.isoformat()
        } for op in operations])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        new_operation = Operation(
            operation_type=data.get('operation_type'),
            item_id=data.get('item_id'),
            quantity=data.get('quantity'),
            reference=data.get('reference', ''),
            notes=data.get('notes', ''),
            user_id=current_user.id
        )
        
        db.session.add(new_operation)
        
        item = InventoryItem.query.get(data.get('item_id'))
        if item:
            if data.get('operation_type') in ['purchase', 'adjustment_in']:
                item.quantity += data.get('quantity', 0)
            elif data.get('operation_type') in ['sale', 'adjustment_out']:
                item.quantity -= data.get('quantity', 0)
     
            movement = StockMovement(
                item_id=item.id,
                movement_type='in' if data.get('operation_type') in ['purchase', 'adjustment_in'] else 'out',
                quantity=data.get('quantity'),
                operation_id=new_operation.id,
                user_id=current_user.id
            )
            db.session.add(movement)
        
        db.session.commit()
        return jsonify({'success': True, 'id': new_operation.id})


@app.route('/api/stock', methods=['GET', 'POST'])
@login_required
def stock_api():
    if request.method == 'GET':
        items = InventoryItem.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': item.id,
            'name': item.name,
            'sku': item.sku,
            'quantity': item.quantity,
            'price': item.price,
            'category': item.category,
            'location': item.location,
            'low_stock': item.quantity < 10
        } for item in items])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        movement = StockMovement(
            item_id=data.get('item_id'),
            movement_type=data.get('movement_type'),
            quantity=data.get('quantity'),
            from_location=data.get('from_location'),
            to_location=data.get('to_location'),
            user_id=current_user.id
        )
        
        db.session.add(movement)
        
        item = InventoryItem.query.get(data.get('item_id'))
        if item:
            if data.get('movement_type') == 'in':
                item.quantity += data.get('quantity')
            elif data.get('movement_type') == 'out':
                item.quantity -= data.get('quantity')
            elif data.get('movement_type') == 'transfer':
                item.location = data.get('to_location')
        
        db.session.commit()
        return jsonify({'success': True})


@app.route('/api/history', methods=['GET'])
@login_required
def history_api():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    operations = Operation.query.filter_by(user_id=current_user.id).order_by(Operation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'operations': [{
            'id': op.id,
            'operation_type': op.operation_type,
            'item_name': op.item.name if op.item else 'Unknown',
            'quantity': op.quantity,
            'reference': op.reference,
            'notes': op.notes,
            'created_at': op.created_at.isoformat()
        } for op in operations.items],
        'total': operations.total,
        'pages': operations.pages,
        'current_page': page
    })


@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def settings_api():
    if request.method == 'GET':
        settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'company_name': settings.company_name,
            'low_stock_threshold': settings.low_stock_threshold,
            'email_notifications': settings.email_notifications,
            'theme': settings.theme
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
        
        settings.company_name = data.get('company_name')
        settings.low_stock_threshold = data.get('low_stock_threshold', 10)
        settings.email_notifications = data.get('email_notifications', True)
        settings.theme = data.get('theme', 'light')
        
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/receipts', methods=['GET', 'POST'])
@login_required
def receipts_api():
    if request.method == 'POST':
        data = request.get_json()
       
        receipt = Receipt(
            from_entity=data.get('from_entity'),
            to_location=data.get('to_location'),
            contact=data.get('contact'),
            schedule_date=datetime.strptime(data.get('schedule_date'), '%Y-%m-%d').date(),
            status=data.get('status', 'Ready'),
            notes=data.get('notes', ''),
            user_id=current_user.id
        )
        
        receipt.generate_reference()
        
        db.session.add(receipt)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': receipt.id,
            'reference': receipt.reference
        })
    
    else:  
        receipts = Receipt.query.filter_by(user_id=current_user.id).order_by(Receipt.created_at.desc()).all()
        return jsonify([{
            'id': receipt.id,
            'reference': receipt.reference,
            'from_entity': receipt.from_entity,
            'to_location': receipt.to_location,
            'contact': receipt.contact,
            'schedule_date': receipt.schedule_date.strftime('%Y-%m-%d'),
            'status': receipt.status,
            'notes': receipt.notes,
            'created_at': receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for receipt in receipts])

@app.route('/api/receipts/<int:receipt_id>/items', methods=['GET', 'POST'])
@login_required
def receipt_items_api(receipt_id):
    receipt = Receipt.query.filter_by(id=receipt_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json()
        
        receipt_item = ReceiptItem(
            receipt_id=receipt_id,
            item_id=data.get('item_id'),
            quantity=data.get('quantity'),
            unit_price=data.get('unit_price'),
            total_price=data.get('quantity') * data.get('unit_price'),
            notes=data.get('notes', '')
        )
        
        db.session.add(receipt_item)
        db.session.commit()
        
        return jsonify({'success': True, 'id': receipt_item.id})
    
    else: 
        items = ReceiptItem.query.filter_by(receipt_id=receipt_id).all()
        return jsonify([{
            'id': item.id,
            'item_id': item.item_id,
            'item_name': item.item.name if item.item else 'Unknown',
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total_price': item.total_price,
            'notes': item.notes
        } for item in items])

if __name__ == '__main__':
    app.run(debug=True)


