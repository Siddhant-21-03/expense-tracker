from datetime import datetime
from collections import defaultdict
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_next_month(expenses):
    if not expenses:
        return None  # No data, return None for template to handle

    # Step 1: Aggregate expenses by month
    monthly_totals = defaultdict(float)
    for exp in expenses:
        try:
            # Ensure date is in datetime format
            exp_date = exp.date if isinstance(exp.date, datetime) else datetime.strptime(str(exp.date), '%Y-%m-%d')
            month_str = exp_date.strftime('%Y-%m')
            monthly_totals[month_str] += exp.amount
        except Exception as e:
            print(f"Skipping invalid expense entry: {e}")
            continue

    # Step 2: Prepare DataFrame for model training
    df = pd.DataFrame(list(monthly_totals.items()), columns=['month', 'total'])
    df = df.sort_values('month')
    df['month_num'] = range(1, len(df) + 1)

    # Step 3: Check if there's enough data
    if len(df) < 2:
        return None  # Need at least 2 months of data for regression

    # Step 4: Train model and predict
    model = LinearRegression()
    model.fit(df[['month_num']], df['total'])

    next_month = [[df['month_num'].iloc[-1] + 1]]
    predicted_value = model.predict(next_month)[0]
    return round(predicted_value, 2)
