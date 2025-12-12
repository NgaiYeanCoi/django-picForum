from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.urls import reverse_lazy
from django.conf import settings

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账号 {username} 创建成功！可以登录了。')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class RememberLoginView(LoginView):
    '''
    当用户勾选“记住我”复选框时，会将登录状态保存到会话中
    @param self: 视图实例
    @param request: HTTP请求对象
    @param form: 登录表单实例
    @return: HTTP响应对象
    '''
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        remember = self.request.POST.get('remember_me')
        if not remember:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return response


