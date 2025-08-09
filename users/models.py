# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.utils import timezone

USER_ROLES = (('admin', 'Admin'),('librarian', 'Librarian'),('member', 'Member'))

class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=USER_ROLES)
    mobile_no = models.CharField(max_length=15, blank=True)
    membership_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_librarian(self):
        return self.role == 'librarian'
    
    @property
    def is_member(self):
        return self.role == 'member'
    
    def save(self, *args, **kwargs):
        # Clear membership_date when role is changed to admin or librarian
        if self.role in ['admin', 'librarian']:
            self.membership_date = None
        # Set membership_date when role is changed to member and it's not already set
        elif self.role == 'member' and not self.membership_date:
            self.membership_date = timezone.now().date()
        super().save(*args, **kwargs)

# to handle AnonymousUser
def get_user_role(user):
    if isinstance(user, AnonymousUser):
        return None
    return user.role