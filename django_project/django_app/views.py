from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import Cart, Order, Book, CartItem, Rating



def book_list(request):
    # Start with all books and annotate with average rating
    books = Book.objects.annotate(avg_rating=Avg('ratings__rating')).all()

    # Get filter parameters from the request
    genre = request.GET.get('genre', '')
    is_new_release = request.GET.get('is_new_release', '') == 'on'
    is_best_seller = request.GET.get('is_best_seller', '') == 'on'
    is_on_sale = request.GET.get('is_on_sale', '') == 'on'
    query = request.GET.get('q', '')

    # Debug: print the filter values to the console
    print("Genre:", genre)
    print("Is new release:", is_new_release)
    print("Is best seller:", is_best_seller)
    print("Is on sale:", is_on_sale)
    print("Query:", query)

    # Apply filters
    if genre:
        books = books.filter(genre=genre)
    if is_new_release:
        books = books.filter(is_new_release=True)
    if is_best_seller:
        books = books.filter(is_best_seller=True)
    if is_on_sale:
        books = books.filter(is_on_sale=True)
    if query:
        books = books.filter(
            Q(title__icontains(query)) | Q(author__icontains(
                query)) | Q(description__icontains(query))
        )

    print("Books count after filtering:", books.count())

    return render(request, 'books/book_list.html', {
        'books': books,
        'genre': genre,
        'is_new_release': is_new_release,
        'is_best_seller': is_best_seller,
        'is_on_sale': is_on_sale,
        'query': query
    })


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user_rating = None
    all_ratings = Rating.objects.filter(book=book)
    if request.user.is_authenticated:
        user_rating = all_ratings.filter(user=request.user).first()
    return render(request, 'books/book_detail.html', {'book': book, 'user_rating': user_rating, 'all_ratings': all_ratings})


def search_books(request):
    query = request.GET.get('q')
    if query is None:
        query = ""
    books = Book.objects.filter(
        Q(title__icontains(query)) | Q(author__icontains(
            query)) | Q(description__icontains(query))
    )
    return render(request, 'books/book_list.html', {'books': books, 'query': query})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    else:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect('book_list')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user_rating = None

    if request.method == 'POST':
        rating_value = request.POST.get('rating')

        if not rating_value:
            context = {
                'book': book,
                'user_rating': user_rating,
                'error_message': "Rating value is required. Please select a value between 1 and 5."
            }
            return render(request, 'books/book_detail.html', context)

        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                raise ValueError("Rating value must be between 1 and 5.")
            user_rating, created = Rating.objects.get_or_create(
                book=book, user=request.user, defaults={'rating': rating_value}
            )
            if not created:
                user_rating.rating = rating_value
                user_rating.save()
            return HttpResponseRedirect(reverse('book_detail', args=[book_id]))
        except (ValueError, TypeError):
            context = {
                'book': book,
                'user_rating': user_rating,
                'error_message': "Invalid rating value. Please select a value between 1 and 5."
            }
            return render(request, 'books/book_detail.html', context)

    return render(request, 'books/book_detail.html', {'book': book, 'user_rating': user_rating})


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                total_price=cart.total_price()
            )
            for item in cart.items.all():
                order.books.add(item.book)
            order.save()
            cart.items.all().delete()  # Clear the cart after checkout
            return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm()
    return render(request, 'checkout.html', {'form': form, 'cart': cart})
