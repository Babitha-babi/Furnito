from django.shortcuts import render,get_object_or_404,HttpResponse,redirect
from core.models import Product,Category,ProductImages,Cart,CartItem,Address, Order,UserProfile,OrderItem,Coupon,Size,Color,Variants,Coupon,ReturnRequest
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.urls import reverse
from django.contrib import messages
from walletapp.models import Wallet, WalletTransaction
from decimal import Decimal
from .forms import AddressForm,EditProfileForm,EditAddressForm,ReturnRequestForm
from django.db.models import Q
from .paypal_utils import configure_paypal
import paypalrestsdk
from django.utils import timezone

# Create your views here.

def index(request):
    items = Product.objects.all()
    context = {
        "products":items
    }
    return render(request,'user/index.html',context)


def product_list_view(request):
    # Get all products and categories
    items = Product.objects.all()
    categories = Category.objects.filter(is_blocked=False)


    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by')

    # Apply search filter
    if search_query:
        items = items.filter(title__icontains=search_query)

    # Apply price filter
    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            items = items.filter(price__gte=min_price, price__lte=max_price)
        except ValueError:
            pass  # If the price values are invalid, don't apply the filter

    # Apply sorting
    if sort_by == 'price_low_high':
        items = items.order_by('price')
    elif sort_by == 'price_high_low':
        items = items.order_by('-price')
    elif sort_by == 'new_arrivals':
        items = items.order_by('-date')  # Sort by newest products
    elif sort_by == 'a_to_z':
        items = items.order_by('title')  # Sort A to Z by title
    elif sort_by == 'z_to_a':
        items = items.order_by('-title')  # Sort Z to A by title

    # Calculate total stock for each product
    for product in items:
        total_stock = sum(variant.stock for variant in product.variants_set.all())
        product.total_stock = total_stock  # Add the total stock attribute to product

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(items, 12)  # Show 12 products per page
    page_obj = paginator.get_page(page_number)

    # Pass the context to the template
    context = {
        'items': items,
        'products': page_obj,
        'categories': categories,
        'search': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }

    return render(request, 'user/product_list.html', context)


def category_list_view(request):
    category =Category.objects.filter(is_blocked=False)

    context = {
        "category":category
    }
    return render(request,'user/category_list.html',context)



def category_product_list_view(request, cid):
    # Get the category by ID
    category = get_object_or_404(Category, cid=cid)

    # Get the products in the selected category
    products = Product.objects.filter(category=category)

    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by')

    # Apply search filter
    if search_query:
        products = products.filter(title__icontains=search_query)

    # Apply price filter
    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            products = products.filter(price__gte=min_price, price__lte=max_price)
        except ValueError:
            pass  # If the price values are invalid, don't apply the filter

    # Apply sorting
    if sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    elif sort_by == 'new_arrivals':
        products = products.order_by('-date')  # Sort by newest products
    elif sort_by == 'a_to_z':
        products = products.order_by('title')  # Sort A to Z by title
    elif sort_by == 'z_to_a':
        products = products.order_by('-title')  # Sort Z to A by title


    for product in products:
        variants = Variants.objects.filter(product=product)
        total_stock = sum([variant.stock for variant in variants])
        product.total_stock = total_stock 

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_obj = paginator.get_page(page_number)

    # Pass the context to the template
    context = {
        'category': category,
        'products': page_obj,
        'search': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }

    return render(request, 'user/category_product_list.html', context)



def product_detail_view(request, pid):
    # Fetch the product, handle the case if it does not exist
    product = get_object_or_404(Product, pid=pid)

    # Fetch all the images related to the product
    p_images = product.p_images.all()

    # Fetch all variants (sizes and colors) associated with the product
    variants = Variants.objects.filter(product=product).select_related('color', 'size').distinct()

    # Get unique colors and sizes
    colors = set(variant.color for variant in variants)
    sizes = set(variant.size for variant in variants)

    # Get the default variant (first available variant if any)
    default_variant = variants.first() if variants.exists() else None

    # Calculate total stock
    total_stock = sum([variant.stock for variant in variants])

    # Context to pass to the template
    context = {
        "product": product,
        "p_images": p_images,
        "variants": variants,
        "total_stock": total_stock,
        "default_variant": default_variant,
        "colors": colors,
        "sizes": sizes,
    }

    return render(request, 'user/product_detail.html', context)





