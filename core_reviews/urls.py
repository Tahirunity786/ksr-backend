from django.urls import path
from core_reviews.views import CreateReviews
urlpatterns = [
    path('<int:tutor_id>/', CreateReviews.as_view())
]
