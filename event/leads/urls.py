from django.urls import path
from . import views

urlpatterns = [
    path('', views.leads_list_view, name='leads_list'),
    path('contact/<slug:vendor_slug>/', views.lead_create_view, name='lead_create'),
    path('<uuid:lead_id>/', views.lead_detail_view, name='lead_detail'),
    path('<uuid:lead_id>/update-status/', views.lead_update_status, name='lead_update_status'),
    path('<uuid:lead_id>/notes/', views.lead_add_notes, name='lead_add_notes'),
    path('phone-reveal/<slug:vendor_slug>/', views.phone_reveal_view, name='phone_reveal'),
]
