import matplotlib
matplotlib.use('Agg')  # ✅ Required for server-side rendering

import matplotlib.pyplot as plt
import io
import base64
from models import Expense
from flask_login import current_user
from sqlalchemy import extract
from extensions import db

def generate_plot_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    image = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)  # ✅ Close to prevent memory leaks
    return f'<img src="data:image/png;base64,{image}" class="chart-img"/>'

def generate_bar_chart(user_id):
    data = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter_by(user_id=user_id).group_by(Expense.category).all()

    if not data:
        return "<p>No data available for Bar Chart</p>"

    categories = [x[0] for x in data]
    totals = [x[1] for x in data]

    fig, ax = plt.subplots()
    ax.bar(categories, totals, color='skyblue')
    ax.set_title("Expenses by Category")
    ax.set_ylabel("Total Amount")
    ax.set_xlabel("Category")
    return generate_plot_image(fig)

def generate_line_chart(user_id):
    data = db.session.query(
        Expense.date,
        db.func.sum(Expense.amount)
    ).filter_by(user_id=user_id).group_by(Expense.date).all()

    if not data:
        return "<p>No data available for Line Chart</p>"

    dates = [x[0].strftime('%d-%b') for x in data]
    totals = [x[1] for x in data]

    fig, ax = plt.subplots()
    ax.plot(dates, totals, marker='o', color='green')
    ax.set_title("Daily Expense Trend")
    ax.set_ylabel("Total Spent")
    ax.set_xlabel("Date")
    ax.set_xticklabels(dates, rotation=45)
    return generate_plot_image(fig)

def generate_pie_chart(user_id):
    data = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter_by(user_id=user_id).group_by(Expense.category).all()

    if not data:
        return "<p>No data available for Pie Chart</p>"

    categories = [x[0] for x in data]
    totals = [x[1] for x in data]

    fig, ax = plt.subplots()
    ax.pie(totals, labels=categories, autopct='%1.1f%%')
    ax.set_title("Expense Distribution")
    return generate_plot_image(fig)
