from django.contrib import admin
from core.models import Category,Product,ProductImages,Cart,CartItem,Address,UserProfile,Variants,Order
# Register your models here.


class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user','title', 'product_image','price','category','product_status','stock','max_quantity_per_user']

# Product Varaint
class VariantsAdmin(admin.ModelAdmin):
    list_display=('id','image_tag','product','price','color','size')
admin.site.register(Variants,VariantsAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','category_image']

# Cart Admin
class CartAdmin(admin.ModelAdmin):
    # Define which fields to display in the list view
    list_display = ['user', 'total_price', 'total_items', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']

    # Calculate total price of the cart
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

    # Calculate total items in the cart
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'

    # Pre-fetch related items to avoid N+1 queries
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('items')
        return queryset

# Register Cart Admin
admin.site.register(Cart, CartAdmin)


# CartItem Admin
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price', 'image']
    list_filter = ['cart', 'product']
    search_fields = ['cart__user__username', 'product__title']

    # Calculate total price of the cart item (price * quantity)
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

    # Display product image (optional)
    def image(self, obj):
        if obj.product.image:
            return mark_safe(f'<img src="{obj.product.image.url}" width="50" height="50" />')
        return "No image"
    image.short_description = 'Product Image'


# Register CartItem Admin
admin.site.register(CartItem, CartItemAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'bio', 'birth_date']

admin.site.register(UserProfile, UserProfileAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','address_line1','address_line2','city','state','postal_code','is_default']



# Optionally, create a custom Admin class for Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'payment_method', 'placed_at', 'coupon')  # Customize columns displayed in the list view
    search_fields = ('user__username', 'id', 'coupon__code')  # Allow searching by user or order ID
    list_filter = ('status', 'payment_method', 'coupon')  # Filters for easy filtering in the admin panel
    readonly_fields = ('placed_at', 'total_amount')  # Fields to be shown as read-only in the admin form

# Register the Order model with the custom admin
admin.site.register(Order, OrderAdmin)

from django.contrib import admin
from .models import ReturnRequest

class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status', 'created_at')  # Display these fields in the admin list
    list_filter = ('status', 'created_at')  # Filter by status and creation date
    search_fields = ('order__id', 'user__username')  # Allow searching by order ID and user username

admin.site.register(ReturnRequest, ReturnRequestAdmin)




admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Address,AddressAdmin)



