
    $(document).ready(function() {
        // Example of using jQuery
        $("#add-to-cart-btn").on("click", function() {
            let this_val = $(this);
            let index = this_val.attr("data-index");
            let quantity = $("#product-quantity-"+_index).val();
            let product_title = $(".product-title-"+_index).val();
            let product_pid = $(".product-pid-"+_index).val();
            let product_image = $(".product-image-"+_index).val();
            let product_id = $(".product-id-"+_index).val();
            let product_price = $("#current-product-price-"+_index).text();
            

            console.log("Quantity:", quantity);
            console.log("Title:", product_title);
            console.log("Price:", product_price);
            console.log("ID:", product_id);
            console.log("PID:", product_pid);
            console.log("Image:", product_image);
            console.log("Index:", index);
            console.log("Current Element:", this_val);

            // Send the data to the server via AJAX
            $.ajax({
                url: "/add-to-cart",  // Your Django URL for adding to cart
                
                data: {
                    'id': product_id,
                    'qty': quantity,
                    'pid':product_pid,
                    'image':product_image,
                    'title': product_title,
                    'price' : product_price,
                },
                dataType:'JSON',
                beforeSend:function(){
                 console.log("Adding product to cart");
                },
                success: function(res) {
                    this_val.html("item added to cart")
                    console.log("Added product to cart")
                    $("#cart-quantity").text(response.totalcartitems)
                },
               
            });
        });
    });
