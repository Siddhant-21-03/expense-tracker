import matplotlib.pyplot as plt
import os
from collections import defaultdict
def get_expense_insights(expenses):
    total_spent = sum(exp.amount for exp in expenses)

    category_totals = defaultdict(float)
    daily_totals = defaultdict(float)

    for exp in expenses:
        category_totals[exp.category] += exp.amount
        daily_totals[exp.date.strftime('%Y-%m-%d')] += exp.amount

    max_day = max(daily_totals.items(), key=lambda x: x[1]) if daily_totals else ('N/A', 0)

    return {
        'total_spent': round(total_spent, 2),
        'category_totals': dict(category_totals),
        'max_spent_day': max_day[0],
        'max_spent_amount': round(max_day[1], 2)
    }
def generate_summary(expenses):
    summary = defaultdict(float)
    for exp in expenses:
        summary[exp.category] += exp.amount
    return dict(summary)

def save_plot(fig):
    path = os.path.join('static', 'expense_chart.png')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)

def generate_bar_chart(expenses):
    summary = generate_summary(expenses)
    fig, ax = plt.subplots()
    ax.bar(summary.keys(), summary.values(), color='skyblue')
    ax.set_title('Expenses by Category')
    ax.set_ylabel('Amount')
    save_plot(fig)

def generate_pie_chart(expenses):
    summary = generate_summary(expenses)
    fig, ax = plt.subplots()
    ax.pie(summary.values(), labels=summary.keys(), autopct='%1.1f%%', startangle=140)
    ax.set_title('Expense Distribution')
    save_plot(fig)

def generate_monthly_trend(expenses):
    data = defaultdict(float)
    for exp in expenses:
        month = exp.date.strftime('%Y-%m')
        data[month] += exp.amount

    sorted_data = dict(sorted(data.items()))
    fig, ax = plt.subplots()
    ax.plot(list(sorted_data.keys()), list(sorted_data.values()), marker='o', linestyle='-', color='green')
    ax.set_title('Monthly Expense Trend')
    ax.set_ylabel('Amount')
    plt.xticks(rotation=45)
    save_plot(fig)
