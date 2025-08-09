# users/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, get_user_role
from .serializers import CustomUserSerializer, UserRegistrationSerializer, UserLoginSerializer,UserRoleUpdateSerializer
from .permissions import IsLibrarian, IsAdminUser


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    - Admins have full access.
    - Librarians can view and create users.
    - Members can only view their own profile.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_role = get_user_role(user)
        
        if user_role == 'admin':
            return CustomUser.objects.all()
        elif user_role == 'librarian':
            return CustomUser.objects.filter(role='member')
        return CustomUser.objects.filter(id=user.id)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_role(self, request, pk=None):
        """
        Update user role.
        - Only admins can update user roles.
        """
        user = self.get_object()
        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            if user.is_superuser:
                return Response(
                    {'error': 'Cannot change role of a superuser'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
