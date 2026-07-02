from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import VehicleListing, SparePartListing, ListingImage, Category
from .forms import VehicleListingForm, SparePartForm, SearchForm


def home_view(request):
    recent_vehicles = VehicleListing.objects.filter(status='approved').order_by('-created_at')[:8]
    recent_parts = SparePartListing.objects.filter(status='approved').order_by('-created_at')[:4]
    vehicle_cats = Category.objects.filter(category_type='vehicle')
    spare_cats = Category.objects.filter(category_type='sparepart')
    total_vehicles = VehicleListing.objects.filter(status='approved').count()
    total_parts = SparePartListing.objects.filter(status='approved').count()
    return render(request, 'listings/home.html', {
        'recent_vehicles': recent_vehicles,
        'recent_parts': recent_parts,
        'vehicle_cats': vehicle_cats,
        'spare_cats': spare_cats,
        'total_vehicles': total_vehicles,
        'total_parts': total_parts,
        'search_form': SearchForm(),
    })


def browse_view(request):
    form = SearchForm(request.GET)
    listing_type = request.GET.get('listing_type', '')
    vehicles = VehicleListing.objects.filter(status='approved')
    parts = SparePartListing.objects.filter(status='approved')

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        location = form.cleaned_data.get('location')
        fuel_type = form.cleaned_data.get('fuel_type')
        max_km = form.cleaned_data.get('max_km')

        if query:
            vehicles = vehicles.filter(Q(title__icontains=query) | Q(brand__icontains=query) | Q(model__icontains=query))
            parts = parts.filter(Q(title__icontains=query) | Q(part_name__icontains=query) | Q(compatible_brand__icontains=query))
        if category:
            vehicles = vehicles.filter(category=category)
            parts = parts.filter(category=category)
        if min_price:
            vehicles = vehicles.filter(price__gte=min_price)
            parts = parts.filter(price__gte=min_price)
        if max_price:
            vehicles = vehicles.filter(price__lte=max_price)
            parts = parts.filter(price__lte=max_price)
        if location:
            vehicles = vehicles.filter(location__icontains=location)
            parts = parts.filter(location__icontains=location)
        if fuel_type:
            vehicles = vehicles.filter(fuel_type=fuel_type)
        if max_km:
            vehicles = vehicles.filter(km_driven__lte=max_km)

    if listing_type == 'vehicle':
        parts = SparePartListing.objects.none()
    elif listing_type == 'sparepart':
        vehicles = VehicleListing.objects.none()

    total_results = vehicles.count() + parts.count()
    paginator_v = Paginator(vehicles, 9)
    paginator_p = Paginator(parts, 9)
    page = request.GET.get('page', 1)
    page_vehicles = paginator_v.get_page(page)
    page_parts = paginator_p.get_page(page)

    return render(request, 'listings/browse.html', {
        'page_vehicles': page_vehicles,
        'page_parts': page_parts,
        'form': form,
        'total_results': total_results,
        'listing_type': listing_type,
    })


def vehicle_detail_view(request, slug):
    listing = get_object_or_404(VehicleListing, slug=slug, status='approved')
    related = VehicleListing.objects.filter(category=listing.category, status='approved').exclude(pk=listing.pk)[:4]
    return render(request, 'listings/vehicle_detail.html', {'listing': listing, 'related': related})


def part_detail_view(request, slug):
    listing = get_object_or_404(SparePartListing, slug=slug, status='approved')
    related = SparePartListing.objects.filter(category=listing.category, status='approved').exclude(pk=listing.pk)[:4]
    return render(request, 'listings/part_detail.html', {'listing': listing, 'related': related})


@login_required
def sell_choose_view(request):
    return render(request, 'listings/sell_choose.html')


@login_required
def sell_vehicle_view(request):
    if request.method == 'POST':
        form = VehicleListingForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.status = 'pending'
            listing.save()
            for i, img in enumerate(images):
                ListingImage.objects.create(vehicle=listing, image=img, is_primary=(i == 0))
            messages.success(request, '🎉 Vehicle listed! It will go live after admin approval.')
            return redirect('dashboard')
    else:
        form = VehicleListingForm()
    return render(request, 'listings/sell_vehicle.html', {'form': form})


@login_required
def sell_part_view(request):
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.status = 'pending'
            listing.save()
            for i, img in enumerate(images):
                ListingImage.objects.create(spare_part=listing, image=img, is_primary=(i == 0))
            messages.success(request, '🎉 Spare part listed! It will go live after admin approval.')
            return redirect('dashboard')
    else:
        form = SparePartForm()
    return render(request, 'listings/sell_part.html', {'form': form})


@login_required
def edit_vehicle_view(request, slug):
    listing = get_object_or_404(VehicleListing, slug=slug, seller=request.user)
    if request.method == 'POST':
        form = VehicleListingForm(request.POST, instance=listing)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.status = 'pending'
            listing.save()
            for img in images:
                ListingImage.objects.create(vehicle=listing, image=img)
            messages.success(request, 'Listing updated and resubmitted for approval.')
            return redirect('dashboard')
    else:
        form = VehicleListingForm(instance=listing)
    return render(request, 'listings/edit_vehicle.html', {'form': form, 'listing': listing})


@login_required
def edit_part_view(request, slug):
    listing = get_object_or_404(SparePartListing, slug=slug, seller=request.user)
    if request.method == 'POST':
        form = SparePartForm(request.POST, instance=listing)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.status = 'pending'
            listing.save()
            for img in images:
                ListingImage.objects.create(spare_part=listing, image=img)
            messages.success(request, 'Part listing updated and resubmitted.')
            return redirect('dashboard')
    else:
        form = SparePartForm(instance=listing)
    return render(request, 'listings/edit_part.html', {'form': form, 'listing': listing})


@login_required
def delete_vehicle_view(request, slug):
    listing = get_object_or_404(VehicleListing, slug=slug, seller=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Vehicle listing deleted.')
        return redirect('dashboard')
    return render(request, 'listings/delete_confirm.html', {'listing': listing})


@login_required
def delete_part_view(request, slug):
    listing = get_object_or_404(SparePartListing, slug=slug, seller=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Spare part listing deleted.')
        return redirect('dashboard')
    return render(request, 'listings/delete_confirm.html', {'listing': listing})


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if category.category_type == 'vehicle':
        listings = VehicleListing.objects.filter(category=category, status='approved')
        listing_type = 'vehicle'
    else:
        listings = SparePartListing.objects.filter(category=category, status='approved')
        listing_type = 'sparepart'
    paginator = Paginator(listings, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'listings/category.html', {
        'category': category,
        'page_obj': page_obj,
        'listing_type': listing_type,
    })
