from django.urls import path
from . import views

urlpatterns = [
    path('add/<slug:vendor_slug>/', views.review_create_view, name='review_create'),
    path('<uuid:review_id>/edit/', views.review_update_view, name='review_update'),
    path('<uuid:review_id>/delete/', views.review_delete_view, name='review_delete'),
]
