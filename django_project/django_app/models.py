from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('nonfiction', 'Non-fiction'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('biography', 'Biography'),
        # Add more genres as needed
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    publication_date = models.DateField()
    cover_image = models.ImageField(
        upload_to='book_covers/', blank=True, null=True)
    genre = models.CharField(
        max_length=20, choices=GENRE_CHOICES, default='fiction')
    is_new_release = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.rating for rating in ratings) / ratings.count()
        return 0


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}\'s Cart'

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items',
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} ({self.quantity})"

    def total_price(self):
        return self.book.price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order {self.id}'

    def calculate_total_price(self):
        return sum(item.total_price() for item in self.books.all())


class Rating(models.Model):
    book = models.ForeignKey(
        Book, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f'{self.rating} - {self.book.title} by {self.user.username}'
