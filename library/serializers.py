from rest_framework import serializers
from .models import Author, Book, BorrowRecord

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'ISBN', 'category', 'availability_status']
"""
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'membership_date']
"""
        
class BorrowRecordSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(read_only=True)  # Or use a nested serializer
    class Meta:
        model = BorrowRecord
        fields = ['id', 'book', 'member', 'borrow_date', 'return_date']		


class BorrowSerializer(serializers.Serializer):
    book = serializers.IntegerField()
    member = serializers.IntegerField()  # This will be CustomUser ID

class ReturnSerializer(serializers.Serializer):
    borrow_record_id = serializers.IntegerField()
    return_date = serializers.DateField()
    
