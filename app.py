import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from yookassa import Configuration, Payment
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///devsite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# YooKassa настройки
Configuration.account_id = os.environ.get('YOOKASSA_ACCOUNT_ID', 'your_account_id')
Configuration.secret_key = os.environ.get('YOOKASSA_SECRET_KEY', 'your_secret_key')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    icon = db.Column(db.String(50), default='💻')
    category = db.Column(db.String(50), default='development')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    payment_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    service = db.relationship('Service', backref='orders')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Инициализация базы данных и создание тестовых услуг
def init_db():
    with app.app_context():
        db.create_all()
        if Service.query.count() == 0:
            services = [
                Service(title='Telegram Бот', description='Разработка ботов любой сложности для Telegram', price=15000, icon='🤖'),
                Service(title='Веб-сайт', description='Создание современных адаптивных веб-сайтов', price=50000, icon='🌐'),
                Service(title='Веб-сервис', description='Разработка полноценных веб-приложений и сервисов', price=100000, icon='⚙️'),
                Service(title='Десктопное приложение', description='Программы для Windows, macOS, Linux', price=80000, icon='💻'),
                Service(title='API Разработка', description='Создание и интеграция REST API', price=40000, icon='🔌'),
                Service(title='Консультация', description='Техническая консультация и аудит проекта', price=5000, icon='💡'),
            ]
            db.session.add_all(services)
            db.session.commit()

# Маршруты
@app.route('/')
def index():
    services = Service.query.all()
    return render_template('index.html', services=services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not email or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('register'))
        
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        flash('Вы успешно вошли!', 'success')
        return redirect(next_page if next_page else url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/order/<int:service_id>', methods=['GET', 'POST'])
def create_order(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        description = request.form.get('description')
        
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            service_id=service.id,
            description=description
        )
        db.session.add(order)
        db.session.commit()
        
        # Создание платежа YooKassa
        payment = Payment.create({
            "amount": {
                "value": str(service.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": url_for('payment_success', order_id=order.id, _external=True)
            },
            "capture": True,
            "description": f'Оплата заказа #{order.id} - {service.title}'
        })
        
        order.payment_id = payment.id
        order.payment_status = 'paid' if payment.paid else 'pending'
        db.session.commit()
        
        if payment.confirmation_token:
            return redirect(payment.confirmation_token)
        
        flash('Заказ создан! Ожидайте подтверждения оплаты.', 'success')
        return redirect(url_for('order_success', order_id=order.id))
    
    return render_template('order.html', service=service)

@app.route('/order-success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_success.html', order=order)

@app.route('/payment-success/<int:order_id>')
def payment_success(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'confirmed'
    db.session.commit()
    flash('Оплата прошла успешно! Ваш заказ принят в работу.', 'success')
    return render_template('payment_success.html', order=order)

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
