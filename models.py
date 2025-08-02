from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pets = db.relationship('Pet', backref='owner', lazy=True)
    donations = db.relationship('Donation', backref='donor', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)  # dog, cat, etc.
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)  # Age in months
    gender = db.Column(db.String(10))
    description = db.Column(db.Text)
    health_info = db.Column(db.Text)
    behavior_info = db.Column(db.Text)
    adoption_status = db.Column(db.String(20), default='available')  # available, pending, adopted
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Pet matching attributes
    size = db.Column(db.String(20))  # small, medium, large
    energy_level = db.Column(db.String(20))  # low, medium, high
    good_with_children = db.Column(db.Boolean, default=False)
    good_with_other_pets = db.Column(db.Boolean, default=False)
    special_needs = db.Column(db.Boolean, default=False)
    training_level = db.Column(db.String(30))  # untrained, basic, well_trained
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Pet {self.name}, {self.species}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # food, toys, accessories, etc.
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}, ${self.price}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    shipping_address = db.Column(db.String(255))
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)
    
    def __repr__(self):
        return f'<Order {self.id}, User {self.user_id}>'


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of purchase
    
    def __repr__(self):
        return f'<OrderItem {self.id}, Product {self.product_id}>'


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Donation ${self.amount}, User {self.user_id}>'


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True, cascade='all, delete-orphan'))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    
    def __repr__(self):
        return f'<CartItem User {self.user_id}, Product {self.product_id}, Qty {self.quantity}>'
