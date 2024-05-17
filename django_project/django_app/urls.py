from django.urls import path
from .views import book_list, book_detail, add_to_cart, remove_from_cart, cart_detail, checkout, signup, rate_book, search_books, order_success

urlpatterns = [
    path('', book_list, name='book_list'),
    path('books/<int:book_id>/', book_detail, name='book_detail'),
    path('add-to-cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/',
         remove_from_cart, name='remove_from_cart'),
    path('cart/', cart_detail, name='cart_detail'),
    path('checkout/', checkout, name='checkout'),
    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('signup/', signup, name='signup'),
    path('rate-book/<int:book_id>/', rate_book, name='rate_book'),
    path('search/', search_books, name='search_books'),
]
