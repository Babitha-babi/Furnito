from core.models import Category,Product,ProductImages,Cart,CartItem,Address

def default(request):
    categories = Category.objects.all()
    return {
        'categories':categories,
    }