from django.shortcuts import render
from .forms import UploadFileForm
from .models import SalesRecord, CustomerFeedback
from django.db.models import Sum
from .utils import predict_future_sales, get_average_sentiment
import pandas as pd
from textblob import TextBlob

def upload_file(request):
    message = ""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                data = pd.read_csv(file)
                columns = data.columns.tolist()

                # CHECK: Is this a Sales file or a Review file?
                
                if 'Revenue' in columns:
                    # Logic for SALES upload
                    for index, row in data.iterrows():
                        SalesRecord.objects.create(
                            date=row['Date'],
                            product_category=row['Category'],
                            quantity_sold=row['Quantity'],
                            revenue=row['Revenue']
                        )
                    message = "Success! Sales Data uploaded."

                elif 'Review' in columns:
                    # Logic for REVIEW upload (New AI Part)
                    for index, row in data.iterrows():
                        # Run AI Analysis immediately
                        analysis = TextBlob(str(row['Review']))
                        score = analysis.sentiment.polarity # Returns -1 to 1

                        CustomerFeedback.objects.create(
                            date=row['Date'],
                            feedback_text=row['Review'],
                            sentiment_score=score # Save the AI score
                        )
                    message = "Success! Reviews analyzed & saved."
                
                else:
                    message = "Error: CSV must have 'Revenue' or 'Review' column."

            except Exception as e:
                message = f"Error: {e}"
    else:
        form = UploadFileForm()
    return render(request, 'analytics/upload.html', {'form': form, 'message': message})

# --- DASHBOARD VIEW ---
def dashboard(request):
    total_revenue = SalesRecord.objects.aggregate(Sum('revenue'))['revenue__sum']
    total_quantity = SalesRecord.objects.aggregate(Sum('quantity_sold'))['quantity_sold__sum']

    total_revenue = SalesRecord.objects.aggregate(Sum('revenue'))['revenue__sum'] or 0
    total_quantity = SalesRecord.objects.aggregate(Sum('quantity_sold'))['quantity_sold__sum'] or 0

    # 3. Handle case where database is empty (None)
    if total_revenue is None:
        total_revenue = 0
        total_quantity = 0

    category_data = SalesRecord.objects.values('product_category').annotate(total=Sum('revenue'))

    # 2. Split into two lists for the Chart (Labels and Numbers)
    chart_labels = []
    chart_values = []
    
    for item in category_data:
        chart_labels.append(item['product_category'])
        chart_values.append(float(item['total'])) # Convert Decimal to Float for JS
    category_data = SalesRecord.objects.values('product_category').annotate(total=Sum('revenue'))
    chart_labels = [item['product_category'] for item in category_data]
    chart_values = [float(item['total']) for item in category_data]

    # --- SEND TO HTML ---
    predicted_revenue, prediction_date = predict_future_sales()

    sentiment_score, sentiment_mood = get_average_sentiment()

    context = {
        'revenue': round(total_revenue, 2),
        'quantity': total_quantity,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        # Add these two new lines:
        'prediction': predicted_revenue, 
        'prediction_date': prediction_date,
        'sentiment_score': sentiment_score,
        'sentiment_mood': sentiment_mood
    }
    return render(request, 'analytics/dashboard.html', context)