def search_view(request):
    query = request.GET.get("q")
    products = Product.objects.filter(title__icontains=query).order_by("date")
    context = {
        "products":products,
        "query":query
    }
    return render(request,'user/search.html',context)



def get_variant_details(request):
    size_id = request.GET.get('size_id')
    color_id = request.GET.get('color_id')
    product_id = request.GET.get('product_id')

    try:
        product = Product.objects.get(id=product_id)
        size = Size.objects.get(id=size_id) if size_id else None
        color = Color.objects.get(id=color_id) if color_id else None

        variant = Variants.objects.filter(product=product, size=size, color=color).first()

        if variant:
            response_data = {
                'price': variant.price,
                'stock': variant.stock,
            }
        else:
            response_data = {
                'price': product.price,
                'stock': product.stock,
            }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_to_cart(request, product_id):
    # Fetch the product
    product = get_object_or_404(Product, id=product_id)

    # Get selected size and color from POST data
    selected_size_id = request.POST.get('selected_size')
    selected_color_id = request.POST.get('selected_color')
    quantity = int(request.POST.get('quantity', 1))

    # Fetch the selected size and color from the database
    selected_size = get_object_or_404(Size, id=selected_size_id) if selected_size_id else None
    selected_color = get_object_or_404(Color, id=selected_color_id) if selected_color_id else None

    # Fetch the correct variant based on size and color
    variant = Variants.objects.filter(
        product=product,
        size=selected_size,
        color=selected_color
    ).first()

    # If the variant doesn't exist, return an error
    if not variant:
        messages.error(request, "The selected variant (size/color) is not available.")
        return redirect('core:product_detail', pid=product.pid)

    # Check if the selected quantity exceeds the variant's stock
    if quantity > variant.stock:
        messages.error(request, f"Sorry, we only have {variant.stock} of {product.title} in this variant.")
        return redirect('core:product_detail', pid=product.pid)

    # Check if the selected quantity exceeds the max allowed per user
    if quantity > product.max_quantity_per_user:
        messages.error(request, f"You can only add a maximum of {product.max_quantity_per_user} of {product.title} to your cart.")
        return redirect('core:product_detail', pid=product.pid)

    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create a cart item for the variant
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, variant=variant)

    if not item_created:
        # If the item already exists in the cart, update the quantity
        new_quantity = cart_item.quantity + quantity

        # Ensure the quantity doesn't exceed the variant's stock or max per user
        if new_quantity > variant.stock:
            messages.error(request, f"Sorry, we only have {variant.stock} of {product.title} in this variant.")
            return redirect('core:product_detail', pid=product.pid)

        if new_quantity > product.max_quantity_per_user:
            messages.error(request, f"You can only add a maximum of {product.max_quantity_per_user} of {product.title} to your cart.")
            return redirect('core:product_detail', pid=product.pid)

        # Update the cart item quantity
        cart_item.quantity = new_quantity
        cart_item.save()
    else:
        # If it's a new cart item, set the quantity
        cart_item.quantity = quantity
        cart_item.save()

    # Update the variant stock after the item is added to the cart
    # variant.stock -= quantity
    # variant.save()

    messages.success(request, f"{product.title} ({selected_size.name}, {selected_color.name}) has been added to your cart.")
    return redirect('core:cart_detail')




