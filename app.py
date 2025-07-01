from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from forms import RegisterForm, LoginForm, ExpenseForm
from models import db, User, Expense
from analysis import generate_bar_chart, generate_line_chart, generate_pie_chart
from extensions import db
from ml_models import predict_budget
import pandas as pd



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Aaditya%4019@localhost/expense-tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from extensions import db
db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):

            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            category=form.category.data,
            date=form.date.data,
            note=form.note.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully.', 'success')
        return redirect(url_for('home'))

    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('home.html', form=form, expenses=expenses)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html",
        total_spent=get_total_spent(current_user.id),
        max_day=get_max_spent_day(current_user.id),
        min_day=get_min_spent_day(current_user.id),
        monthly_avg=get_monthly_average(current_user.id)
    )

@app.route('/predictions')
@login_required
def predictions():
    prediction = predict_budget(current_user.id)
    return render_template('predictions.html', prediction=prediction)


@app.route("/analysis")
@login_required
def analysis():
    user_id = current_user.id

    # 1. All expenses for the user
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([{
        'date': e.date,
        'category': e.category,
        'amount': e.amount,
        'description': e.note 
    } for e in expenses])

    # 2. Total spent
    total_spent = df['amount'].sum() if not df.empty else 0

    # 3. Max spent day
    if not df.empty:
        daily_totals = df.groupby('date')['amount'].sum()
        max_day = daily_totals.idxmax()
        min_day = daily_totals.idxmin()
    else:
        max_day = "N/A"
        min_day = "N/A"

    # 4. Category-wise totals
    category_totals = df.groupby('category')['amount'].sum().to_dict() if not df.empty else {}

    # 5. Generate charts
    bar_chart = generate_bar_chart(user_id)
    line_chart = generate_line_chart(user_id)
    pie_chart = generate_pie_chart(user_id)

    # 6. Render template
    return render_template("analysis.html",
        total_spent=total_spent,
        max_day=max_day,
        min_day=min_day,
        category_totals=category_totals,
        bar_chart=bar_chart,
        line_chart=line_chart,
        pie_chart=pie_chart,
        expenses=expenses
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
