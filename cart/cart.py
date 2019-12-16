from decimal import Decimal
from django.conf import settings

from shop.models import Product
from coupons.models import Coupon


class Cart(object):
    def __init__(self, request):
        """Initialize cart"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """
            Iterate over the items in the cart and get the products
            from the database.
        """
        product_ids = self.cart.keys()

        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield  item

    def __len__(self):
        """Count all items in the cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total cost of the items in the cart"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_total_products(self):
        return len(self.cart)

    def save(self):
        """Mark the session as modified to make sure it gets saved"""
        self.session.modified = True

    def remove(self, product):
        """Remove product from cart"""
        product_id = str(product.id)
        self.cart.pop(product_id, False)
        self.save()

    def clear(self):
        """Clear the cart session"""
        # del self.session[settings.CART_SESSION_ID]
        self.session.pop(settings.CART_SESSION_ID, False)
        self.save()

    def add(self, product, quantity=1, update_quantity=False):
        """Add a product to the cart or update its quantity.

        :param object product: Product instance to add or update in the cart.
        :param int quantity: An optional integer with the product quantity.
        This defaults to 1.
        :param bool update_quantity: This is a boolean that indicates whether
        the quantity needs to be updated with the given quantity True, or
        whether the new quantity has to be added to the existing quantity False
        """

        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal('100'))  * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