@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    product = cart_item.product
    variant = cart_item.variant  # The selected variant

    # Get the new quantity from the form
    new_quantity = request.POST.get('quantity')

    # Check if the new quantity is valid
    if new_quantity and new_quantity.isdigit():
        new_quantity = int(new_quantity)

        # Ensure the new quantity doesn't exceed available stock for the selected variant
        if new_quantity > variant.stock:
            messages.error(request, f"Sorry, we only have {variant.stock} of {variant.size.name} / {variant.color.name} in stock.")
            return redirect('core:cart_detail')

        # Ensure the new quantity doesn't exceed the max allowed per user for the selected variant
        if new_quantity > product.max_quantity_per_user:
            messages.error(request, f"You can only add a maximum of {product.max_quantity_per_user} of {product.title} to your cart.")
            return redirect('core:cart_detail')

        # Restore the stock before updating
        variant.stock += cart_item.quantity  # Restore previous variant quantity
        variant.save()

        # Update the quantity in the cart
        cart_item.quantity = new_quantity
        cart_item.save()

        # Update stock (decrease stock after the quantity update)
        variant.stock -= new_quantity
        variant.save()

        messages.success(request, f"Your quantity for {product.title} ({variant.size.name} / {variant.color.name}) has been updated to {new_quantity}.")
    else:
        messages.error(request, "Invalid quantity.")

    return redirect('core:cart_detail')


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    product = cart_item.product
    variant = cart_item.variant  # Get the selected variant for the cart item

    # Restore the stock of the variant when removing the item
    variant.stock += cart_item.quantity  # Add the quantity back to the variant stock
    variant.save()

    # Remove the item from the cart
    cart_item.delete()

    messages.success(request, f"{product.title} ({variant.size.name} / {variant.color.name}) has been removed from your cart.")
    return redirect('core:cart_detail')




@login_required
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return render(request, 'user/cart_empty.html')
    
    # Filter out cart items with out-of-stock products
    cart_items = cart.items.filter(product__stock__gt=0)

   
    # Calculate the total price for the cart
    cart_total = sum(item.variant.price * item.quantity if item.variant else item.product.price * item.quantity for item in cart_items)

    # Placeholder for shipping and discount (can be updated later)
    shipping_cost = 0
    discount = 0
    total_after_discount = cart_total + shipping_cost - discount

    # Message for out-of-stock items
    message = ''
    if cart_items.count() < cart.items.count():
        message = 'Some items in your cart are out of stock.'

    return render(request, 'user/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'shipping_cost': shipping_cost,
        'total_after_discount': total_after_discount,
        'message': message
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Cart, Address, Order, OrderItem
from userauths.models import CustomUser
@login_required
def checkout(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)
    
    wallet_balance = wallet.balance

    # Helper function to get the cart
    def get_cart():
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            messages.error(request, "Your cart is empty. Please add items to your cart.")
            return None
        return cart

    # Helper function to apply a coupon
    def apply_coupon(subtotal):
        applied_coupon = request.session.get('applied_coupon', None)
        if applied_coupon:
            coupon = Coupon.objects.filter(code=applied_coupon).first()
            if coupon and coupon.is_valid()[0]:  # Ensure the coupon is valid
                discount = (coupon.discount_percentage / 100) * subtotal
                discounted_total = round(subtotal - discount, 2)
                discount = round(discount, 2)
                messages.success(request, f"Coupon {coupon.code} applied successfully! Discount: ${discount:.2f}")
                
                return discounted_total, discount, coupon  # Return coupon as well
            else:
                messages.error(request, "This coupon is expired or invalid.")
        return subtotal, 0.00, None


    # Get the cart
    cart = get_cart()
    if not cart:
        return redirect('core:product_list')

    cart_items = cart.items.all()
    if not cart_items:
        messages.error(request, "Your cart is empty. Please add items to your cart.")
        return redirect('core:product_list')

    # Calculate total amount in cart (without coupon applied)
    subtotal = Decimal(sum([item.quantity * item.variant.price for item in cart_items]))
    discounted_total, discount, coupon = apply_coupon(subtotal)

     # Ensure an order exists or create a new one
    order = Order.objects.filter(user=user, status='Pending').first()
    if not order:
        # If no pending order, create a new one
        order = Order.objects.create(user=user, total_amount=discounted_total, status='Pending')

    # Handle checkout form submission
    if request.method == 'POST':
        selected_address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # Validate address and payment method
        if not selected_address_id or not payment_method:
            messages.error(request, "Please select an address and payment method to proceed.")
            return render_checkout_page(request, cart_items, discounted_total, discount,subtotal,wallet_balance)

        selected_address = get_object_or_404(Address, id=selected_address_id)

        # Check if there is enough stock for each cart item variant
        for cart_item in cart_items:
            variant = cart_item.variant
            if cart_item.quantity > variant.stock:
                messages.error(request, f"Sorry, we only have {variant.stock} of {variant.product.title} in stock.")
                return redirect('core:cart_detail')

        # Handle payment method
        if payment_method == 'COD' and discounted_total > 1000:
            messages.error(request, "Cash on Delivery is not available for orders above Rs 1000. Please select a different payment method.")
            return render_checkout_page(request, cart_items, discounted_total, discount,subtotal,wallet_balance)

        # Wallet Payment
        if payment_method == 'wallet':
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
           
            if wallet.balance >= discounted_total:
                # Manually deduct funds from the wallet balance
                wallet.balance -= discounted_total
                
                # Save the updated wallet balance to the database
                wallet.save()

                # Create a wallet transaction for the debit
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=Decimal(discounted_total),
                    transaction_type='debited',  # Type of transaction
                )

            else:
                messages.error(request, "Insufficient balance in your wallet.")
                return render_checkout_page(request, cart_items, discounted_total, discount,subtotal,wallet_balance)

        # Create the order
        order = create_order(user, selected_address, discounted_total, payment_method, coupon)

        # Create order items from cart items
        create_order_items(order, cart_items)

        # Clear the cart after placing the order
        cart_items.delete()

        # Clear coupon from session
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        messages.success(request, "Your order has been successfully placed!")
        return redirect('core:order_confirmation', order_id=order.id)

    # Render the checkout page if GET request
    return render_checkout_page(request, cart_items, discounted_total, discount,subtotal,wallet_balance)


