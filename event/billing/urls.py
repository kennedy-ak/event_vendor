from django.urls import path
from . import views

urlpatterns = [
    # Subscription management
    path('plans/', views.subscription_plans_view, name='subscription_plans'),
    path('subscribe/<uuid:plan_id>/', views.subscribe_view, name='subscribe'),
    path('verify-subscription/<uuid:subscription_id>/', views.verify_subscription_payment, name='verify_subscription'),
    path('cancel-subscription/<uuid:subscription_id>/', views.cancel_subscription_view, name='cancel_subscription'),

    # Boost/Featured listings
    path('purchase-boost/', views.purchase_boost_view, name='purchase_boost'),
    path('verify-boost/<uuid:boost_id>/', views.verify_boost_payment, name='verify_boost'),

    # Webhook
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
