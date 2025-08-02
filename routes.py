import os
import logging
import json
import shutil
import requests
import math
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Pet, Product, Order, OrderItem, Donation, CartItem
from forms import (LoginForm, RegistrationForm, PetRegistrationForm, 
                 DonationForm, ProfileUpdateForm, SearchForm, PetMatchForm)
import uuid


# Context processor to make cart count available in all templates
@app.context_processor
def inject_cart_count():
    cart_count = 0
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_count = sum(item.quantity for item in cart_items)
    return dict(cart_count=cart_count)


@app.route('/')
def index():
    # Get featured pets (newest 4 pets)
    featured_pets = Pet.query.filter_by(adoption_status='available').order_by(Pet.created_at.desc()).limit(4).all()
    # Get recent donations (only show non-anonymous)
    recent_donations = Donation.query.filter_by(is_anonymous=False).order_by(Donation.donation_date.desc()).limit(3).all()
    return render_template('index.html', featured_pets=featured_pets, recent_donations=recent_donations)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose another.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use another email or login.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/pets')
def pet_listing():
    form = SearchForm(request.args, meta={'csrf': False})
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of pets per page
    
    # Base query
    query = Pet.query.filter_by(adoption_status='available')
    
    # Apply filters if provided
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query = query.filter((Pet.name.like(search_term)) | 
                            (Pet.breed.like(search_term)) | 
                            (Pet.description.like(search_term)))
    
    if form.species.data:
        query = query.filter_by(species=form.species.data)
    
    # Get paginated results
    pets = query.order_by(Pet.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('pet_listing.html', pets=pets, form=form)


@app.route('/pets/<int:pet_id>')
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    # Get other pets from the same owner
    other_pets = []
    if pet.owner:
        other_pets = Pet.query.filter(Pet.user_id == pet.user_id, 
                                     Pet.id != pet.id, 
                                     Pet.adoption_status == 'available').limit(4).all()
    
    return render_template('pet_detail.html', pet=pet, other_pets=other_pets)


@app.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    form = PetRegistrationForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            # Generate a unique filename
            filename = secure_filename(form.image.data.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            try:
                form.image.data.save(file_path)
                image_filename = unique_filename
            except Exception as e:
                app.logger.error(f"Error saving image: {str(e)}")
                flash('Error uploading image. Please try again.', 'danger')
                return render_template('add_pet.html', form=form)
        
        # Create new pet
        pet = Pet(
            name=form.name.data,
            species=form.species.data,
            breed=form.breed.data,
            age=form.age.data,
            gender=form.gender.data,
            description=form.description.data,
            health_info=form.health_info.data,
            behavior_info=form.behavior_info.data,
            image_filename=image_filename,
            user_id=current_user.id
        )
        
        db.session.add(pet)
        db.session.commit()
        
        flash('Pet successfully registered for adoption!', 'success')
        return redirect(url_for('pet_detail', pet_id=pet.id))
    
    return render_template('add_pet.html', form=form)


@app.route('/products')
def products():
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get all unique categories for the filter
    categories = [c[0] for c in db.session.query(Product.category).distinct()]
    
    # Base query
    query = Product.query
    
    # Apply category filter if provided
    if category:
        query = query.filter_by(category=category)
    
    # Get paginated results
    products = query.paginate(page=page, per_page=per_page)
    
    return render_template('products.html', products=products, categories=categories, active_category=category)


@app.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get related products (same category, excluding this product)
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    
    return render_template('product_detail.html', product=product, related_products=related_products)


@app.route('/cart')
@login_required
def view_cart():
    # Get user's cart items with product details
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Shipping cost (could be calculated based on cart total or other factors)
    shipping = 5.99 if total_price > 0 else 0
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price, shipping=shipping)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get quantity from form data
    quantity = int(request.form.get('quantity', 1))
    
    # Check if quantity is valid
    if quantity <= 0:
        flash('Invalid quantity', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Check if product is in stock
    if product.stock < quantity:
        flash(f'Only {product.stock} items available in stock', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Check if product is already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        # Update quantity if already in cart
        cart_item.quantity += quantity
        db.session.commit()
    else:
        # Add new item to cart
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()
    
    flash(f'{product.name} added to your cart', 'success')
    return redirect(url_for('view_cart'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    quantity = int(data.get('quantity', 1))
    
    # Validate quantity
    if quantity <= 0:
        return jsonify({'success': False, 'message': 'Invalid quantity'})
    
    # Check stock
    if quantity > cart_item.product.stock:
        return jsonify({'success': False, 'message': f'Only {cart_item.product.stock} items available in stock'})
    
    # Update quantity
    cart_item.quantity = quantity
    db.session.commit()
    
    # Calculate new values for response
    subtotal = cart_item.product.price * cart_item.quantity
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_subtotal = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)
    shipping = 5.99 if cart_subtotal > 0 else 0
    cart_total = cart_subtotal + shipping
    
    return jsonify({
        'success': True,
        'subtotal': subtotal,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'cart_count': cart_count
    })


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_cart_item(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    # Calculate new values for response
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_subtotal = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)
    shipping = 5.99 if cart_subtotal > 0 else 0
    cart_total = cart_subtotal + shipping
    
    return jsonify({
        'success': True,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'cart_empty': len(cart_items) == 0
    })


@app.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cart cleared'
    })


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        # Calculate total price
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        shipping = 5.99 if total_price > 0 else 0
        final_total = total_price + shipping
        
        # Create new order
        order = Order(
            user_id=current_user.id,
            total_amount=final_total,
            shipping_address=f"{current_user.address}, {current_user.city}, {current_user.state} {current_user.zip_code}"
        )
        db.session.add(order)
        db.session.flush()  # Flush to get the order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update product stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            
        # Clear the cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('profile'))
    
    # GET request - show checkout page
    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    shipping = 5.99 if total_price > 0 else 0
    
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, shipping=shipping)


@app.route('/donate', methods=['GET', 'POST'])
def donate():
    form = DonationForm()
    
    # Get recent donations for display (non-anonymous only)
    recent_donations = Donation.query.filter_by(is_anonymous=False).order_by(Donation.donation_date.desc()).limit(5).all()
    
    # Handle anonymous donations (no login required)
    if form.validate_on_submit():
        user_id = current_user.id if current_user.is_authenticated else None
        
        donation = Donation(
            user_id=user_id,
            amount=form.amount.data,
            message=form.message.data,
            is_anonymous=form.is_anonymous.data
        )
        
        db.session.add(donation)
        db.session.commit()
        
        flash('Thank you for your donation!', 'success')
        return redirect(url_for('donate'))
    
    return render_template('donate.html', form=form, recent_donations=recent_donations)


@app.route('/pet-match', methods=['GET', 'POST'])
def pet_match():
    form = PetMatchForm()
    
    if form.validate_on_submit():
        preferences = {
            'species': form.species.data,
            'age_preference': form.age_preference.data,
            'gender_preference': form.gender_preference.data,
            'size_preference': form.size_preference.data,
            'energy_level': form.energy_level.data,
            'good_with_children': form.good_with_children.data == 'yes',
            'good_with_other_pets': form.good_with_other_pets.data == 'yes',
            'special_needs': form.special_needs.data == 'yes',
            'living_environment': form.living_environment.data,
            'time_availability': form.time_availability.data,
            'training_preference': form.training_preference.data
        }
        
        # Store preferences in session for API use
        session['match_preferences'] = preferences
        
        # Redirect to results
        return redirect(url_for('pet_match_results'))
    
    return render_template('pet_match.html', form=form)


@app.route('/pet-match-results')
def pet_match_results():
    # Get preferences from session
    preferences = session.get('match_preferences')
    if not preferences:
        flash('Please fill out the pet matching form first.', 'warning')
        return redirect(url_for('pet_match'))
    
    # Get all available pets
    available_pets = Pet.query.filter_by(adoption_status='available').all()
    
    # Calculate match scores
    matching_pets = []
    for pet in available_pets:
        score = calculate_match_score(pet, preferences)
        matching_pets.append((pet, score))
    
    # Sort by score (highest first)
    matching_pets.sort(key=lambda x: x[1], reverse=True)
    
    # Only show pets with at least 50% match
    matching_pets = [match for match in matching_pets if match[1] >= 50]
    
    return render_template('pet_match_results.html', matching_pets=matching_pets, preferences=preferences)


@app.route('/api/pet-match', methods=['POST'])
def api_pet_match():
    # Get preferences from request JSON
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    preferences = {
        'species': data.get('species', 'any'),
        'age_preference': data.get('age_preference', 'any'),
        'gender_preference': data.get('gender_preference', 'any'),
        'size_preference': data.get('size_preference', 'any'),
        'energy_level': data.get('energy_level', 'any'),
        'good_with_children': data.get('good_with_children', False),
        'good_with_other_pets': data.get('good_with_other_pets', False),
        'special_needs': data.get('special_needs', False),
        'living_environment': data.get('living_environment', 'any'),
        'time_availability': data.get('time_availability', 'any'),
        'training_preference': data.get('training_preference', 'any')
    }
    
    # Get all available pets
    available_pets = Pet.query.filter_by(adoption_status='available').all()
    
    # Calculate match scores
    matching_pets = []
    for pet in available_pets:
        score = calculate_match_score(pet, preferences)
        if score >= 50:  # Only include pets with at least 50% match
            pet_data = {
                'id': pet.id,
                'name': pet.name,
                'species': pet.species,
                'breed': pet.breed,
                'age': pet.age,
                'gender': pet.gender,
                'image_url': url_for('static', filename=f'uploads/{pet.image_filename}', _external=True) if pet.image_filename else None,
                'match_score': score
            }
            matching_pets.append(pet_data)
    
    # Sort by score (highest first)
    matching_pets.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Return the matches
    return jsonify({
        'matches': matching_pets,
        'count': len(matching_pets)
    })


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username is taken by someone else
        user_check = User.query.filter_by(username=form.username.data).first()
        if user_check and user_check.id != current_user.id:
            flash('That username is already taken.', 'danger')
            return render_template('profile.html', form=form)
        
        # Check if email is taken by someone else
        email_check = User.query.filter_by(email=form.email.data).first()
        if email_check and email_check.id != current_user.id:
            flash('That email is already registered.', 'danger')
            return render_template('profile.html', form=form)
        
        # Update user profile
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.zip_code = form.zip_code.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    # Get user's pets
    user_pets = Pet.query.filter_by(user_id=current_user.id).all()
    
    # Get user's donations
    user_donations = Donation.query.filter_by(user_id=current_user.id).order_by(Donation.donation_date.desc()).all()
    
    return render_template('profile.html', form=form, user_pets=user_pets, user_donations=user_donations)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message='Page not found (404)'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='Internal server error (500)'), 500