# Helper function to render the checkout page
def render_checkout_page(request, cart_items, total_amount, discount,subtotal,wallet_balance):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'user/checkout.html', {
        'addresses': addresses,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'discount': discount,
        'subtotal':subtotal,
        'wallet_balance': wallet_balance,
    })


def create_order(user, selected_address, discounted_total, payment_method, coupon):
    
    
    return Order.objects.create(
        user=user,
        address=selected_address,
        total_amount=discounted_total,
        payment_method=payment_method,
        coupon=coupon if coupon else None,  # Ensure coupon is passed correctly or None
    )



# Helper function to create order items from cart items
def create_order_items(order, cart_items):
    for cart_item in cart_items:
        variant = cart_item.variant
        quantity = cart_item.quantity

        # Check if the quantity is greater than the stock, and handle accordingly
        if variant.stock < quantity:
            messages.error(f"Sorry, not enough stock for {cart_item.product.title}. Only {variant.stock} left.")
            return

       
        variant.stock -= quantity
        variant.save()

        # Create order items
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            variant=variant,
            quantity=quantity,
            total_amount=cart_item.variant.price * quantity,
        )




def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'user/order_confirmation.html', {'order': order})



@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-placed_at')  # Filter by user
    return_requests = ReturnRequest.objects.filter(user=request.user)

    # Loop through return requests and check for their status
    for return_request in return_requests:
        # If the return request is pending, add a flag to indicate it
        return_request.is_pending = return_request.status == 'Pending'

    
    # Handling search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(Q(id__icontains=search_query) | Q(status__icontains=search_query))

    # Set up pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'user/order_history.html', {'page_obj': page_obj, 'search_query': search_query, 'return_requests': return_requests})



from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from decimal import Decimal

