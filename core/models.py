from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import CustomUser
from django.contrib.auth import get_user_model
from django.utils import timezone



STATUS = [
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In_review"),
    ("published","Published"),
]

RATING = [
    ("1","⭐☆☆☆☆"),
    ("2","⭐⭐☆☆☆"),
    ("3","⭐⭐⭐☆☆"),
    ("4","⭐⭐⭐⭐☆"),
    ("5","⭐⭐⭐⭐⭐"),
]


# Create your models here.
def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id,filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True,length=10,max_length=30,prefix="cat",alphabet="abcdefgh12345")
    title = models.CharField(max_length=100,default="sofa")
    image = models.ImageField(upload_to="category",default="category.jpg")
    description = models.TextField(null = True, blank = True,default="this is a product")

    class Meta:
        verbose_name_plural = 'Categories'

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title



class Product(models.Model):
    STATUS_CHOICE = (
        ("True","True"),
        ("False","False"),
    )
    VARIANTS = (
        ('None','None'),
        ('Size','Size'),
        ('Color','Color'),
        ('Size-Color','Size-Color'),
    )

    pid = ShortUUIDField(unique=True,length=10,max_length=30,alphabet="abcdefgh12345")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null = True,default='babitha@gmail.com')
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name='category')


    title = models.CharField(max_length=100,default="chair")
    image = models.ImageField(upload_to=user_directory_path,default="product.jpg")
    description = models.TextField(null = True, blank = True,default="this is a product")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=100.99)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default=200.99)

    specifications = models.TextField(null=True,blank=True)
    variant = models.CharField(choices=VARIANTS,max_length=10,default='None')
    product_status = models.CharField(choices=STATUS_CHOICE,max_length=10)
    in_stock = models.BooleanField(default=True)

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True,blank=True)

     
    stock = models.PositiveIntegerField(default=0)  # New field to track stock
    max_quantity_per_user = models.PositiveIntegerField(default=10)  # Maximum quantity per user

    class Meta:
        verbose_name_plural = 'Products'

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title



class ProductImages(models.Model):
    images= models.ImageField(upload_to="product-images",default="product.jpg")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,related_name="p_images")
    class Meta:
        verbose_name_plural = 'Product Images'


class Color(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""

class Size(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return self.name





class Variants(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE,blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE,blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)  # Stock available for the variant
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Variant-specific price
    image_id = models.FloatField(default=0)
    

    def __str__(self):
        return f"{self.product.title} - {self.size} / {self.color}"

    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            varimage = img.image.url
        else:
            varimage=""
        return varimage

    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            return mark_safe('<img src="{}" width="50" height="50" />'.format(img.image.url))
        else:
            return ""





class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Discount in percentage
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    used = models.BooleanField(default=False)  # To track if the coupon is used

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()

        # Check if coupon is active
        if not self.is_active:
            return False, "Coupon is not active."

        # Check if coupon is within valid date range
        # if self.valid_from > now:
        #     return False, "Coupon is not yet valid."

        if self.valid_until < now:
            return False, "Coupon has expired."

        return True, ""



class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        # Sum the total_price of all items in the cart
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        # Sum the quantity of all items in the cart
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    variant = models.ForeignKey(Variants, related_name="cart_items", on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="cart_images/", null=True, blank=True)

    @property
    def total_price(self):
        # Determine price based on variant or product
        if self.variant and self.variant.price is not None:
            # If variant price is available, use it
            price = self.variant.price
        elif self.product and self.product.price is not None:
            # If variant price is not available, use product price
            price = self.product.price
        else:
            # If neither variant nor product has a price, set it to 0 and print a warning
            print(f"Warning: Neither product nor variant has a price for {self.product}.")
            price = 0

        # Calculate total price for this CartItem by multiplying with quantity
        return price * self.quantity

    def __str__(self):
        # Return a string showing the quantity and selected variant details
        if self.variant:
            return f"{self.quantity} x {self.product.title} ({self.variant.size.name} - {self.variant.color.name}) in cart"
        return f"{self.quantity} x {self.product.title} in cart"

    def save(self, *args, **kwargs):
        # Set the image to be the product's image if not already set
        if not self.image:
            self.image = self.product.image  # Use the product's main image
        super().save(*args, **kwargs)



class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'Profile for {self.user.email}'


    
class Address(models.Model):
    user = models.ForeignKey(CustomUser,related_name='addresses', on_delete=models.SET_NULL, null = True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100,default="India")
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Address'

        
    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}"
    

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'),('Cancelled', 'Cancelled'),('Returned', 'Returned'),], default='Pending')
    payment_method = models.CharField(max_length=20, choices=[('COD', 'Cash on Delivery'),('wallet', 'Wallet'), ('Online', 'Online Payment')], default='COD')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def apply_discount(self):
        """Applies the discount from the coupon to the total amount."""
        if self.coupon and self.coupon.is_valid()[0]:
            discount_percentage = self.coupon.discount_percentage
            discount_amount = self.total_amount * (discount_percentage / 100)
            self.total_amount -= discount_amount
            self.coupon.save()  # Save the coupon to track its usage
            return self.total_amount
        return self.total_amount

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variants, on_delete=models.CASCADE, null=True, blank=True)  # New variant field
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)


    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.product.price
        super().save(*args, **kwargs)



