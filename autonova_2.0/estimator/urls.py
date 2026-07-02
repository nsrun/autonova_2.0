from django.urls import path
from . import views

urlpatterns = [
    path('', views.estimator_view, name='estimator'),
    path('sparepart/', views.spare_part_estimator_view, name='sparepart_estimator'),
]
