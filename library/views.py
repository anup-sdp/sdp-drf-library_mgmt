from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Author, Book, Member, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, MemberSerializer, BorrowRecordSerializer, BorrowSerializer, ReturnSerializer    


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class BorrowRecordViewSet(ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

# borrow book, POST: http://127.0.0.1:8000/borrow/
@api_view(['POST'])
def borrow_book(request):
    serializer = BorrowSerializer(data=request.data)
    if serializer.is_valid():
        book_id = serializer.validated_data['book']
        member_id = serializer.validated_data['member']
        
        book = get_object_or_404(Book, id=book_id)
        member = get_object_or_404(Member, id=member_id)
        
        if not book.availability_status:
            return Response(
                {'error': 'Book is not available for borrowing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=member
        )
        
        # Update book availability
        book.availability_status = False
        book.save()
        
        return Response(
            BorrowRecordSerializer(borrow_record).data, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# return book, POST: at http://127.0.0.1:8000/return/
@api_view(['POST'])
def return_book(request): 
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
        
        # Update book availability
        borrow_record.book.availability_status = True
        borrow_record.book.save()
        
        return Response(
            BorrowRecordSerializer(borrow_record).data, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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