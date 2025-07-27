from django.contrib import admin
from .models import Author, Book, Member, BorrowRecord

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'ISBN', 'category', 'availability_status']
    list_filter = ['availability_status', 'category', 'author']
    search_fields = ['title', 'ISBN']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'membership_date']
    search_fields = ['name', 'email']

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'borrow_date', 'return_date']
    list_filter = ['borrow_date', 'return_date']

