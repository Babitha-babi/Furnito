from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from core.models import Product  # Assuming you have a Product model

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the product is already in the user's wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        # If product is already in wishlist, show a message or just redirect
        return redirect('wishlist:wishlist')  # Redirect to wishlist page
    
    # If not, add it to the wishlist
    Wishlist.objects.create(user=request.user, product=product)
    return redirect('wishlist:wishlist')  # Redirect to wishlist page


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the product is in the user's wishlist
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    if wishlist_item.exists():
        wishlist_item.delete()  # Remove the item from the wishlist
    
    return redirect('wishlist:wishlist')  # Redirect to wishlist page

@login_required
def view_wishlist(request):
    # Assuming the wishlist is associated with the user
    wishlist_items = Wishlist.objects.filter(user=request.user)

    # If wishlist_items contains product instances, fetch products
    # This will depend on how your Wishlist model is structured
    context = {
        'wishlist_items': wishlist_items,
    }

    return render(request, 'user/wishlist.html', context)