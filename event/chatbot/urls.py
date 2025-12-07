from django.urls import path
from . import views

urlpatterns = [
    # Main chatbot page
    path('plan-my-event/', views.plan_my_event_view, name='plan_my_event'),

    # API endpoints
    path('api/chat/start/', views.chat_start, name='chat_start'),
    path('api/chat/message/', views.chat_message, name='chat_message'),
    path('api/chat/recommendations/<str:conversation_code>/', views.chat_recommendations, name='chat_recommendations'),
    path('api/chat/email/', views.email_recommendations, name='email_recommendations'),
    path('api/chat/track/', views.track_recommendation_action, name='track_recommendation_action'),
]
