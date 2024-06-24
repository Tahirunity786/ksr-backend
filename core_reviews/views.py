from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions  import IsAuthenticated

from django.contrib.auth import get_user_model

from core_reviews.serializers import ReviewsSerializer

User = get_user_model()
# Create your views here.

class CreateReviews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tutor_id):
        try:
            tutor = User.objects.get(id=tutor_id)
        except User.DoesNotExist:
            return Response({"Success": False, "Info": "Tutor not available"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['tutor'] = tutor.id
        data['reviewer'] = request.user.id 

        serializer = ReviewsSerializer(data=data)
        if serializer.is_valid():
            review = serializer.save()
            tutor.reviews.add(review)  # Add the review to the tutor's reviews field
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)