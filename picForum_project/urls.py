from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accounts.views import register  # 导入注册视图

urlpatterns = [
    path('admin/', admin.site.urls),
    path('works/', include('works.urls')),
    path('shares/', include('shares.urls')),
    path('', include('works.urls')),  # 根路径指向作品应用

    # 认证URL
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register, name='register'),
]

# 开发环境中处理媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)    