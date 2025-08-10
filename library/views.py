# library/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from .models import Author, Book, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer, BorrowSerializer, ReturnSerializer
from users.models import CustomUser, get_user_role
from users.permissions import IsLibrarian, IsMember, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone

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
    
"""
^
in swagger it shows endpoints: 
GET /borrow-records/
POST /borrow-records/
GET /borrow-records/{id}/
PUT /borrow-records/{id}/
PATCH /borrow-records/{id}/
DELETE /borrow-records/{id}/
"""	


@swagger_auto_schema(
    method='post',
    request_body=BorrowSerializer,
    examples={
        "application/json": {
            "book": 1
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMember|IsLibrarian])
def borrow_book(request):
    """
    Borrow a book from the library.
    
    ### Request URL:
    ```
    POST /library/borrow/
    ```
    
    ### Request Body Example:
    ```json
    {
        "book": 1
    }
    ```
    
    ### Parameters:
    - **book** (integer, required): ID of the book to borrow
    
    ### Notes:
    - Only members and librarians can borrow books
    - The authenticated user will be automatically set as the borrower
    - Borrow date is automatically set to current date
    """
    serializer = BorrowSerializer(data=request.data)
    if serializer.is_valid():
        book_id = serializer.validated_data['book']        
        book = get_object_or_404(Book, id=book_id)
        member = request.user
        if not member.is_member or member.is_librarian:
            return Response({'error': 'Only a member or librarian can borrow books'}, status=status.HTTP_400_BAD_REQUEST)
        if not book.availability_status:
            return Response({'error': 'Book is not available for borrowing'}, status=status.HTTP_400_BAD_REQUEST)
        borrow_record = BorrowRecord.objects.create(book=book, member=member)        
        book.availability_status = False
        book.save()        
        return Response(BorrowRecordSerializer(borrow_record).data, status=status.HTTP_201_CREATED)    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='post',
    request_body=ReturnSerializer,
    examples={
        "application/json": {
            "borrow_record_id": 5
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMember|IsLibrarian])
def return_book(request): 
    """
    Return a borrowed book to the library.
    
    ### Request URL:
    ```
    POST /library/return/
    ```
    
    ### Request Body Example:
    ```json
    {
        "borrow_record_id": 5
    }
    ```
    
    ### Parameters:
    - **borrow_record_id** (integer, required): ID of the borrow record to return
    
    ### Notes:
    - Only members and librarians can return books
    - Return date is automatically set to current date
    - Members can only return their own borrowed books
    - Librarians can return any borrowed book
    """
    serializer = ReturnSerializer(data=request.data)
    if serializer.is_valid():
        borrow_record_id = serializer.validated_data['borrow_record_id']        
        borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id)        
        if borrow_record.return_date is not None:
            return Response({'error': 'Book has already been returned'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role == 'member' and borrow_record.member != request.user:
            return Response({'error': 'members can only return their own borrowed books'}, status=status.HTTP_403_FORBIDDEN)
        borrow_record.return_date = timezone.now().date()
        borrow_record.save()
        borrow_record.book.availability_status = True
        borrow_record.book.save()
        
        return Response(BorrowRecordSerializer(borrow_record).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



"""
while authenticated,
borrow book:
POST http://127.0.0.1:8000/library/borrow/
request body:
{
    "book": 5
}
response:
201 Created
{
    "id": 1,
    "book": 5,
    "member": 3,
    "borrow_date": "2025-08-10",
    "return_date": null
}

return book:
POST http://127.0.0.1:8000/library/return/
request body:
{
    "borrow_record_id": 1
}
response:
200 OK
{
    "id": 1,
    "book": 5,
    "member": 3,
    "borrow_date": "2025-08-10",
    "return_date": "2025-08-10"
}
"""