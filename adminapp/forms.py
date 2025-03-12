from django import forms
from core.models import Product, Category,ProductImages, Variants, Size, Color,Coupon
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'category', 'image', 'description', 'price', 'old_price',
            'specifications', 'variant', 'product_status', 'in_stock', 'max_quantity_per_user'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control'}),
            'variant': forms.Select(choices=Product.VARIANTS, attrs={'class': 'form-control'}),
            'product_status': forms.Select(choices=Product.STATUS_CHOICE, attrs={'class': 'form-control'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'max_quantity_per_user': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ['images', ]
        widgets = {
            'images': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

# Formset for managing multiple product images (extra=1 allows for adding 1 extra image field initially)
ProductImageFormSet = modelformset_factory(ProductImages, form=ProductImageForm, extra=1)

class VariantsForm(forms.ModelForm):
    class Meta:
        model = Variants
        fields = ['product', 'size', 'color', 'stock', 'price', 'image_id']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Adjust this depending on how the image_id is managed.
        }

        def clean_stock(self):
            stock = self.cleaned_data.get('stock')
            if stock < 0:
                raise forms.ValidationError("Stock cannot be negative.")
            return stock

        def save(self, commit=True):
        # Save the variant first
            variant = super().save(commit=False)

            # If it's a new variant or updated, we update the product stock
            if commit:
                variant.save()

                # After saving the variant, we update the product stock
                # Calculate the total stock for this product
                total_stock = Variants.objects.filter(product=variant.product).aggregate(total_stock=models.Sum('stock'))['total_stock'] or 0

                # Update the product's stock with the total stock from all variants
                product = variant.product
                product.stock = total_stock
                product.save()

            return variant
        
        def delete(self, *args, **kwargs):
            # Get the product before deleting the variant
            product = self.product

            # Delete the variant
            super().delete(*args, **kwargs)

            # After deleting, recalculate and update the product's stock
            total_stock = Variants.objects.filter(product=product).aggregate(total_stock=models.Sum('stock'))['total_stock'] or 0
            product.stock = total_stock
            product.save()


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'image', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter Category Title',
                'class': 'form-control',
                'id': 'category-title'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'id': 'category-image'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Provide a short description of the category',
                'class': 'form-control',
                'rows': 4,
                'id': 'category-description'
            }),
        }


from django.utils import timezone

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'valid_from', 'valid_until']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get("valid_from")
        valid_until = cleaned_data.get("valid_until")
        discount_percentage = cleaned_data.get("discount_percentage")

        # Ensure valid_from is aware (has timezone information)
        if valid_from and valid_from.tzinfo is None:
            valid_from = timezone.make_aware(valid_from)

        # Validate that valid_from is before valid_until
        if valid_from and valid_until and valid_from >= valid_until:
            raise ValidationError("The start date must be before the end date.")

        # Validate that valid_from is not in the past
        if valid_from and valid_from < timezone.now():
            raise ValidationError("The start date cannot be in the past.")

        # Validate the discount percentage
        if discount_percentage is not None:
            if discount_percentage < 0 or discount_percentage > 70:
                raise ValidationError("Discount percentage must be between 0 and 70.")

        return cleaned_data
