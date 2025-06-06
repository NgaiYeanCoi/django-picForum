from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from accounts.views import register  # 导入注册视图
from works.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('works/', include('works.urls')),
    path('shares/', include('shares.urls')),
    path('',index,name='index' ),

    # 认证URL
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register, name='register'),
    path('accounts/password_change',PasswordChangeView.as_view(template_name='registration/password_change.html'),name='password_change'),
    path('accounts/password_change/done/',PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),name='password_change_done'),
]

# 开发环境中处理媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)    