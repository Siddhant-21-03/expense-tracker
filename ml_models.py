from models import Expense
from datetime import datetime
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_budget(user_id):
    # Load user's expenses from database
    expenses = Expense.query.filter_by(user_id=user_id).all()

    if not expenses:
        return "No data available to make a prediction."

    # Prepare data
    df = pd.DataFrame([{
        'date': exp.date,
        'amount': exp.amount
    } for exp in expenses])

    df['date'] = pd.to_datetime(df['date'])  # ⬅️ convert to datetime first
    df['month'] = df['date'].dt.to_period('M').astype(str)

    monthly_totals = df.groupby('month')['amount'].sum().reset_index()
    monthly_totals['month'] = pd.to_datetime(monthly_totals['month'])

    # Add numeric month index for regression
    monthly_totals['month_num'] = np.arange(len(monthly_totals))

    # Train simple model
    X = monthly_totals[['month_num']]
    y = monthly_totals['amount']
    model = LinearRegression().fit(X, y)

    # Predict for next month
    next_month_num = [[monthly_totals['month_num'].max() + 1]]
    prediction = model.predict(next_month_num)[0]

    return round(prediction, 2)
