from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('browse/', views.browse_view, name='browse'),

    # Sell
    path('sell/', views.sell_choose_view, name='sell_choose'),
    path('sell/vehicle/', views.sell_vehicle_view, name='sell_vehicle'),
    path('sell/part/', views.sell_part_view, name='sell_part'),

    # Vehicle listings
    path('vehicle/<slug:slug>/', views.vehicle_detail_view, name='vehicle_detail'),
    path('vehicle/<slug:slug>/edit/', views.edit_vehicle_view, name='edit_vehicle'),
    path('vehicle/<slug:slug>/delete/', views.delete_vehicle_view, name='delete_vehicle'),

    # Spare part listings
    path('part/<slug:slug>/', views.part_detail_view, name='part_detail'),
    path('part/<slug:slug>/edit/', views.edit_part_view, name='edit_part'),
    path('part/<slug:slug>/delete/', views.delete_part_view, name='delete_part'),

    # Category
    path('category/<slug:slug>/', views.category_view, name='category'),
]
