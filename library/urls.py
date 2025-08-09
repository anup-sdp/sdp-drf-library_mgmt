from django.urls import path
from . import views

urlpatterns = [
    path('borrow/', views.borrow_book, name='borrow-book'),
    path('return/', views.return_book, name='return-book'),
]