from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from userauths.models import CustomUser
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import authenticate, login, logout
from .forms import ProductForm,CategoryForm,ColorForm,SizeForm,CouponForm,VariantsForm
from core.models import Product,ProductImages,Category,Order,Color,Size,Coupon,Variants, OrderItem
from .forms import ProductImageFormSet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth, TruncYear
from datetime import datetime
from django.utils import timezone
import json

# Dashboard View
def adminhome(request):
    # Sales data by month or year filter
    filter_type = request.GET.get('filter', 'monthly')  # Monthly by default
    
    # Calculate total sales for the selected period
    if filter_type == 'monthly':
        orders = Order.objects.annotate(month=TruncMonth('placed_at')).values('month').annotate(total_sales=Sum(F('total_amount')))
        sales_data = {order['month'].strftime('%B %Y'): float(order['total_sales']) for order in orders}
    elif filter_type == 'yearly':
        orders = Order.objects.annotate(year=TruncYear('placed_at')).values('year').annotate(total_sales=Sum(F('total_amount')))
        sales_data = {order['year'].strftime('%Y'): float(order['total_sales']) for order in orders}
    else:
        sales_data = {}

    # Best-selling products (top 10)
    best_selling_products = OrderItem.objects.values('product__title') \
        .annotate(total_sales=Sum(F('quantity'))) \
        .order_by('-total_sales')[:10]

    # Best-selling categories (top 10)
    best_selling_categories = OrderItem.objects.values('product__category__title') \
        .annotate(total_sales=Sum(F('quantity'))) \
        .order_by('-total_sales')[:10]

    context = {
        'sales_data': json.dumps(sales_data),
        'best_selling_products': best_selling_products,
        'best_selling_categories': best_selling_categories,
        'filter_type': filter_type,
    }

    return render(request, 'adminapp/adminhome.html', context)



def product_list(request):
    products = Product.objects.all()
    return render(request, 'adminapp/product_list.html', {'products': products})

