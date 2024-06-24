import logging
import json
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.contrib.auth import get_user_model
import string
from core_payment.models import Receipts
from core_payment.serializers import PaymentSerializer
User = get_user_model()



logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def generate_receipt_id(prefix="CM-SKU", length=8):
        """
        Generate a receipt ID with a specified prefix and a random string of a specified length.
    
        Args:
            prefix (str): The fixed prefix for the receipt ID. Default is "CM-SKU".
            length (int): The length of the random string to generate. Default is 8.
    
        Returns:
            str: A receipt ID with the specified prefix followed by a random string of the specified length.
        """
        letters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(letters) for i in range(length))
        return f"{prefix}{random_string}"
    
    
    def post(self, request):
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        # Move the product_id retrieval here
        tutor_id = request.data.get('tutor_id')

        try:
            tutor = User.objects.get(id=tutor_id)
        except ObjectDoesNotExist:
            return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_blocked:
            try:

                customer = stripe.Customer.create()

                ephemeralKey = stripe.EphemeralKey.create(
                    customer=customer['id'],
                    stripe_version='2023-08-16',
                )
                # Create a PaymentIntent
                payment_intent = stripe.PaymentIntent.create(
                    amount=(user.hourly_rate)*100,
                    currency="gbp",
                    customer=customer['id'],
                    automatic_payment_methods={"enabled": True},
                )
                print("Payment Intent", payment_intent)
                # You would typically pass the client_secret to the frontend
                client_secret = payment_intent.client_secret
                # Product management logic
                total_price = user.hourly_rate

                receipt_id = self.generate_receipt_id(prefix="CM-SKU", length=8)
                # Record the payment intent ID in your database (don't capture yet)
                order = Receipts.objects.create(
                    receipt_id=receipt_id,
                    student=user,
                    product=tutor.id,  # Change this line to assign the UserProducts instance directly
                    price=total_price,
                )

                # Serialize the payment data for the response
                payment_serializer = PaymentSerializer(order)

                return Response({'client_secret': client_secret, 'ephemeralKey': ephemeralKey.secret, 'customer': customer.id, 'publishableKey': settings.STRIPE_PUBLIC_KEY, 'payment': payment_serializer.data}, status=status.HTTP_201_CREATED)

            except stripe.error.CardError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.RateLimitError as e:
                return Response({'error': 'Rate limit error'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except stripe.error.InvalidRequestError as e:
                return Response({'error': 'Invalid request: {}'.format(str(e))}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.AuthenticationError as e:
                return Response({'error': 'Authentication error'}, status=status.HTTP_401_UNAUTHORIZED)
            except stripe.error.APIConnectionError as e:
                return Response({'error': 'API connection error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except stripe.error.StripeError as e:
                return Response({'error': 'Stripe error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif user.is_blocked:
            return Response({"Error": "You are blocked by admin so you can't buy or sell product"}, status=status.HTTP_403_FORBIDDEN)
        
    