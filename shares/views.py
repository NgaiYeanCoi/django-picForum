from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from .models import ShareLink
from works.models import Work
import hashlib
from django.conf import settings

def share_detail(request, share_code):
    """分享链接详情视图"""
    try:
        share_link = get_object_or_404(ShareLink, share_code=share_code)
        work = share_link.work
        
        # 检查链接是否过期
        if share_link.is_expired():
            messages.error(request, "分享链接已过期！")
            return redirect('works:work_list')
        
        # 检查是否需要密码
        if share_link.password:
            if 'share_password' not in request.session or request.session['share_password'] != share_link.password:
                return redirect('shares:share_password', share_code=share_code)
        
        # 检查权限：公开作品或创建者本人
        if not work.is_public and request.user != share_link.created_by:
            return HttpResponseForbidden("无访问权限！")
        
        # 记录访问
        share_link.accessed_count += 1
        share_link.last_accessed_at = datetime.now()
        share_link.save()
        
        return render(request, 'shares/share_detail.html', {'work': work, 'share_link': share_link})
    
    except ShareLink.DoesNotExist:
        raise Http404("分享链接不存在！")

@login_required
def create_share_link(request, work_id):
    """创建分享链接视图"""
    work = get_object_or_404(Work, id=work_id, photographer=request.user)
    
    if request.method == 'POST':
        expires_days = int(request.POST.get('expires_days', 7))
        password = request.POST.get('password', '')
        
        # 创建分享链接
        share_link = ShareLink.create_share_link(
            work=work,
            user=request.user,
            expires_days=expires_days,
            password=password if password else None
        )
        
        messages.success(request, "分享链接创建成功！")
        return render(request, 'shares/share_created.html', {'share_link': share_link})
    
    return render(request, 'shares/create_share.html', {'work': work})

def share_password(request, share_code):
    """分享密码验证视图"""
    share_link = get_object_or_404(ShareLink, share_code=share_code)
    
    if request.method == 'POST':
        entered_password = request.POST.get('password', '')
        hashed_password = hashlib.sha256(entered_password.encode()).hexdigest()
        
        if hashed_password == share_link.password:
            # 密码正确，存储到session
            request.session['share_password'] = hashed_password
            return redirect('shares:share_detail', share_code=share_code)
        else:
            messages.error(request, "密码错误！")
    
    return render(request, 'shares/share_password.html', {'share_link': share_link})    