from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Work, Category, WorkCategory
from .forms import WorkForm
import exifread
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import os

@login_required
def work_list(request):
    """作品列表视图"""
    works = Work.objects.filter(photographer=request.user).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'works/work_list.html', {'works': works, 'categories': categories})

@login_required
def work_upload(request):
    """作品上传视图"""
    if request.method == 'POST':
        form = WorkForm(request.POST, request.FILES)
        if form.is_valid():
            work = form.save(commit=False)
            work.photographer = request.user
            
            # 尝试提取EXIF信息
            try:
                with open(work.image.path, 'rb') as f:
                    tags = exifread.process_file(f)
                    if 'EXIF DateTimeOriginal' in tags:
                        date_str = str(tags['EXIF DateTimeOriginal'])
                        work.shot_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date()
                    if 'Image Model' in tags:
                        work.camera_model = str(tags['Image Model'])
            except Exception as e:
                print(f"EXIF提取失败: {e}")
            
            work.save()
            
            # 处理分类
            category_ids = request.POST.getlist('categories')
            for category_id in category_ids:
                if category_id:
                    category = get_object_or_404(Category, id=category_id)
                    WorkCategory.objects.create(work=work, category=category)
            
            # 生成缩略图（异步处理会更好，但此处简化）
            try:
                generate_thumbnail(work.image.path)
            except Exception as e:
                print(f"缩略图生成失败: {e}")
            
            messages.success(request, '作品上传成功！')
            return redirect('works:work_list')
    else:
        form = WorkForm()
    categories = Category.objects.all()
    return render(request, 'works/work_upload.html', {'form': form, 'categories': categories})

@login_required
def work_detail(request, pk):
    """作品详情视图"""
    work = get_object_or_404(Work, id=pk, photographer=request.user)
    return render(request, 'works/work_detail.html', {'work': work})

@login_required
def work_edit(request, pk):
    """作品编辑视图"""
    work = get_object_or_404(Work, id=pk, photographer=request.user)
    if request.method == 'POST':
        form = WorkForm(request.POST, request.FILES, instance=work)
        if form.is_valid():
            form.save()
            
            # 更新分类
            WorkCategory.objects.filter(work=work).delete()
            category_ids = request.POST.getlist('categories')
            for category_id in category_ids:
                if category_id:
                    category = get_object_or_404(Category, id=category_id)
                    WorkCategory.objects.create(work=work, category=category)
            
            messages.success(request, '作品更新成功！')
            return redirect('works:work_detail', pk=work.id)
    else:
        form = WorkForm(instance=work)
    categories = Category.objects.all()
    selected_categories = work.categories.all().values_list('id', flat=True)
    return render(request, 'works/work_edit.html', {
        'form': form, 
        'categories': categories,
        'selected_categories': selected_categories
    })

@login_required
def work_delete(request, pk):
    """作品删除视图"""
    work = get_object_or_404(Work, id=pk, photographer=request.user)
    if request.method == 'POST':
        # 删除相关文件
        try:
            if os.path.exists(work.image.path):
                os.remove(work.image.path)
            # 可以添加删除缩略图的逻辑
        except Exception as e:
            print(f"文件删除失败: {e}")
        
        work.delete()
        messages.success(request, '作品已删除！')
        return redirect('works:work_list')
    return render(request, 'works/work_delete_confirm.html', {'work': work})

@login_required
def work_list_by_category(request, category_id):
    """按分类显示作品列表"""
    category = get_object_or_404(Category, id=category_id)
    works = Work.objects.filter(categories=category, photographer=request.user).order_by('-created_at')
    all_categories = Category.objects.all()
    return render(request, 'works/work_list.html', {
        'works': works, 
        'categories': all_categories,
        'current_category': category
    })

def generate_thumbnail(image_path):
    """生成图片缩略图和水印图"""
    try:
        img = Image.open(image_path)
        img.thumbnail((1200, 1200))  # 调整尺寸
        
        # 添加简单水印
        draw = ImageDraw.Draw(img)
        font_size = max(20, int(min(img.size) / 20))
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SimHei.ttf'), font_size)
        except:
            font = ImageFont.load_default()
        
        # 添加半透明水印文字
        watermark_text = f"© {settings.COPYRIGHT_NAME}" if hasattr(settings, 'COPYRIGHT_NAME') else "© Photographer"
        text_width, text_height = draw.textsize(watermark_text, font=font)
        position = ((img.width - text_width) // 2, (img.height - text_height) // 2)
        
        # 创建带有透明度的水印图层
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw_watermark = ImageDraw.Draw(watermark)
        draw_watermark.text(position, watermark_text, font=font, fill=(255, 255, 255, 128))
        
        # 合并水印
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img = Image.alpha_composite(img, watermark)
        
        # 保存处理后的图片
        img = img.convert('RGB')  # 转换回RGB以保存为JPEG
        img.save(image_path)
        
    except Exception as e:
        print(f"图片处理错误: {e}")    