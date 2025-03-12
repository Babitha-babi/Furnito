from django.urls import path,include
from . import views
from django.http import HttpResponse

app_name = 'core'

urlpatterns = [
    path('',views.index,name='index'),
    path('product_list/',views.product_list_view,name='product_list'),
    path('product_detail/<pid>',views.product_detail_view,name='product_detail'),

    path('category_list/',views.category_list_view,name='category_list'),
    path('category_list/<cid>',views.category_product_list_view,name='category_product_list'),

    path('search/',views.search_view,name='search'),
    path('get_variant_details/', views.get_variant_details, name='get_variant_details'),


    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),
     path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart-detail/', views.cart_detail, name='cart_detail'),



    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/detail/', views.order_detail, name='order_detail'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return_order/<int:order_id>/', views.return_order, name='return_order'),
    


    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address_view/',views.address_view,name='address_view'),
    path('address/delete/<int:id>/', views.delete_address, name='delete_address'),

    
    path('my_profile/',views.my_profile,name='my_profile'),

    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),


    path('payment/create/<int:order_id>/', views.create_payment, name='create_payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('payment/cancel/', views.cancel_payment, name='cancel_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('favicon.ico', lambda x: HttpResponse(status=204)),


    path('apply-coupon-user/', views.apply_coupon_user, name='apply_coupon_user'),
    path('remove-coupon/', views.remove_coupon_user, name='remove_coupon_user'),
    path('coupons/', views.list_coupons, name='list_coupons'),

    path('order/invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

]
