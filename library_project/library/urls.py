from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('books/book_detail/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('authors/author_detail/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my_borrowed'),
    path('library_status/', views.library_status, name='library_status'),
    path('book/<uuid:pk>/renew/', views.renew_book, name='renew_book'),
    path('books_on_loan/', views.LoanedBooksListView.as_view(), name='books_on_loan'),
    path('books_on_maintenance/', views.MaintenanceBooksListView.as_view(), name='books_on_maintenance'),
    path('available_books/', views.AvailableBooksListView.as_view(), name='available_books'),
    path('reserved_books/', views.ReservedBooksListView.as_view(), name='reserved_books'),
]
