import pandas as pd
from sklearn.linear_model import LinearRegression
from .models import SalesRecord
from textblob import TextBlob
from django.db.models import Avg
from.models import CustomerFeedback

import datetime

def predict_future_sales():
    # 1. Get data from Database
    records = SalesRecord.objects.all().values('date', 'revenue')
    if not records:
        return 0, "Not enough data"

    # 2. Convert to Pandas DataFrame
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])
    
    # 3. Prepare data for AI (Convert dates to "Day numbers")
    # Linear Regression needs Numbers, not Date objects
    df['date_ordinal'] = df['date'].map(datetime.datetime.toordinal)

    X = df[['date_ordinal']] # Input: Time
    y = df['revenue']        # Output: Money

    # 4. Train the Model (The Learning Phase)
    model = LinearRegression()
    model.fit(X, y)

    # 5. Predict Next Month
    last_date = df['date'].max()
    future_date = last_date + datetime.timedelta(days=30)
    future_ordinal = [[future_date.toordinal()]]
    
    prediction = model.predict(future_ordinal)[0]

    return round(prediction, 2), future_date.strftime("%B %Y")

def get_average_sentiment():
    # 1. Get all reviews
    reviews = CustomerFeedback.objects.all()
    if not reviews:
        return 0, "No Data"
    
    # 2. Calculate Average Score (from database)
    avg_score = reviews.aggregate(Avg('sentiment_score'))['sentiment_score__avg']
    
    # 3. Interpret the Score
    # Score is between -1.0 (Bad) and +1.0 (Good)
    if avg_score > 0.5:
        mood = "Very Positive (Happy Customers)"
    elif avg_score > 0:
        mood = "Positive"
    elif avg_score == 0:
        mood = "Neutral"
    else:
        mood = "Negative (Unhappy Customers)"
        
    return round(avg_score, 2), mood