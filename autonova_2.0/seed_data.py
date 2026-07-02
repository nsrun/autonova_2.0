"""
AutoNova Seed Data Script
Run from Django shell: exec(open('seed_data.py').read())
Or as: python manage.py shell < seed_data.py
"""

from listings.models import Category

print("Seeding AutoNova categories...")

# Vehicle Categories
vehicle_categories = [
    ('Cars', 'cars', 'bi-car-front-fill', 'vehicle', 1),
    ('Bikes & Scooters', 'bikes-scooters', 'bi-bicycle', 'vehicle', 2),
    ('Trucks & Commercial', 'trucks-commercial', 'bi-truck', 'vehicle', 3),
    ('Tractors & Farm', 'tractors-farm', 'bi-tree', 'vehicle', 4),
    ('Luxury & Vintage', 'luxury-vintage', 'bi-gem', 'vehicle', 5),
    ('Electric Vehicles', 'electric-vehicles', 'bi-lightning-charge', 'vehicle', 6),
]

# Spare Part Categories
spare_categories = [
    ('Engine Parts', 'engine-parts', 'bi-gear-wide', 'sparepart', 10),
    ('Body Parts', 'body-parts', 'bi-car-front', 'sparepart', 11),
    ('Tyres & Wheels', 'tyres-wheels', 'bi-circle', 'sparepart', 12),
    ('Batteries & Electrical', 'batteries-electrical', 'bi-battery-charging', 'sparepart', 13),
    ('Brakes & Suspension', 'brakes-suspension', 'bi-shield-check', 'sparepart', 14),
    ('Lights & Indicators', 'lights-indicators', 'bi-lightbulb', 'sparepart', 15),
    ('Interior & Accessories', 'interior-accessories', 'bi-stars', 'sparepart', 16),
    ('Filters & Fluids', 'filters-fluids', 'bi-droplet', 'sparepart', 17),
    ('Exhaust & Cooling', 'exhaust-cooling', 'bi-wind', 'sparepart', 18),
    ('Bike Parts', 'bike-parts', 'bi-bicycle', 'sparepart', 19),
]

all_categories = vehicle_categories + spare_categories
created_count = 0
updated_count = 0

for name, slug, icon, cat_type, order in all_categories:
    obj, created = Category.objects.update_or_create(
        slug=slug,
        defaults={
            'name': name,
            'icon': icon,
            'category_type': cat_type,
            'order': order,
        }
    )
    if created:
        created_count += 1
        print(f"  ✅ Created: {name} ({cat_type})")
    else:
        updated_count += 1
        print(f"  🔄 Updated: {name} ({cat_type})")

print(f"\nDone! Created: {created_count}, Updated: {updated_count}")
print(f"Total categories: {Category.objects.count()}")
print(f"  Vehicle: {Category.objects.filter(category_type='vehicle').count()}")
print(f"  Spare Parts: {Category.objects.filter(category_type='sparepart').count()}")
