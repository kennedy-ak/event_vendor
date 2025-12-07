from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_list_view, name='vendor_list'),
    path('dashboard/', views.vendor_dashboard_view, name='vendor_dashboard'),
    path('create/', views.vendor_create_view, name='vendor_create'),
    path('category/<slug:slug>/', views.category_view, name='category_vendors'),
    path('stories/', views.success_stories_list_view, name='success_stories_list'),
    path('stories/create/', views.success_story_create_view, name='success_story_create'),
    path('<slug:slug>/', views.vendor_detail_view, name='vendor_detail'),
    path('<slug:slug>/edit/', views.vendor_update_view, name='vendor_update'),
]
