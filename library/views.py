# library/views.py

# library/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from .models import Author, Book, BorrowRecord
from .serializers import (
    AuthorSerializer, 
    BookSerializer, 
    BorrowRecordSerializer, 
    BorrowSerializer, 
    ReturnSerializer
)
from users.models import CustomUser, get_user_role
from users.permissions import IsLibrarian, IsMember, IsAdminUser

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing authors.
    - Librarians have full access.
    - Members can only view authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsLibrarian]
        return super().get_permissions()

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing books.
    
    ### Permissions:
    - **Librarians**: Full access (create, read, update, delete)
    - **Members**: Read-only access (list, retrieve)
    
    ### Endpoints:
    - `GET /books/` - List all books
    - `POST /books/` - Create a new book (Librarian only)
    - `GET /books/{id}/` - Retrieve a specific book
    - `PUT /books/{id}/` - Update a book (Librarian only)
    - `DELETE /books/{id}/` - Delete a book (Librarian only)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsLibrarian]
        return super().get_permissions()

class BorrowRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing borrow records.
    - Librarians have full access.
    - Members can only view their own borrow records.
    """
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_role = get_user_role(user)
        
        if user_role == 'librarian':
            return BorrowRecord.objects.all()
        elif user_role == 'member':
            return BorrowRecord.objects.filter(member=user)
        return BorrowRecord.objects.none()  # Return empty queryset for other cases
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsLibrarian]
        return super().get_permissions()

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMember|IsLibrarian])
def borrow_book(request):
    """
    Borrow a book.
    - Members and librarians can borrow books.
    """
    serializer = BorrowSerializer(data=request.data)
    if serializer.is_valid():
        book_id = serializer.validated_data['book']
        member_id = serializer.validated_data['member']
        
        book = get_object_or_404(Book, id=book_id)
        member = get_object_or_404(CustomUser, id=member_id)
        
        # Check if user is a member
        if not member.is_member:
            return Response(
                {'error': 'User is not a member'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not book.availability_status:
            return Response(
                {'error': 'Book is not available for borrowing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=member
        )
        
        book.availability_status = False
        book.save()
        
        return Response(
            BorrowRecordSerializer(borrow_record).data, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMember|IsLibrarian])
def return_book(request): 
    """
    Return a book.
    - Members and librarians can return books.
    """
    serializer = ReturnSerializer(data=request.data)
    if serializer.is_valid():
        borrow_record_id = serializer.validated_data['borrow_record_id']
        return_date = serializer.validated_data['return_date']
        
        borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id)
        
        if borrow_record.return_date is not None:
            return Response(
                {'error': 'Book has already been returned'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        borrow_record.return_date = return_date
        borrow_record.save()
        
        borrow_record.book.availability_status = True
        borrow_record.book.save()
        
        return Response(
            BorrowRecordSerializer(borrow_record).data, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# valid for practice 22.5:
"""
4. Request & Response Examples

borrow book:
POST: http://127.0.0.1:8000/borrow/
{
    "book": 1,
    "member": 1
}


success response:
HTTP 201 Created
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": 2,
    "book": 1,
    "member": 1,
    "borrow_date": "2025-07-27",
    "return_date": null
}

fail response:
HTTP 400 Bad Request
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "error": "Book is not available for borrowing"
}

return book: post at http://127.0.0.1:8000/return/

{
    "borrow_record_id": 2,
    "return_date": "2025-07-27"
}

HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": 2,
    "book": 1,
    "member": 1,
    "borrow_date": "2025-07-27",
    "return_date": "2025-07-27"
}

"""