from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('authors', views.AuthorViewSet)
router.register('books', views.BookViewSet)
router.register('members', views.MemberViewSet)
router.register('borrow-records', views.BorrowRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('borrow/', views.borrow_book, name='borrow-book'),
    path('return/', views.return_book, name='return-book'),
]