@login_required
def cancel_order(request, order_id):
    try:
        # Fetch the order for the logged-in user with the status 'Pending'
        order = Order.objects.get(id=order_id, user=request.user, status='Pending')
    except Order.DoesNotExist:
        # If no order is found or status is not 'Pending'
        messages.error(request, "No such order exists or the order is not in 'Pending' status.")
        return redirect('core:order_history')  # Redirect to the order history page

    # Check if the order is already canceled
    if order.status == 'Cancelled':
        messages.info(request, "This order has already been canceled.")
        return redirect('core:order_history')  # Redirect to order history page

    # Save the refund amount for later use
    refund_amount = order.total_amount

    # Update order status to 'Cancelled'
    order.status = 'Cancelled'
    order.save()

    # Increment product stock for each order item
    for order_item in order.items.all():
        variant = order_item.variant
        variant.stock += order_item.quantity  # Increment stock by the quantity of items ordered
        variant.save()

    # Check if the payment method is Cash on Delivery (COD)
    if order.payment_method != 'COD':
        # If it's not COD, refund to wallet (for paid orders)
        wallet, created = Wallet.objects.get_or_create(user=request.user)

       
        wallet.balance += Decimal(refund_amount)  # Add the refund amount to the wallet balance
        wallet.save()
       

        # Record the transaction in WalletTransaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='refund',
            amount=Decimal(refund_amount)  # Record the refund transaction
        )

        messages.success(request, f"Order {order.id} has been canceled and ${refund_amount} has been refunded to your wallet.")

    else:
        # Handle the case for COD - no wallet update, but we still acknowledge the cancellation.
        messages.success(request, f"Order {order.id} has been canceled. No refund applied as payment was Cash on Delivery.")

    return redirect('core:order_history')  # Redirect to order history page






@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'Delivered':
        if request.method == 'POST':
            # User submits a return request with a reason
            form = ReturnRequestForm(request.POST)
            if form.is_valid():
                # Create the return request
                return_request = form.save(commit=False)
                return_request.order = order
                return_request.user = request.user
                return_request.save()

                messages.success(request, "Your return request has been submitted and is pending admin approval.")
                return redirect('core:order_history')

        else:
            # If not a POST request, show the return request form
            form = ReturnRequestForm()

        return render(request, 'user/return_order.html', {
            'order': order,
            'form': form
        })
    else:
        messages.error(request, f"Order #{order.id} can only be returned if it is delivered.")
        return redirect('core:order_history')

def list_coupons(request):
    # Filter active and valid coupons

    current_time = timezone.now()
    coupons = Coupon.objects.filter(is_active=True, valid_until__gte=current_time, used=False)
    
    return render(request, 'user/list_coupons.html', {
        'coupons': coupons
    })



@login_required
def user_profile(request):
    # Get the logged-in user and their profile
    user = request.user

     # Check if the user has a profile, if not, create one
    if not hasattr(user, 'profile'):
        # Create a profile if it does not exist
        UserProfile.objects.create(user=user)

    profile = user.profile
    default_address = Address.objects.filter(user=user, is_default=True).first()

    return render(request, 'user/user_profile.html', {
        'user': user,
        'profile': profile,
        'default_address': default_address,

    })


@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('core:user_profile')  # Redirect back to user profile page
    else:
        form = EditProfileForm(instance=profile)

    return render(request, 'user/edit_profile.html', {'form': form})





@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Assign the logged-in user to the address
            address.save()
            return redirect('core:address_view')  # Redirect to user profile or address list
    else:
        form = AddressForm()
    return render(request, 'user/add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        form = EditAddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            # Check if the address is marked as default, and update accordingly
            if address.is_default:
                # If this is the default address, set other addresses to not default
                Address.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)
            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('core:address_view')
    else:
        form = EditAddressForm(instance=address)

    return render(request, 'user/edit_address.html', {'form': form, 'address': address})


@login_required
def delete_address(request, id):
    try:
        # Get the address object using the id
        address = Address.objects.get(id=id)
        # Delete the address
        address.delete()
        messages.success(request, 'Address successfully deleted.')
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')

    return redirect('core:address_view')


def address_view(request):
    return render(request,'user/address_view.html')




def my_profile(request):
    return render(request,'user/my_profile.html')



# @login_required
# def order_history(request):
#     # Fetch all orders for the logged-in user
#     orders = Order.objects.filter(user=request.user).order_by('-placed_at')  # Ordered by most recent first
    
#     return render(request, 'user/order_history.html', {
#         'orders': orders,
#     })


