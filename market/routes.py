from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Items, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SaleItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sale_form = SaleItemForm()
    if request.method == 'POST':
        #Purchase item logis
        pruchase_item = request.form.get('purchase_item')
        p_item_obj = Items.query.filter_by(name=pruchase_item).first()
        if p_item_obj:
            if current_user.can_purchase(p_item_obj):
                p_item_obj.buy(current_user)
                flash(f'You have purchased {p_item_obj.name} for {p_item_obj.price}$', category='success')
            else:
                flash(f"Unfortunately, You don't have enough money to purchase {p_item_obj.name}", category='danger')
        #Sell item logis
        sold_item = request.form.get('sold_item')
        s_item_obj = Items.query.filter_by(name=sold_item).first()
        if s_item_obj:
            if current_user.can_sell(s_item_obj):
                s_item_obj.sell(current_user)
                flash(f'You have sold {s_item_obj.name} back to market', category='success')
            else:
                flash(f"Something went wrong with selling {s_item_obj.name}", category='danger')
        return redirect(url_for('market_page'))
            
        
    elif request.method == 'GET':   
        items = Items.query.filter_by(owner=None)
        owned_items = Items.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, 
                               purchase_form=purchase_form, 
                               owned_items=owned_items,
                               selling_form=sale_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successly! You are now logged in as: {user_to_create.username}', category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f'Error from create user: {err}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and \
            attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! you are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash(f'Username or password are not match! Please try again', category='danger')
    return render_template('login_page.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home_page'))
