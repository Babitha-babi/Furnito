function addToCart(productId, quantity) {
    fetch("{% url 'core:add_to_cart' product_id=0 %}".replace('0', productId), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            // Show error message (e.g., via an alert or modal)
            alert(data.error);
        } else {
            // Show success message
            showCartPopup(data.message);

            // Update the cart quantity in the icon
            updateCartIcon(data.cart_item_count);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to update the cart icon quantity
function updateCartIcon(cartItemCount) {
    const cartIcon = document.getElementById('cart-quantity');

    // Update the text of the cart icon with the new item count
    cartIcon.innerText = cartItemCount;

    // If you want to hide the count when it's 0, you can add this logic:
    if (cartItemCount === 0) {
        cartIcon.style.display = 'none';  // Hide count if 0
    } else {
        cartIcon.style.display = 'inline';  // Show count if greater than 0
    }
}

// Function to show the cart popup
function showCartPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'cart-popup';
    popup.innerText = message;
    document.body.appendChild(popup);

    setTimeout(() => {
        popup.remove();
    }, 3000); // Remove the popup after 3 seconds
}