@login_required
def order_detail(request, order_id):
    # Get the order by ID for the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()

    return render(request, 'user/order_detail.html', {
        'order_items': order_items,
        'order': order
    })





# Initialize PayPal SDK
configure_paypal()

def create_payment(request):
    # The payment request will be created here
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://127.0.0.1:8000/payment/execute/",
            "cancel_url": "http://127.0.0.1:8000/payment/cancel/"
        },
        "transactions": [{
            "amount": {
                "total": "10.00",  # Example total amount
                "currency": "USD"
            },
            "description": "Example payment"
        }]
    })

    if payment.create():
        # Payment was successfully created
        approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
        return redirect(approval_url)
    else:
        # Payment creation failed
        return JsonResponse({"error": payment.error}, status=400)




configure_paypal()

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    # Log the payment_id and payer_id for debugging
    print(f"Received Payment ID: {payment_id}")
    print(f"Received Payer ID: {payer_id}")

    # Find the payment by ID
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment was successful
        return render(request, 'user/success.html', {'payment': payment})
    else:
        # Payment execution failed
        return JsonResponse({"error": payment.error}, status=400)


def cancel_payment(request):
    return render(request, 'user/cancel.html')




def payment_success(request):
    return render(request, 'user/success.html')

def payment_failure(request):
    return render(request, 'user/failure.html')




import json
from django.http import JsonResponse
from decimal import Decimal
from .models import Coupon, Order, CustomUser, Cart
def apply_coupon_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated. Please log in.'})

    if request.method == 'POST':
        try:
            # Parse the JSON body from the request
            data = json.loads(request.body)
            print(f"Received Data: {data}")  # Debugging: print received data

            coupon_code = data.get('coupon_code')
            if not coupon_code:
                return JsonResponse({'status': 'error', 'message': 'No coupon code provided!'})

            print(f"Coupon Code Received: {coupon_code}")  # Debugging: print coupon code

            # Try to retrieve the coupon based on the code
            coupon = Coupon.objects.filter(code=coupon_code).first()  # safer than .get()
            if not coupon:
                return JsonResponse({'status': 'error', 'message': 'Invalid coupon code!'})

            # Check if the coupon is valid
            if not coupon.is_valid():
                return JsonResponse({'status': 'error', 'message': 'This coupon is either expired or not valid.'})

            if coupon.used:
                return JsonResponse({'status': 'error', 'message': 'Coupon has already been used.'})

            # Retrieve the custom user object
            user = CustomUser.objects.get(id=request.user.id)

            # Check if the user has any pending orders
            order = Order.objects.filter(user=user, status='Pending').first()

            if not order:
                return JsonResponse({'status': 'error', 'message': 'No active order found! Please create an order first.'})

            # Fetch the cart associated with the user to calculate subtotal
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return JsonResponse({'status': 'error', 'message': 'No cart found for the user!'})

            # Calculate the subtotal based on cart items
            cart_items = cart.items.all()  # Assuming `items` is the related name for cart items in Cart model
            subtotal = Decimal(sum([item.quantity * item.variant.price for item in cart_items]))

            # Calculate the discount based on the subtotal
            discount = (coupon.discount_percentage / 100) * subtotal

            # Update the order total amount after applying the discount
            new_total = subtotal - discount

            # If the discount is greater than the subtotal, we should not apply it (avoiding negative total)
            if new_total < 0:
                return JsonResponse({'status': 'error', 'message': 'Discount is greater than the subtotal. Cannot apply.'})

            # Mark the coupon as used (before applying the discount)
            coupon.used = True
            coupon.save()

            order.total_amount = new_total  # Update the order total amount
            order.coupon = coupon
            order.save()

            # Save the coupon code in the session
            request.session['applied_coupon'] = coupon_code 

            # Return success response with discount details and subtotal
            return JsonResponse({
                'status': 'success',
                'message': f'Coupon {coupon.code} applied successfully!',
                'discount': round(discount, 2),
                'new_total_price': round(order.total_amount, 2),
                'subtotal': round(subtotal, 2)  # Return the subtotal in the response
            })

        except json.JSONDecodeError:
            # Handle invalid JSON format errors
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request.'})

        except Exception as e:
            # Log unexpected errors and return a generic error message
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})



