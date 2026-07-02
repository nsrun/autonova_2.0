from .models import Category

def categories_processor(request):
    try:
        vehicle_cats = Category.objects.filter(category_type='vehicle')
        spare_cats = Category.objects.filter(category_type='sparepart')
    except Exception:
        vehicle_cats = []
        spare_cats = []
    return {
        'all_categories': list(vehicle_cats) + list(spare_cats),
        'vehicle_cats': vehicle_cats,
        'spare_cats': spare_cats,
    }
