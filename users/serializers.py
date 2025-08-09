# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser, get_user_role
from django.conf import settings

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'mobile_no', 'membership_date', 'is_active']
        read_only_fields = ['id', 'membership_date']
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        
        # Allow admins to edit the role field
        if request and hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            user_role = get_user_role(request.user)
            if user_role in ['admin']:
                fields['role'].read_only = False
        
        return fields

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(
        required=True,
        help_text="Required. A valid email address."
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'mobile_no']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        # Set is_active=False if email activation is enabled
        if settings.DJOSER.get('SEND_ACTIVATION_EMAIL', False):
            user = CustomUser.objects.create_user(is_active=False, **validated_data)
        else:
            user = CustomUser.objects.create_user(**validated_data)
        
        user.role = 'member'
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField()

class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user role.
    """
    class Meta:
        model = CustomUser
        fields = ['role']