# Initialize the database with sample data
def initialize_db():
    # Create a test user if no users exist
    if User.query.count() == 0:
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            phone="555-123-4567",
            address="123 Test Street",
            city="Testville",
            state="TS",
            zip_code="12345"
        )
        test_user.set_password("password123")
        db.session.add(test_user)
        db.session.commit()
        app.logger.info('Test user created')
    
    # Add sample products if none exist
    if Product.query.count() == 0:
        # Sample product data
        products = [
            {
                'name': 'Premium Dog Food',
                'category': 'Dog Food',
                'price': 29.99,
                'description': 'High-quality dog food made with real meat and vegetables. Suitable for dogs of all ages and breeds.',
                'stock': 50,
                'image_filename': 'dog_food.jpg'
            },
            {
                'name': 'Cat Scratching Post',
                'category': 'Cat Accessories',
                'price': 34.99,
                'description': 'A sturdy scratching post with multiple platforms for your cat to climb and play. Includes a dangling toy.',
                'stock': 35,
                'image_filename': 'scratching_post.jpg'
            },
            {
                'name': 'Pet Carrier',
                'category': 'Travel',
                'price': 49.99,
                'description': 'A comfortable and secure carrier for transporting your pet. Available in multiple sizes to fit most cats and small to medium-sized dogs.',
                'stock': 25,
                'image_filename': 'pet_carrier.jpg'
            },
            {
                'name': 'Dog Leash and Collar Set',
                'category': 'Dog Accessories',
                'price': 19.99,
                'description': 'Durable leash and collar set for daily walks. Made with high-quality materials for comfort and safety.',
                'stock': 45,
                'image_filename': 'dog_leash.jpg'
            },
            {
                'name': 'Cat Food Bowl',
                'category': 'Cat Accessories',
                'price': 12.99,
                'description': 'Shallow, wide bowl designed specifically for cats to prevent whisker fatigue. Non-slip bottom keeps it in place.',
                'stock': 60,
                'image_filename': 'cat_bowl.jpg'
            },
            {
                'name': 'Premium Cat Food',
                'category': 'Cat Food',
                'price': 32.99,
                'description': 'Nutritious cat food made with premium ingredients. Grain-free formula suitable for cats with sensitive stomachs.',
                'stock': 50,
                'image_filename': 'cat_food.jpg'
            }
        ]
        
        for product_data in products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        app.logger.info('Sample products created')
    
    # Only add pets if there are none in the database
    if Pet.query.count() == 0:
        # Get the test user ID
        test_user = User.query.filter_by(username="testuser").first()
        user_id = test_user.id if test_user else None
        
        # Sample pet data
        pets = [
            {
                'name': 'Buddy',
                'species': 'dog',
                'breed': 'Golden Retriever',
                'age': 36,  # 3 years in months
                'gender': 'male',
                'description': 'Buddy is a friendly and energetic Golden Retriever who loves to play fetch and go for long walks. He is great with children and other pets.',
                'health_info': 'Fully vaccinated, neutered, and recently had a health check-up with no issues.',
                'behavior_info': 'Well-trained, knows basic commands, good on a leash, and socialized with other dogs.',
                'adoption_status': 'available',
                'image_filename': 'buddy_golden.jpg',
                'user_id': user_id
            },
            {
                'name': 'Whiskers',
                'species': 'cat',
                'breed': 'Maine Coon',
                'age': 24,  # 2 years in months
                'gender': 'female',
                'description': 'Whiskers is a beautiful Maine Coon with a playful personality. She enjoys cuddling and playing with toys.',
                'health_info': 'Spayed, vaccinated, and tested negative for FeLV and FIV.',
                'behavior_info': 'Litter box trained, good with other cats, a bit shy with strangers at first.',
                'adoption_status': 'available',
                'image_filename': 'whiskers_cat.jpg',
                'user_id': user_id
            },
            {
                'name': 'Max',
                'species': 'dog',
                'breed': 'Beagle',
                'age': 48,  # 4 years in months
                'gender': 'male',
                'description': 'Max is a sweet Beagle who loves to sniff and explore. He has a gentle temperament and gets along well with everyone.',
                'health_info': 'Up-to-date on vaccinations, neutered, and in excellent health.',
                'behavior_info': 'House-trained, knows basic commands, and loves car rides.',
                'adoption_status': 'available',
                'image_filename': 'max_beagle.jpg',
                'user_id': user_id
            },
            {
                'name': 'Luna',
                'species': 'cat',
                'breed': 'Siamese',
                'age': 12,  # 1 year in months
                'gender': 'female',
                'description': 'Luna is a vocal Siamese cat with striking blue eyes. She is very intelligent and forms strong bonds with her human companions.',
                'health_info': 'Spayed, microchipped, and up-to-date on all vaccinations.',
                'behavior_info': 'Litter box trained, quite talkative, and enjoys interactive play.',
                'adoption_status': 'available',
                'image_filename': 'luna_siamese.jpg',
                'user_id': user_id
            },
            {
                'name': 'Rocky',
                'species': 'dog',
                'breed': 'Boxer',
                'age': 30,  # 2.5 years in months
                'gender': 'male',
                'description': 'Rocky is an energetic Boxer with a playful disposition. He is loyal, protective, and great with families.',
                'health_info': 'Neutered, vaccinated, and on monthly heartworm prevention.',
                'behavior_info': 'House-trained, needs regular exercise, and responds well to positive reinforcement training.',
                'adoption_status': 'available',
                'image_filename': 'rocky_boxer.jpg',
                'user_id': user_id
            },
            {
                'name': 'Oliver',
                'species': 'cat',
                'breed': 'Tabby',
                'age': 36,  # 3 years in months
                'gender': 'male',
                'description': 'Oliver is a handsome tabby cat with a laid-back personality. He enjoys window watching and lounging in sunny spots.',
                'health_info': 'Neutered, vaccinated, and has had a dental cleaning.',
                'behavior_info': 'Litter box trained, gets along with other pets, and enjoys being brushed.',
                'adoption_status': 'available',
                'image_filename': 'oliver_tabby.jpg',
                'user_id': user_id
            }
        ]
        
        # We'll use the existing sample pet images that are already in the static/uploads folder
        # All sample pets already have images in static/uploads:
        # buddy_golden.jpg, whiskers_cat.jpg, max_beagle.jpg, luna_siamese.jpg, oliver_tabby.jpg
        
        # We won't need to download images, so we'll just verify that all image files exist
        for pet in pets:
            if pet['image_filename']:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], pet['image_filename'])
                if not os.path.exists(file_path):
                    app.logger.warning(f"Pet image file not found: {pet['image_filename']}")
                    # Set to None if file doesn't exist
                    pet['image_filename'] = None
        
        # Add pet records to database
        for pet_data in pets:
            pet = Pet(**pet_data)
            # Add matching attributes for the pet
            pet = add_pet_matching_attributes(pet)
            db.session.add(pet)
        
        db.session.commit()
        app.logger.info('Database initialized with sample pets')

    # We'll use the existing product images instead of downloading them
    # For now, we'll proceed without downloading images for products
    pass

