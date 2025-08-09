# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser, get_user_role

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
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 'mobile_no']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        user.role = 'member'  # Default role for registration
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