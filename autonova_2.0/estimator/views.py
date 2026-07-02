from django.shortcuts import render
from .forms import EstimatorForm, SparePartEstimatorForm
from .price_engine import estimate_price
from .sparepart_engine import estimate_spare_part_price


def estimator_view(request):
    form   = EstimatorForm(request.GET or None)
    result = None
    if request.GET and form.is_valid():
        d = form.cleaned_data
        result = estimate_price(
            vehicle_type = d.get('vehicle_type'),
            brand        = d.get('brand'),
            year         = d.get('year'),
            condition    = d.get('condition'),
            km_driven    = d.get('km_driven'),
            model        = d.get('model'),
            fuel_type    = d.get('fuel_type') or 'petrol',
            num_owners   = d.get('num_owners') or '1',
            insurance    = d.get('insurance') or 'third_party',
        )
    return render(request, 'estimator/estimator.html', {
        'form': form, 'result': result, 'active_tab': 'vehicle',
    })


def spare_part_estimator_view(request):
    form   = SparePartEstimatorForm(request.GET or None)
    result = None
    if request.GET and form.is_valid():
        d = form.cleaned_data
        result = estimate_spare_part_price(
            part_type               = d.get('part_type'),
            part_name               = d.get('part_name', ''),
            brand                   = d.get('brand', ''),
            condition               = d.get('condition'),
            compatible_vehicle_type = d.get('compatible_vehicle_type', 'car'),
            compatible_brand        = d.get('compatible_brand', ''),
            quantity                = d.get('quantity') or 1,
        )
    return render(request, 'estimator/sparepart_estimator.html', {
        'form': form, 'result': result, 'active_tab': 'sparepart',
    })