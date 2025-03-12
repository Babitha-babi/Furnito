from django.urls import path
from . import views


app_name = 'walletapp'

urlpatterns = [
    path('wallet/',views.wallet,name='wallet'),
    path('add-funds/', views.add_funds, name='add_funds'),# walletapp/urls.py
    path('execute_payment/', views.execute_payment, name='execute_payment'),

]