@login_required
def add_product(request):
    # if not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to view this page.")
    #     return redirect('core:index')

    if request.user.username != 'babitha':
        # If the user is not the allowed user, show a forbidden message and return a forbidden response.
        messages.error(request, "You are not authorized to add products.")
        return HttpResponseForbidden("You are not authorized to add products.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handling file upload (for images)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save yet
            product.user = request.user
            form.save()
            # Handle multiple product images
            product_images = request.FILES.getlist('product_images')  # Get the list of images from the form
            for image in product_images:
                ProductImages.objects.create(product=product, images=image)
            messages.success(request, "Product created successfully!")
            return redirect('adminapp:product_list')  # Redirect to the product list
        else:
            messages.error(request, "Error creating the product. Please try again.")
    else:
        form = ProductForm()

    return render(request, 'adminapp/add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to edit this product.")
        return redirect('core:index')

    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # Use the existing instance to update
        if form.is_valid():
            form.save()
             # Handle multiple image uploads
            product_images = request.FILES.getlist('product_images')
            for image in product_images:
                ProductImages.objects.create(product=product, images=image)
            messages.success(request, f"Product {product.title} updated successfully!")
            return redirect('adminapp:product_list')
        else:
            messages.error(request, "Error updating the product. Please try again.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'adminapp/edit_product.html', {'form': form, 'product': product})



# Image Deletion View (for removing an image)
@csrf_exempt
def remove_product_image(request, image_id):
    if request.method == 'DELETE':
        image = get_object_or_404(ProductImages, id=image_id)
        product = image.product  # Get the associated product
        image.delete()  # Delete the image from the database

        return JsonResponse({'message': 'Image deleted successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    messages.success(request, f"Product {product.title} deleted successfully!")
    return redirect('adminapp:product_list')



@login_required
def product_images(request, product_id):
    product = Product.objects.get(id=product_id)
    
    # If the request method is POST, process the image uploads
    if request.method == 'POST':
        formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.filter(product=product))
        
        if formset.is_valid():
            formset.save()
            messages.success(request, f"Images for {product.title} uploaded successfully.")
            return redirect('adminapp:product_images', product_id=product.id)
        else:
            messages.error(request, "Error uploading images. Please try again.")
    
    else:
        formset = ProductImageFormSet(queryset=ProductImage.objects.filter(product=product))

    return render(request, 'adminpp/product_images.html', {'formset': formset, 'product': product})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_product_image(request, image_id):
    image = ProductImage.objects.get(id=image_id)
    product = image.product
    image.delete()
    messages.success(request, f"Image deleted successfully from {product.title}.")
    return redirect('adminapp:product_images', product_id=product.id)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'adminapp/category_list.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('adminapp:category_list')
    else:
        form = CategoryForm()
    return render(request, 'adminapp/category_form.html', {'form': form})

# Edit category
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('adminapp:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'adminapp/category_form.html', {'form': form})

# Soft delete category
def soft_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete() 
    messages.success(request, f"Category '{category.title}' has been deleted!")
    return redirect('adminapp:category_list')



def color_list(request):
    colors = Color.objects.all()
    return render(request, 'adminapp/color_list.html', {'colors': colors})

def add_color(request):
    if request.method == 'POST':
        form = ColorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Color added successfully!")
            return redirect('adminapp:color_list')
    else:
        form = ColorForm()
    return render(request, 'adminapp/color_form.html', {'form': form})

# Edit color
def edit_color(request, color_id):
    color = get_object_or_404(Color, id=color_id)
    if request.method == 'POST':
        form = ColorForm(request.POST,request.FILES, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, "Color updated successfully!")
            return redirect('adminapp:color_list')
    else:
        form = ColorForm(instance=color)
    return render(request, 'adminapp/color_form.html', {'form': form})

# Soft delete color
def soft_delete_color(request, color_id):
    color = get_object_or_404(Color, id=color_id)
    color.delete() 
    messages.success(request, f"color '{color.name}' has been deleted!")
    return redirect('adminapp:color_list')


# Size
def size_list(request):
    sizes = Size.objects.all()
    return render(request, 'adminapp/size_list.html', {'sizes': sizes})

def add_size(request):
    if request.method == 'POST':
        form = SizeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "size added successfully!")
            return redirect('adminapp:size_list')
    else:
        form = SizeForm()
    return render(request, 'adminapp/size_form.html', {'form': form})

# Edit color
def edit_size(request, size_id):
    size = get_object_or_404(Size, id=size_id)
    if request.method == 'POST':
        form = SizeForm(request.POST,request.FILES, instance=size)
        if form.is_valid():
            form.save()
            messages.success(request, "size updated successfully!")
            return redirect('adminapp:size_list')
    else:
        form = SizeForm(instance=size)
    return render(request, 'adminapp/size_form.html', {'form': form})

# Soft delete color
def soft_delete_size(request, size_id):
    size = get_object_or_404(Size, id=size_id)
    size.delete() 
    messages.success(request, f"size '{size.name}' has been deleted!")
    return redirect('adminapp:size_list')


# List users for admin
@login_required
def user_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    users = CustomUser.objects.all()  # Fetching all users
    return render(request, 'adminapp/user_list.html', {'users': users})

# Block user
@login_required
def block_user(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to block users.")
    
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_superuser:
        messages.error(request, "You cannot block an admin user.")
        return redirect('adminapp:user_list')
    user.is_blocked = True
    user.save()

    messages.success(request, f"User {user.email} has been blocked.")
    return redirect('adminapp:user_list')

# Unblock user
@login_required
def unblock_user(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to unblock users.")
    
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = False
    user.save()

    messages.success(request, f"User {user.email} has been unblocked.")
    return redirect('adminapp:user_list')



def logout_view(request):
    logout(request)
    messages.success(request,'you logged out')
    return redirect('core:index')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def order_list(request):
    # List all orders, ordered by when they were placed
    orders = Order.objects.all().order_by('-placed_at')
    for order in orders:
        # Add a flag indicating if the order can be cancelled
        order.can_be_cancelled = order.status in ['Pending', 'Shipped']
    return render(request, 'adminapp/order_list.html', {'orders': orders})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Get the status choices from the field definition
    status_choices = dict(Order._meta.get_field('status').choices)

     # Prevent status change if the order is cancelled
    if order.status == 'Cancelled':
        messages.error(request, f"Order #{order.id} is already cancelled and cannot be modified.")
        return redirect('adminapp:order_list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Check if the new status is in the available choices
        if new_status in status_choices:
            # Handle logic for each status change
            if new_status == 'Cancelled' and order.status in ['Shipped', 'Delivered']:
                messages.error(request, "You can't cancel a delivered or shipped order.")
            elif new_status == 'Returned' and order.status != 'Delivered':
                messages.error(request, "Only delivered orders can be returned.")
            else:
                order.status = new_status
                order.save()
                messages.success(request, f"Order #{order.id} status changed to {status_choices[new_status]}.")
        else:
            messages.error(request, "Invalid status.")

    
    return redirect('adminapp:order_list')  

@login_required
@user_passes_test(lambda u: u.is_superuser)
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if the order can be cancelled (only orders that are 'Pending' or 'Shipped' can be cancelled)
    if order.status in ['Pending', 'Shipped']:
        for item in order.order_items.all():
            product = item.product
            product.stock += item.quantity  # Increment the stock by the quantity of the product
            product.save()
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
    else:
        messages.error(request, f"Order #{order.id} cannot be cancelled because it is already {order.get_status_display()}.")
    
    return redirect('adminapp:order_list')



# View for adding or editing a coupon
def add_edit_coupon(request, coupon_id=None):
    if coupon_id:
        coupon = Coupon.objects.get(id=coupon_id)
    else:
        coupon = None
    
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon saved successfully.')
            return redirect('adminapp:coupon_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'adminapp/add_edit_coupon.html', {'form': form, 'coupon': coupon})

# View for listing all coupons
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'adminapp/coupon_list.html', {'coupons': coupons})

# View to delete a coupon
def delete_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully.')
    return redirect('adminapp:coupon_list')

# View to apply a coupon to orders (example placeholder)
def apply_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    # Apply coupon logic to orders, cart, etc.
    messages.success(request, f'Coupon {coupon.code} applied to orders successfully.')
    return redirect('adminapp:coupon_list')



def variant_list(request, product_id):
    # Fetch the product using the provided product_id
    product = get_object_or_404(Product, id=product_id)
    
    # Fetch variants for this product
    variants = Variants.objects.filter(product=product)

    return render(request, 'adminapp/variant_list.html', {'product': product, 'variants': variants})


def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = VariantsForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product  # Associate the variant with the product
            variant.save()
            messages.success(request, "Variant added successfully!")
            return redirect('adminapp:variant_list', product_id=product.id)
    else:
        form = VariantsForm()

    return render(request, 'adminapp/add_variant.html', {'form': form, 'product': product})

def edit_variant(request, variant_id):
    # Fetch the variant by ID
    variant = get_object_or_404(Variants, id=variant_id)

    if request.method == 'POST':
        form = VariantsForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, "Variant updated successfully!")
            return redirect('adminapp:variant_list', product_id=variant.product.id)
    else:
        form = VariantsForm(instance=variant)

    return render(request, 'adminapp/edit_variant.html', {'form': form, 'variant': variant})

def delete_variant(request, variant_id):
    # Fetch the variant by ID
    variant = get_object_or_404(Variants, id=variant_id)
    product_id = variant.product.id  # Save the product ID to redirect after deletion

    if request.method == 'POST':
        variant.delete()
        messages.success(request, "Variant deleted successfully!")
        return redirect('adminapp:variant_list', product_id=product_id)

    return render(request, 'adminapp/confirm_delete_variant.html', {'variant': variant})


import datetime
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone



def sales_report(request):
    today = timezone.now()
    start_date = None
    end_date = None
    sales_count = 0
    total_sales = 0
    total_discount = 0

    # Handle different date filters
    if request.method == 'POST':
        report_type = request.POST.get('report_type')  # Daily, Weekly, Monthly, Custom
        if report_type == 'daily':
            start_date = today - datetime.timedelta(days=1)
            end_date = today
        elif report_type == 'weekly':
            start_date = today - datetime.timedelta(weeks=1)
            end_date = today
        elif report_type == 'monthly':
            start_date = today - datetime.timedelta(weeks=4)
            end_date = today
        elif report_type == 'yearly':
            start_date = today - datetime.timedelta(weeks=52)
            end_date = today
        elif report_type == 'custom':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)

        # Fetch orders within the selected date range
        orders = Order.objects.filter(placed_at__range=[start_date, end_date])

        # Calculate sales count, total sales, total discount, and total order amounts
        sales_count = orders.count()
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_discount = orders.filter(coupon__isnull=False).aggregate(Sum('coupon__discount_percentage'))['coupon__discount_percentage__sum'] or 0

    return render(request, 'adminapp/sales_report.html', {
        'sales_count': sales_count,
        'total_sales': total_sales,
        'total_discount': total_discount,
    })



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
def sales_report_pdf(request):
    # Fetch the date range for the report
    report_type = request.GET.get('report_type', 'daily')
    start_date = None
    end_date = timezone.now().date()

    # Determine the date range based on the report type
    if report_type == 'daily':
        start_date = timezone.now().date()
    elif report_type == 'weekly':
        start_date = timezone.now() - timezone.timedelta(weeks=1)
    elif report_type == 'monthly':
        start_date = timezone.now() - timezone.timedelta(days=30)
    elif report_type == 'yearly':
        start_date = timezone.now() - timezone.timedelta(days=365)
    elif report_type == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            start_date = timezone.make_aware(datetime.strptime(start_date_str, "%Y-%m-%d"))
            end_date = timezone.make_aware(datetime.strptime(end_date_str, "%Y-%m-%d"))

    # Adjust the end_date to the end of the day if not custom
    if report_type != 'custom':
        end_date = timezone.now().date()  # Make sure end_date is today's date for non-custom reports
    end_date = timezone.datetime.combine(end_date, timezone.datetime.max.time()).replace(tzinfo=timezone.utc)  # Set time to the last moment of the day
    
    # Fetch orders within the date range
    orders = Order.objects.filter(placed_at__range=[start_date, end_date])

    sales_count = orders.count()
    total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_discount = orders.filter(coupon__isnull=False).aggregate(Sum('coupon__discount_percentage'))['coupon__discount_percentage__sum'] or 0

    # Render the HTML to a string for the PDF
    html_content = render_to_string('adminapp/pdf_sales_report.html', {
        'orders': orders,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'sales_count': sales_count,
        'start_date': start_date,
        'end_date': end_date,
    })

    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Use xhtml2pdf to convert HTML to PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=buffer)

    # Check if PDF creation was successful
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    # Write the generated PDF to the response
    response.write(buffer.getvalue())
    return response

from openpyxl import Workbook
from django.http import HttpResponse
from django.utils import timezone

def sales_report_excel(request):
    # Fetch the date range for the report
    report_type = request.GET.get('report_type', 'daily')
    start_date = None
    end_date = timezone.now().date()

    # Determine the date range based on the report type
    if report_type == 'daily':
        start_date = timezone.now().date()
    elif report_type == 'weekly':
        start_date = timezone.now() - timezone.timedelta(weeks=1)
    elif report_type == 'monthly':
        start_date = timezone.now() - timezone.timedelta(days=30)
    elif report_type == 'yearly':
        start_date = timezone.now() - timezone.timedelta(days=365)
    elif report_type == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                start_date = end_date = timezone.now().date()  # Default to today's date if invalid

    # Adjust the end_date to the end of the day for proper comparison
    if report_type != 'custom':
        end_date = timezone.now().date()  # Make sure end_date is today's date for non-custom reports
    end_date = timezone.datetime.combine(end_date, timezone.datetime.max.time()).replace(tzinfo=None)  # Set time to the last moment of the day, and remove tzinfo

    # Fetch orders within the date range
    orders = Order.objects.filter(placed_at__range=[start_date, end_date])

    # Calculate totals
    sales_count = orders.count()
    total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_discount = orders.filter(coupon__isnull=False).aggregate(Sum('coupon__discount_percentage'))['coupon__discount_percentage__sum'] or 0

    # Create an Excel file with openpyxl
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    # Write headers
    ws.append(["Order ID", "User", "Total Amount", "Discount Applied", "Status", "Payment Method", "Placed At"])

    # Write order data
    for order in orders:
        # Convert placed_at to naive datetime (if timezone-aware)
        placed_at = order.placed_at
        if placed_at.tzinfo is not None:
            placed_at = placed_at.replace(tzinfo=None)

        # Assuming apply_discount is a method on Order model that calculates discount
        discount = order.apply_discount()  # Ensure this method is defined on the Order model
        ws.append([order.id, order.user.username, order.total_amount, discount, order.status, order.payment_method, placed_at])

    # Add summary row
    ws.append(["", "", "Total Sales", total_sales, "Total Discount", total_discount, "Sales Count", sales_count])

    # Create the response to send the Excel file
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=sales_report.xlsx"
    wb.save(response)

    return response





