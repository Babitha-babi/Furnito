import re
from django import forms
from .models import Address,UserProfile

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Special handling for the 'is_default' field to use checkbox style
        self.fields['is_default'].widget.attrs.update({'class': 'form-check-input'})

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('postal_code')
        
        if zip_code and int(zip_code) < 0:
            raise forms.ValidationError("Postal code cannot be negative.")
        
        return zip_code


class EditAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Special handling for the 'is_default' field to use checkbox style
        self.fields['is_default'].widget.attrs.update({'class': 'form-check-input'})


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'birth_date', 'address', 'profile_picture']

        clear_profile_picture = forms.BooleanField(required=False, label="Clear Profile Picture")


    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number:
            # Use regex to validate a phone number with 10 digits
            if not re.match(r'^\d{10}$', phone_number):
                raise forms.ValidationError("Phone number must be a 10-digit number.")
        
        return phone_number
