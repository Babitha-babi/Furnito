from django.contrib import admin
from .models import Wallet, WalletTransaction

# Register Wallet model in the admin interface
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # You can customize which fields to display in the list
    search_fields = ('user__username',)  # Add search functionality based on user name

# Register WalletTransaction model in the admin interface
@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'created_at')  # Customize fields to display
    list_filter = ('transaction_type',)  # Add a filter for transaction types
    search_fields = ('wallet__user__username', 'transaction_type')  # Add search functionality
