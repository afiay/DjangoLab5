
from django import template
from django_app.models import Cart

register = template.Library()


@register.simple_tag
def cart_item_count(user):
    if user.is_authenticated:
        qs = Cart.objects.filter(user=user)
        if qs.exists():
            # calculate total quantity of all items
            return sum(item.quantity for item in qs[0].items.all())
    return 0
