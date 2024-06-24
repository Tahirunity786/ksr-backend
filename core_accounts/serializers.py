import random
import string
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from core_messaging.serializers import UserSmallSerializer
from core_accounts.models import Availability, PasswordResetToken

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['first_name','last_name', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}
    
    def generate_random_username(self, prefix="CM", length=8):
        letters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(letters) for i in range(length))
        
        max_length = 200
        total_length = len(prefix) + length
        if total_length > max_length:
            raise ValueError(f"Total length of generated username ({total_length}) exceeds the maximum allowed length ({max_length}).")
        
        return f"{prefix}{random_string}"

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2', None)

        validate_password(password)

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        return data

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        if email is None:
            raise serializers.ValidationError({'email': 'Email field is required'})

        validated_data['password'] = validated_data.get('password')
        username = self.generate_random_username(prefix="CM", length=8)
        user = User.objects.create_user(email=email, username=username, **validated_data)
        return user

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = [
            'time_frame', 'monday_from_time', 'monday_to_time', 'tuesday_from_time', 'tuesday_to_time',
            'wednesday_from_time', 'wednesday_to_time', 'thursday_from_time', 'thursday_to_time',
            'friday_from_time', 'friday_to_time', 'saturday_from_time', 'saturday_to_time',
            'sunday_from_time', 'sunday_to_time'
        ]

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    availability = AvailabilitySerializer()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'description', 'subject', 'stage', 'date_of_birth', 'gender', 
                  'mobile_number', 'hourly_rate', 'experience', 'info', 'degree', 'university', 'availability']
        extra_kwargs = {
            'hourly_rate': {'required': False},
            'experience': {'required': False},
            'info': {'required': False},
            'degree': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'subject': {'required': False},
            'stage': {'required': False},
            'university': {'required': False},
            'description': {'required': False},
        }

    def update(self, instance, validated_data):
        availability_data = validated_data.pop('availability', None)
        user_type = instance.user_type

        if user_type == 'tutor':
            validated_data.pop('info', None)
            validated_data.pop('subject', None)
      
        elif user_type == 'tutee':
            validated_data.pop('experience', None)
            validated_data.pop('hourly_rate', None)
            validated_data.pop('degree', None)
            validated_data.pop('description', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if availability_data:
            availability, created = Availability.objects.update_or_create(user=instance, defaults=availability_data)

        return instance
    
class ShowUserProfileSerializer(serializers.ModelSerializer):
    users_messaging_container = UserSmallSerializer(many=True)
    availability = AvailabilitySerializer()
    class Meta:
        model = User
        fields = (
            'id', 'profile', 'profile_slug', 'first_name', 'last_name', 'email', 
            'date_of_birth', 'gender', 'mobile_number', 'user_type', 
            'hourly_rate', 'response_time', 't_to_number_of_students', 
            'experience','university', 'degree', 'info','subject', 'stage','description','availability', 'users_messaging_container'
        )
        extra_kwargs = {
            'hourly_rate': {'required': False},
            'response_time': {'required': False},
            't_to_number_of_students': {'required': False},
            'experience': {'required': False},
            'degree': {'required': False},
            'info': {'required': False},
            'subject': {'required': False}, 
            'stage': {'required': False}, 
            'university': {'required': False}, 
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.user_type == 'tutee':
            # Remove fields specific to tutee
            representation.pop('hourly_rate', None)
            representation.pop('response_time', None)
            representation.pop('t_to_number_of_students', None)
            representation.pop('experience', None)
            representation.pop('degree', None)
            representation.pop('description', None)
            representation.pop('availability', None)
        elif instance.user_type == 'tutor':
            # Remove fields specific to tutor
            representation.pop('info', None)
            representation.pop('subject', None)
            representation.pop('stage', None)
            representation.pop('university', None)
        
        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name',  'email', 'profile', 'profile_slug', 'date_of_birth',
                  'gender', 'mobile_number',
                  'is_blocked', 'is_verified', 'is_staff', 'is_active', 'user_type', 'degree', 'info', 'auth_provider', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        email = validated_data.pop('email')
        user = User.objects.create_user(email=email, password=password, user_type="tutee", **validated_data)
        return user



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No user found with this email address"))
        return value


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_token(self, value):
        if not PasswordResetToken.objects.filter(token=value).exists():
            raise serializers.ValidationError(_("Invalid or expired token"))
        return value

    def validate_new_password(self, value):
        # Add custom password validation if needed
        return value