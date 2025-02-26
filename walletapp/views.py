# walletapp/views.py
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import Wallet,WalletTransaction
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def wallet(request):
    # Get or create the user's wallet
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get wallet transactions ordered by the latest first
    wallet_transactions = wallet.transactions.all().order_by('-created_at')

    # Add pagination
    paginator = Paginator(wallet_transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')  # Get the page number from the query string
    page_obj = paginator.get_page(page_number)  # Get the paginated page object

    context = {
        'wallet': wallet,
        'wallet_transactions': page_obj,  # Pass the paginated transactions instead of the entire queryset
    }
    return render(request, 'user/wallet.html', context)




@login_required
def add_funds(request):
    if request.method == 'POST':
        # Get the amount entered by the user
        try:
            amount = Decimal(request.POST.get('amount'))
            
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('walletapp:wallet')
            
            # Get or create the user's wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
            # Add the amount to the wallet balance
            wallet.balance += amount
            wallet.save()
            
            # Create a wallet transaction for the credit
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='credited',  # Type of transaction
            )
            
            # Notify user of successful transaction
            messages.success(request, f"Successfully added ${amount} to your wallet.")
            
        except Exception as e:
            messages.error(request, "An error occurred while adding funds.")
            print(e)

        return redirect('walletapp:wallet')