# Pet matching algorithm
def calculate_match_score(pet, preferences):
    """
    Calculate a match score between a pet and user preferences.
    Returns a score between 0 and 100.
    """
    score = 0
    max_score = 0
    
    # Species match (must match, no partial credit)
    if preferences['species'] == pet.species:
        score += 20
    else:
        return 0  # If species doesn't match, no need to calculate further
    
    max_score += 20
    
    # Age preference
    if preferences['age_preference'] != 'any':
        max_score += 15
        if pet.age is not None:
            if preferences['age_preference'] == 'baby' and pet.age <= 12:  # Under 1 year
                score += 15
            elif preferences['age_preference'] == 'adult' and pet.age > 12 and pet.age <= 84:  # 1-7 years
                score += 15
            elif preferences['age_preference'] == 'senior' and pet.age > 84:  # Over 7 years
                score += 15
    
    # Gender preference
    if preferences['gender_preference'] != 'any':
        max_score += 10
        if pet.gender == preferences['gender_preference']:
            score += 10
    
    # Size preference
    if preferences['size_preference'] != 'any' and pet.size:
        max_score += 10
        if pet.size == preferences['size_preference']:
            score += 10
    
    # Energy level
    if preferences['energy_level'] != 'any' and pet.energy_level:
        max_score += 15
        if pet.energy_level == preferences['energy_level']:
            score += 15
        # Partial credit for close matches
        elif (pet.energy_level == 'medium' and preferences['energy_level'] in ['low', 'high']) or \
             (preferences['energy_level'] == 'medium' and pet.energy_level in ['low', 'high']):
            score += 7
    
    # Good with children
    if preferences['good_with_children']:
        max_score += 10
        if pet.good_with_children:
            score += 10
    
    # Good with other pets
    if preferences['good_with_other_pets']:
        max_score += 10
        if pet.good_with_other_pets:
            score += 10
    
    # Special needs
    if not preferences['special_needs'] and pet.special_needs:
        max_score += 10
        score += 0  # No points if user doesn't want special needs and pet has them
    elif preferences['special_needs']:
        max_score += 5
        score += 5  # Bonus points for being willing to care for special needs
    
    # If there are no pet attributes to match against or max_score is very low, 
    # normalize to avoid division by zero or skewed percentages
    if max_score < 30:
        max_score = 50
        score = 50  # Default to 50% match when we don't have enough info
        
    # Calculate percentage and round
    return int(min(100, math.ceil((score / max_score) * 100)))


