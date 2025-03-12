from django.urls import path,include
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('', views.adminhome,name='adminhome'),
    path('product_list/', views.product_list, name='product_list'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/images/', views.product_images, name='product_images'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/block/<int:category_id>/', views.block_category, name='block_category'),
    path('categories/unblock/<int:category_id>/', views.unblock_category, name='unblock_category'),

    path('colors/', views.color_list, name='color_list'),
    path('colors/add/', views.add_color, name='add_color'),
    path('colors/edit/<int:color_id>/', views.edit_color, name='edit_color'),
    path('colors/block/<int:color_id>/', views.block_color, name='block_color'),
    path('colors/unblock/<int:color_id>/', views.unblock_color, name='unblock_color'),

    path('sizes/', views.size_list, name='size_list'),
    path('sizes/add/', views.add_size, name='add_size'),
    path('sizes/edit/<int:size_id>/', views.edit_size, name='edit_size'),
    path('sizes/block/<int:size_id>/', views.block_size, name='block_size'),
    path('sizes/unblock/<int:size_id>/', views.unblock_size, name='unblock_size'),

    path('product/<int:product_id>/variants/', views.variant_list, name='variant_list'),
    path('variant/add/<int:product_id>/', views.add_variant, name='add_variant'),
    path('variant/edit/<int:variant_id>/', views.edit_variant, name='edit_variant'),
    path('variants/block/<int:variant_id>/', views.block_variant, name='block_variant'),
    path('variants/unblock/<int:variant_id>/', views.unblock_variant, name='unblock_variant'),


    path('user_list/', views.user_list, name='user_list'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),

     # Order views
    path('orders/', views.order_list, name='order_list'),
    path('orders/change_status/<int:order_id>/', views.change_order_status, name='change_order_status'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
     path('order/<int:order_id>/return/', views.process_return_request, name='process_return_request'),


    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupon/add/', views.add_edit_coupon, name='add_coupon'),
    path('coupon/edit/<int:coupon_id>/', views.add_edit_coupon, name='edit_coupon'),
    path('coupons/block/<int:coupon_id>/', views.block_coupon, name='block_coupon'),
    path('coupons/unblock/<int:coupon_id>/', views.unblock_coupon, name='unblock_coupon'),
    path('coupon/apply/<int:coupon_id>/', views.apply_coupon, name='apply_coupon'),

    path('sales-report/', views.sales_report, name='sales_report'),
    path('sales_report_pdf/', views.sales_report_pdf, name='sales_report_pdf'),
    path('sales_report_excel/', views.sales_report_excel, name='sales_report_excel'),

    path('logout/',views.logout_view,name='logout')
]

