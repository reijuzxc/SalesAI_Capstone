from django.db import models

class SalesRecord(models.Model):
    date = models.DateField()
    product_category = models.CharField(max_length=100)
    quantity_sold = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.product_category}"

class CustomerFeedback(models.Model):
    date = models.DateField()
    feedback_text = models.TextField()
    # We will calculate this score automatically later using AI
    sentiment_score = models.FloatField(default=0.0) 

    def __str__(self):
        return f"Review on {self.date}"