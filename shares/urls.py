from django.urls import path
from . import views

app_name = 'shares'

urlpatterns = [
    path('<str:share_code>/', views.share_detail, name='share_detail'),
    path('create/<int:work_id>/', views.create_share_link, name='create_share'),
    path('password/<str:share_code>/', views.share_password, name='share_password'),
    path('cancel/<str:share_code>/', views.cancel_share, name='cancel_share'),
]    