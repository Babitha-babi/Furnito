# In signals.py (or wherever you're handling signals)
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserProfile

# Ensure a UserProfile is created for every user on signup
@receiver(user_signed_up)
def create_user_profile(sender, request, user, **kwargs):
    UserProfile.objects.get_or_create(user=user)
