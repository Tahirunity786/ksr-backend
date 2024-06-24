from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.


class Receipts(models.Model):
    receipt_id = models.CharField(max_length=100, db_index=True, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True, related_name="receipt_made_by")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True, null=True, related_name="payment_made_to")
    date = models.DateField(auto_now_add=True, db_index=True)
    price = models.IntegerField(db_index=True)