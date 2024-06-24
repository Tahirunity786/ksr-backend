from datetime import timedelta
from mimetypes import guess_extension
import os
from urllib.request import urlopen
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import Response
from rest_framework import status, generics
from core_accounts.serializers import CreateUserSerializer, PasswordResetRequestSerializer, PasswordResetSerializer, UpdateUserProfileSerializer, ShowUserProfileSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.base import ContentFile
from core_accounts.renderers import UserRenderer
from core_accounts.token import get_tokens_for_user
from django.utils import timezone

from core_accounts.agent import MailAgent
from core_accounts.models import PasswordResetToken
User = get_user_model()

import logging
logger = logging.getLogger(__name__)

# Create your views here.

class Register(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request, user_type):
        if user_type not in ['tutee', 'tutor']:
            return Response({"Success": False, "Error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_serializer = CreateUserSerializer(data=request.data)
    
        if user_serializer.is_valid():
            current_user = user_serializer.save()
            current_user.user_type = user_type
            current_user.save()
            # mailer = MailAgent()
            # mailer.greeting(current_user)
            token = get_tokens_for_user(current_user)
            sanitized_user = UserSerializer(instance=current_user)
            return Response({"Success": True,'class':user_type, "data": sanitized_user.data, 'token':token}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Success": False, "Error": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email for this user not found"}, status=status.HTTP_400_BAD_REQUEST)

        authenticated_user = authenticate(request, username=user.email, password=password)

        if authenticated_user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if authenticated_user.is_blocked:
            return Response({"error": "Account banned"}, status=status.HTTP_400_BAD_REQUEST)
        
        if authenticated_user.user_type == 'tutee':
            # Check if all required tutee profile fields are filled
            required_fields = [ "info", 'subject', 'stage']
        elif authenticated_user.user_type == 'tutor':

            # Check if all required tutor profile fields are filled
            required_fields = ["date_of_birth", "gender", "mobile_number", "hourly_rate", "experience", "degree"]
        
        complete_profile = all(getattr(authenticated_user, field) for field in required_fields)

        profile_url = settings.BACKEND + authenticated_user.profile.url if authenticated_user.profile else None
        token = get_tokens_for_user(authenticated_user)
        user_data = {
            "user_id": authenticated_user.id,
            "username": authenticated_user.username,
            "class": authenticated_user.user_type,
            "profile_pic": profile_url,
            "token": token,
            "complete_profile_status": complete_profile
        }

        return Response({"message": "Logged in", "user": user_data}, status=status.HTTP_202_ACCEPTED)

 
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        logging.debug(f"Data: {request.data}")
        user = request.user
        serializer = UpdateUserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            current_data = serializer.save()
            file = request.FILES.get('profile')

            if file:
                current_data.profile = file
                current_data.save()
            return Response({"Success": True, "Info": f"Profile updated successfully. file = {file}"}, status=status.HTTP_200_OK)
        return Response({"Success": False, "Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"Success": True, "Info": "User profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class ShowProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"Success": False, 'Info': "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialization
        serialized_user = ShowUserProfileSerializer(instance=user)

        return Response(serialized_user.data, status=status.HTTP_200_OK)

    
class GoogleUserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        
        try:
            # Check if user already exists
            user = User.objects.get(email=email)
            if user.user_type == 'tutee':
                # Check if all required tutee profile fields are filled
                required_fields = ["date_of_birth", "gender", "info", "mobile_number", "certificate"]
            elif user.user_type == 'tutor':

                # Check if all required tutor profile fields are filled
                required_fields = ["date_of_birth", "gender", "mobile_number", "hourly_rate", "experience", "degree"]
        
            complete_profile = all(getattr(user, field) for field in required_fields)
            token = get_tokens_for_user(user)
            sanitized_user = UserSerializer(instance=user)
            return Response({"Success": True,"complete_profile_status":complete_profile, 'auth': token, 'data': sanitized_user.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass  # User does not exist, proceed to create a new user

        user_data = {
            "first_name": data.get("given_name", ""),
            "last_name": data.get("family_name", ""),
            "email": email,
            "is_verified": data.get("email_verified", False),
            "auth_provider": "google",
            "password": User.objects.make_random_password()
        }

        # Handle the profile image
        profile_url = data.get("picture")
        if profile_url:
            profile_response = urlopen(profile_url)
            mime_type = profile_response.info().get_content_type()
            extension = guess_extension(mime_type)
            if not extension:
                return Response({"profile": ["Unsupported image format."]}, status=status.HTTP_400_BAD_REQUEST)
            profile_filename = os.path.basename(profile_url)
            if not profile_filename.endswith(extension):
                profile_filename += extension
            profile_content = ContentFile(profile_response.read(), name=profile_filename)
            user_data["profile"] = profile_content

        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            sanitized_user = UserSerializer(instance=user)
            return Response({"Success": True,'complete_profile_status':False, 'auth': token, 'data': sanitized_user.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        token, created = PasswordResetToken.objects.get_or_create(user=user)
        send_mail(
            'Password Reset Request',
            f'Use this link to reset your password: {settings.FRONTEND_URL}/reset-password/{token.token}/',
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        return Response({"detail": "Password reset link sent"}, status=status.HTTP_200_OK)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        if reset_token.created_at < timezone.now() - timedelta(hours=1):
            reset_token.delete()
            return Response({"detail": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.delete()

        return Response({"detail": "Password has been reset"}, status=status.HTTP_200_OK)