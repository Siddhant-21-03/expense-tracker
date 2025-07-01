from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm, ExpenseForm
from models import db, User, Expense
from analysis import generate_summary, generate_bar_chart, generate_pie_chart, generate_monthly_trend, get_expense_insights
from ml_models import predict_next_month
from datetime import datetime
import os
import csv
from io import TextIOWrapper
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Aaditya%4019@localhost/expense-tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    form = ExpenseForm()
    user = User.query.get(session['user_id'])
    if form.validate_on_submit():
        expense = Expense(
            category=form.category.data,
            amount=form.amount.data,
            date=form.date.data,
            user_id=user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!')
        return redirect(url_for('dashboard'))
    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).all()
    return render_template('dashboard.html', form=form, expenses=expenses)

@app.route('/delete/<int:id>')
def delete_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    expense = Expense.query.get_or_404(id)
    if expense.user_id != session['user_id']:
        flash("Unauthorized access")
        return redirect(url_for('dashboard'))
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.")
    return redirect(url_for('dashboard'))

@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            if {'category', 'amount', 'date'}.issubset(row):
                new_expense = Expense(
                    category=row['category'],
                    amount=float(row['amount']),
                    date=pd.to_datetime(row['date']),
                    user_id=session['user_id']
                )
                db.session.add(new_expense)
        db.session.commit()
        flash('Expenses imported successfully.')
    else:
        flash('Please upload a valid CSV file.')
    return redirect(url_for('analysis'))


@app.route('/analysis', methods=['GET'])
def analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    expenses = Expense.query.filter_by(user_id=user.id).all()

    chart_type = request.args.get('chart', 'bar')
    if chart_type == 'bar':
        generate_bar_chart(expenses)
    elif chart_type == 'pie':
        generate_pie_chart(expenses)
    elif chart_type == 'trend':
        generate_monthly_trend(expenses)

    summary = generate_summary(expenses)
    insights = get_expense_insights(expenses)

    return render_template(
        'analysis.html',
        summary=summary,
        chart_type=chart_type,
        insights=insights
    )


@app.route('/predict')
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    expenses = Expense.query.filter_by(user_id=user.id).all()
    prediction = predict_next_month(expenses)
    return render_template('prediction.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
