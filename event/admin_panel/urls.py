from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # User Management
    path('users/', views.users_list_view, name='users_list'),
    path('users/<uuid:user_id>/', views.user_detail_view, name='user_detail'),
    path('users/<uuid:user_id>/toggle-status/', views.user_toggle_status_view, name='user_toggle_status'),
    path('users/<uuid:user_id>/change-role/', views.user_change_role_view, name='user_change_role'),

    # Vendor Management
    path('vendors/', views.vendors_list_view, name='vendors_list'),
    path('vendors/create/', views.vendor_create_view, name='vendor_create'),
    path('vendors/pending/', views.vendors_pending_view, name='vendors_pending'),
    path('vendors/<uuid:vendor_id>/', views.vendor_detail_view, name='vendor_detail'),
    path('vendors/<uuid:vendor_id>/edit/', views.vendor_edit_view, name='vendor_edit'),
    path('vendors/<uuid:vendor_id>/delete/', views.vendor_delete_view, name='vendor_delete'),
    path('vendors/<uuid:vendor_id>/approve/', views.vendor_approve_view, name='vendor_approve'),
    path('vendors/<uuid:vendor_id>/suspend/', views.vendor_suspend_view, name='vendor_suspend'),
    path('vendors/<uuid:vendor_id>/verify/', views.vendor_verify_view, name='vendor_verify'),

    # Category Management
    path('categories/', views.categories_list_view, name='categories_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<uuid:category_id>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<uuid:category_id>/delete/', views.category_delete_view, name='category_delete'),

    # Billing & Subscriptions
    path('billing/', views.billing_overview_view, name='billing_overview'),
    path('billing/subscriptions/', views.subscriptions_list_view, name='subscriptions_list'),
    path('billing/boosts/', views.boosts_list_view, name='boosts_list'),

    # Leads Management
    path('leads/', views.leads_list_view, name='leads_list'),
    path('leads/analytics/', views.leads_analytics_view, name='leads_analytics'),
    path('leads/export/', views.leads_export_view, name='leads_export'),
    path('leads/<uuid:lead_id>/mark-billed/', views.lead_mark_billed_view, name='lead_mark_billed'),

    # Chatbot Monitoring
    path('chatbot/', views.chatbot_conversations_view, name='chatbot_conversations'),
    path('chatbot/<uuid:conversation_id>/', views.chatbot_detail_view, name='chatbot_detail'),
]
