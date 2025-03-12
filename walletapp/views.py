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




import paypalrestsdk
from decimal import Decimal
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from walletapp.models import Wallet, WalletTransaction

# Assuming you've already set up PayPal SDK configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # or "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@login_required
def add_funds(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount'))

            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('walletapp:wallet')
            
            # Create PayPal payment for adding funds
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": "USD"
                    },
                    "description": "Add funds to wallet"
                }],
                "redirect_urls": {
                    "return_url": request.build_absolute_uri('/wallet/execute_payment/'),
                    "cancel_url": request.build_absolute_uri('/wallet/cancel_payment/')
                }
            })

            if payment.create():
                # Redirect the user to PayPal for approval
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return redirect(approval_url)
            else:
                messages.error(request, "Payment creation failed. Please try again.")
        except Exception as e:
            messages.error(request, "An error occurred while adding funds.")
            print(e)

    return render(request, 'walletapp/add_funds.html')


@login_required
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        try:
            # Add the funds to the wallet
            amount = Decimal(payment.transactions[0].amount.total)
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += amount
            wallet.save()

            # Record the transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='credited'
            )

           
            return redirect('walletapp:wallet')
        except Exception as e:
            messages.error(request, "An error occurred while processing your payment.")
            print(e)
    else:
        messages.error(request, "Payment execution failed.")
        return redirect('walletapp:wallet')

