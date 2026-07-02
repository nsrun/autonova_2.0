from django.contrib import admin
from django.utils.html import format_html
from .models import Category, VehicleListing, SparePartListing, ListingImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'slug', 'icon', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category_type']


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    readonly_fields = ['image_preview']
    fields = ['image', 'is_primary', 'image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="60" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Preview'


@admin.register(VehicleListing)
class VehicleListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'brand', 'model', 'year', 'price_inr', 'fuel_type', 'km_driven', 'status', 'created_at']
    list_filter = ['status', 'category', 'fuel_type', 'transmission', 'condition', 'created_at']
    search_fields = ['title', 'brand', 'model', 'seller__username', 'location', 'rto_state']
    list_editable = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    inlines = [ListingImageInline]
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Info', {'fields': ('title', 'slug', 'category', 'brand', 'model', 'variant', 'year', 'color', 'condition', 'description')}),
        ('Vehicle Details', {'fields': ('fuel_type', 'transmission', 'km_driven', 'engine_cc', 'num_owners')}),
        ('Registration & Legal', {'fields': ('rto_state', 'registration_year', 'insurance', 'insurance_valid_until')}),
        ('Pricing & Location', {'fields': ('price', 'is_negotiable', 'location')}),
        ('Status', {'fields': ('seller', 'status', 'rejection_reason')}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def price_inr(self, obj):
        return f"₹{obj.price:,.0f}"
    price_inr.short_description = 'Price'


@admin.register(SparePartListing)
class SparePartListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'part_type', 'compatible_vehicle_type', 'compatible_brand', 'price_inr', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'part_type', 'compatible_vehicle_type', 'condition', 'created_at']
    search_fields = ['title', 'part_name', 'compatible_brand', 'compatible_model', 'seller__username']
    list_editable = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    inlines = [ListingImageInline]

    fieldsets = (
        ('Part Info', {'fields': ('title', 'slug', 'part_name', 'part_number', 'part_type', 'brand', 'condition', 'description')}),
        ('Compatibility', {'fields': ('compatible_vehicle_type', 'compatible_brand', 'compatible_model', 'compatible_year_from', 'compatible_year_to')}),
        ('Stock & Pricing', {'fields': ('quantity', 'price', 'is_negotiable', 'location')}),
        ('Status', {'fields': ('seller', 'status', 'rejection_reason')}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def price_inr(self, obj):
        return f"₹{obj.price:,.0f}"
    price_inr.short_description = 'Price'
