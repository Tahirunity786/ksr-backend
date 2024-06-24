from django.urls import path
from core_payment.views import PaymentView

urlpatterns = [
    path('public/processing', PaymentView.as_view())
]
