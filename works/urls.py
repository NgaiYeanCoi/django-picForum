# works/urls.py
from django.urls import path
from . import views

app_name = 'works'

urlpatterns = [
    path('', views.work_list, name='work_list'),  # 登录后跳转到作品列表页
    path('upload/', views.work_upload, name='work_upload'),  # 作品上传页
    path('detail/<int:pk>/', views.work_detail, name='work_detail'),  # 作品详情页
    path('like/<int:pk>/', views.toggle_like, name='toggle_like'),  # 点赞/取消点赞
    path('edit/<int:pk>/', views.work_edit, name='work_edit'),  # 作品编辑页
    path('delete/<int:pk>/', views.work_delete, name='work_delete'),  # 作品删除
    path('category/<int:category_id>/', views.work_list_by_category, name='work_list_by_category'),  # 分类作品列表
    path('get-exif-info/', views.get_exif_info, name='get_exif_info'),
    path('api/stats/', views.get_works_stats, name='get_works_stats'),
]