def remove_coupon_user(request):
    # Get the user's active order
    try:
        # Get the user's active order (filter instead of get to handle multiple orders)
        order = Order.objects.filter(user=request.user, status='Pending').first()

        if not order:
            # If no pending order found, return an error
            return JsonResponse({'status': 'error', 'message': 'No active order found.'})

        # Check if there's a coupon applied to the order
        if order.coupon:
            coupon = order.coupon  # Get the coupon from the order

            # Calculate the discount that was applied using the coupon's percentage
            discount = (coupon.discount_percentage / 100) * order.total_amount

            # Restore the order's total amount before the coupon was applied
            order.total_amount += discount  # Add the discount back to the total amount

            # Mark the coupon as unused and remove it from the order
            coupon.used = False
            coupon.save()
            order.coupon = None
            order.save()

            # Return a success response with the updated total price
            return JsonResponse({
                'status': 'success',
                'message': f'Coupon {coupon.code} removed successfully!',
                'new_total_price': round(order.total_amount, 2),  # Correct the total price
                'discount': round(discount, 2),  # Return the discount value too
            })
        else:
            # No coupon applied to this order
            return JsonResponse({'status': 'error', 'message': 'No coupon applied to this order.'})

    except Exception as e:
        # Catch any other unexpected errors and return a generic error message
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})




from django.http import HttpResponse
from .models import Order, OrderItem
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
def download_invoice(request, order_id):
    # Get the order and its associated items
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Retrieve the coupon associated with the order
    coupon = order.coupon  # This assumes the Order model has a field `coupon` that stores the coupon

  

    # Create a response object to serve the PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create a buffer to hold the PDF
    buffer = BytesIO()

    # Set up the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create content for the invoice
    elements = []

    # Get the styles from ReportLab
    styles = getSampleStyleSheet()

    # Add a title for the invoice
    title_style = styles['Title']
    title = Paragraph(f"<b>Invoice for Order #{order.id}</b>", style=title_style)
    elements.append(title)

    # Space after title
    elements.append(Spacer(1, 12))

    # Order Information Section
    order_details = [
        ["Order Date:", order.placed_at.strftime('%Y-%m-%d')],
        ["Total Amount:", f"${order.total_amount:.2f}"],
        ["Payment Method:", order.payment_method],
    ]

    order_table = Table(order_details, colWidths=[150, 350])
    order_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(order_table)

    # Space before the product list
    elements.append(Spacer(1, 24))

    # Product Table Section
    item_table_data = [
        ["Product", "Quantity", "Price", "Total"]
    ]
    
    subtotal = Decimal(0)
    
    # Iterate over each order item to get the details
    for item in order_items:
        item_total = item.variant.price * item.quantity  # Calculate the total for each item
        item_table_data.append([item.product.title, item.quantity, f"${item.variant.price:.2f}", f"${item_total:.2f}"])
        subtotal += item_total  # Add to subtotal

    item_table = Table(item_table_data, colWidths=[200, 100, 100, 100])
    item_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(item_table)

    # Space before the footer
    elements.append(Spacer(1, 24))

    # Calculate the discount
    if coupon:
        # Check if coupon.discount_percentage is valid and greater than 0
        if coupon.discount_percentage > 0:
            discount = (coupon.discount_percentage / 100) * subtotal  # Calculate discount based on coupon percentage
        else:
         
            discount = 0
    else:
      
        discount = 0

 

    # Update the order total after the discount
    final_total = subtotal - discount

    # Now we should set the correct discount and total
    total_details = [
        ["Subtotal", f"${subtotal:.2f}"],
        ["Discount", f"-${discount:.2f}"],
        ["Total Amount", f"${final_total:.2f}"]
    ]

    total_table = Table(total_details, colWidths=[200, 200])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(total_table)

    # Build the PDF
    doc.build(elements)

    # Return the PDF content as an HTTP response
    buffer.seek(0)
    response.write(buffer.getvalue())
    return response