# Add pet attributes during database initialization (for sample pets)
def add_pet_matching_attributes(pet):
    """Add matching attributes to sample pets based on their species and breed"""
    # Size defaults
    small_breeds = ['chihuahua', 'pomeranian', 'maltese', 'yorkshire terrier', 'shih tzu']
    large_breeds = ['german shepherd', 'labrador', 'golden retriever', 'boxer', 'rottweiler']
    
    # Set default attributes based on species
    if pet.species == 'dog':
        lower_breed = pet.breed.lower() if pet.breed else ''
        
        # Size
        if any(breed in lower_breed for breed in small_breeds):
            pet.size = 'small'
        elif any(breed in lower_breed for breed in large_breeds):
            pet.size = 'large'
        else:
            pet.size = 'medium'
        
        # Energy level - high for young dogs, medium for adult, low for seniors
        if pet.age and pet.age < 24:  # Under 2 years
            pet.energy_level = 'high'
        elif pet.age and pet.age > 84:  # Over 7 years
            pet.energy_level = 'low'
        else:
            pet.energy_level = 'medium'
        
        # Good with children
        pet.good_with_children = 'golden retriever' in lower_breed or 'labrador' in lower_breed or 'beagle' in lower_breed
        
        # Good with other pets
        pet.good_with_other_pets = 'golden retriever' in lower_breed or 'beagle' in lower_breed
        
        # Training level
        pet.training_level = 'basic'
        
    elif pet.species == 'cat':
        # Size
        pet.size = 'small'
        if 'maine coon' in pet.breed.lower() if pet.breed else False:
            pet.size = 'medium'
        
        # Energy level - high for kittens, medium for adult, low for seniors
        if pet.age and pet.age < 12:  # Under 1 year
            pet.energy_level = 'high'
        elif pet.age and pet.age > 120:  # Over 10 years
            pet.energy_level = 'low'
        else:
            pet.energy_level = 'medium'
        
        # Good with children
        pet.good_with_children = True
        
        # Good with other pets
        pet.good_with_other_pets = True
        
        # Training level
        pet.training_level = 'basic'
    
    # Default special needs
    pet.special_needs = False
    
    return pet

# The initialize_db function will be called from app.py after tables are created
