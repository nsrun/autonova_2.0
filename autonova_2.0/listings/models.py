from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('vehicle', 'Vehicle'),
        ('sparepart', 'Spare Part'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=60, default='bi-tag')
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default='vehicle')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VehicleListing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Brand New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'For Parts / Not Running'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    ]
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
        ('na', 'N/A'),
    ]
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('semi_auto', 'Semi-Automatic'),
        ('na', 'N/A'),
    ]
    OWNER_CHOICES = [
        ('1', '1st Owner'),
        ('2', '2nd Owner'),
        ('3', '3rd Owner'),
        ('4', '4th Owner or more'),
    ]
    INSURANCE_CHOICES = [
        ('comprehensive', 'Comprehensive'),
        ('third_party', 'Third Party'),
        ('expired', 'Expired'),
        ('none', 'None'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_listings')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='vehicle_listings')

    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    description = models.TextField()

    # Vehicle Specifics
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual')
    km_driven = models.PositiveIntegerField(help_text='Kilometers driven', default=0)
    engine_cc = models.PositiveIntegerField(null=True, blank=True, help_text='Engine capacity in CC')
    num_owners = models.CharField(max_length=5, choices=OWNER_CHOICES, default='1')
    color = models.CharField(max_length=50, blank=True)

    # Registration & Legal
    rto_state = models.CharField(max_length=100, blank=True, help_text='Registration state e.g. MH, TN')
    registration_year = models.PositiveIntegerField(null=True, blank=True)
    insurance = models.CharField(max_length=20, choices=INSURANCE_CHOICES, default='third_party')
    insurance_valid_until = models.DateField(null=True, blank=True)

    # Pricing & Location
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_negotiable = models.BooleanField(default=True)
    location = models.CharField(max_length=150)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while VehicleListing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    def get_condition_badge(self):
        badges = {'new': 'success', 'like_new': 'info', 'good': 'primary', 'fair': 'warning', 'poor': 'danger'}
        return badges.get(self.condition, 'secondary')


class SparePartListing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Brand New'),
        ('oem', 'OEM / Original'),
        ('used_good', 'Used - Good Condition'),
        ('used_fair', 'Used - Fair Condition'),
        ('refurbished', 'Refurbished'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    ]
    PART_TYPE_CHOICES = [
        ('engine', 'Engine Parts'),
        ('body', 'Body Parts'),
        ('electrical', 'Electrical & Electronics'),
        ('suspension', 'Suspension & Steering'),
        ('brakes', 'Brakes'),
        ('transmission', 'Transmission & Gearbox'),
        ('exhaust', 'Exhaust System'),
        ('tyres', 'Tyres & Wheels'),
        ('interior', 'Interior & Accessories'),
        ('lights', 'Lights & Indicators'),
        ('battery', 'Battery & Charging'),
        ('filters', 'Filters & Fluids'),
        ('other', 'Other'),
    ]
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('bike', 'Bike / Scooter'),
        ('truck', 'Truck / Commercial'),
        ('tractor', 'Tractor / Farm'),
        ('universal', 'Universal / All Vehicles'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sparepart_listings')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='sparepart_listings')

    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    part_name = models.CharField(max_length=150, help_text='e.g. Brake Pad, Alternator, Headlight')
    part_number = models.CharField(max_length=100, blank=True, help_text='OEM / manufacturer part number')
    part_type = models.CharField(max_length=30, choices=PART_TYPE_CHOICES, default='engine')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='used_good')
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True, help_text='Part brand / manufacturer')

    # Compatibility
    compatible_vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='car')
    compatible_brand = models.CharField(max_length=100, blank=True, help_text='e.g. Maruti, Honda')
    compatible_model = models.CharField(max_length=100, blank=True, help_text='e.g. Swift, City')
    compatible_year_from = models.PositiveIntegerField(null=True, blank=True)
    compatible_year_to = models.PositiveIntegerField(null=True, blank=True)

    # Stock
    quantity = models.PositiveIntegerField(default=1)

    # Pricing & Location
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_negotiable = models.BooleanField(default=False)
    location = models.CharField(max_length=150)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while SparePartListing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    def get_condition_badge(self):
        badges = {'new': 'success', 'oem': 'info', 'used_good': 'primary', 'used_fair': 'warning', 'refurbished': 'secondary'}
        return badges.get(self.condition, 'secondary')


class ListingImage(models.Model):
    vehicle = models.ForeignKey(VehicleListing, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    spare_part = models.ForeignKey(SparePartListing, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    image = models.ImageField(upload_to='listings/%Y/%m/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Image"
