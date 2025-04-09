import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, AIProduct, SiteSettings  # Assuming the models are defined in models.py

app = Flask(__name__)
app.config.from_object('config.Config')  # or use app.config['SECRET_KEY'] = 'your_secret_key'

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

# User Registration Route (Password Hashing)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')  # Hash the password

        # Create a new user
        new_user = User(name=name, email=email, password=hashed_password, status='Active')

        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# User Login Route (Check Hashed Password)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):  # Check hashed password
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    return render_template('admin-dashboard.html')

# Users Management Route
@app.route('/users')
@login_required
def users():
    users = User.query.all()  # Get all users from the database
    return render_template('users.html', users=users)

# Edit User Route
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.status = request.form['status']
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('edit_user.html', user=user)

# Delete User Route
@app.route('/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

# AI Management Route
@app.route('/ai-management')
@login_required
def ai_management():
    ai_products = AIProduct.query.all()
    return render_template('ai-management.html', ai_products=ai_products)

# Edit AI Product Route
@app.route('/edit_ai/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ai(id):
    ai_product = AIProduct.query.get_or_404(id)
    if request.method == 'POST':
        ai_product.name = request.form['name']
        ai_product.status = request.form['status']
        db.session.commit()
        return redirect(url_for('ai_management'))
    return render_template('edit_ai.html', ai_product=ai_product)

# Site Settings Route
@app.route('/site-settings', methods=['GET', 'POST'])
@login_required
def site_settings():
    settings = SiteSettings.query.first()
    if request.method == 'POST':
        settings.site_name = request.form['site_name']
        settings.contact_email = request.form['contact_email']
        settings.whatsapp_number = request.form['whatsapp_number']
        settings.currency = request.form['currency']
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('site_settings'))
    return render_template('site-settings.html', settings=settings)

@app.route('/reports')
@login_required
def reports():
    active_users_count = User.query.filter_by(status='Active').count()
    total_users_count = User.query.count()

    # Create a pie chart using Graph Objects
    fig = go.Figure(data=[go.Pie(labels=["Active Users", "Total Users"], values=[active_users_count, total_users_count])])
    fig.update_layout(title="User Statistics")
    
    graph_html = fig.to_html(full_html=False)

    return render_template('reports.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
