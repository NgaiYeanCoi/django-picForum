# work/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Work, Category, WorkCategory
from .forms import WorkForm
import exifread
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.contrib.auth.models import User
import os
from django.core.paginator import Paginator

def page_nav(queryset, page_number, per_page=6):
    """
    查询集进行分页处理
    :param queryset: 查询集对象
    :param page_number: 当前请求的页码
    :param per_page: 每页显示的对象数量（默认为6）
    :return:    返回一个 Page 对象
    """
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        popular_works = Work.objects.filter(
            is_public=True,
            title__icontains=search_query
        ).order_by('created_at')
        #TODO:实现浏览量
    else:
        popular_works = Work.objects.filter(is_public=True).order_by('created_at') # TODO:筛选公开的热门作品（按浏览量排序暂时没实现）

    # 获取统计信息
    user_count = User.objects.count()
    work_public_count = Work.objects.filter(is_public=True).count() # 只统计公开作品
    work_count= Work.objects.count()

    # 分页
    page_number = request.GET.get('page')
    page_obj = page_nav(popular_works, page_number)

    context = {
        'popular_works': popular_works,
        'user_count': user_count,
        'work_public_count': work_public_count,
        'work_count': work_count,
        'page_obj': page_obj,
        'search_query': search_query
    }

    return render(request, 'index.html', context)


@login_required
def work_list(request):
    """作品列表视图"""
    search_query = request.GET.get('search','')
    if search_query:
        works = Work.objects.filter(
            photographer=request.user,
            title__icontains=search_query
        ).order_by('-created_at')
    else:
        works = Work.objects.filter(photographer=request.user).order_by('-created_at')
    categories = Category.objects.all()

    # 分页
    page_number = request.GET.get('page')
    page_obj = page_nav(works, page_number)

    context = {
        'works': works,
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query
    }
    return render(request, 'works/work_list.html', context)


@login_required
def work_upload(request):
    """作品上传视图"""
    exif_info = {
        'shot_date': None,
        'camera_model': None,
        'image_preview': None  # 图片预览路径
    }
    initial = {'is_public': True}
    form = WorkForm(initial=initial)

    if request.method == 'POST':
        form = WorkForm(request.POST, request.FILES)
        if form.is_valid():
            work = form.save(commit=False)
            work.photographer = request.user

            # 从表单数据中获取EXIF信息,并从cleaned_data获取已验证的数据
            work.shot_date = form.cleaned_data.get('shot_date')
            work.camera_model = form.cleaned_data.get('camera_model')
            work.iso = form.cleaned_data.get('iso')
            work.shutter_speed = form.cleaned_data.get('shutter_speed')
            work.lens_mm = form.cleaned_data.get('lens_mm')
            work.aperture = form.cleaned_data.get('aperture')
            work.save()

            # 生成缩略图
            try:
                if work.image:
                    generate_thumbnail(work.image.path)
            except Exception as e:
                messages.error(request, f"缩略图生成失败: {e}")

            messages.success(request, '作品上传成功！')

            # 重定向到作品列表页
            return redirect('works:work_list')
        else:
            messages.error(request, '表单填写有误，请检查！')

    categories = Category.objects.all()
    return render(request, 'works/work_upload.html', {
        'form': form,
        'categories': categories,
        'exif_info': exif_info
    })

def work_detail(request, pk):
    """作品详情视图"""
    # 先筛选出ID匹配的作品
    queryset = Work.objects.filter(id=pk)
    # 若当前用户不是作品的摄影师，则只显示公开作品
    if request.user != queryset.first().photographer:
        queryset = queryset.filter(is_public=True)
    # 获取对象或返回404
    work = get_object_or_404(queryset)
    return render(request, 'works/work_detail.html', {'work': work})


@login_required
def work_edit(request, pk):
    """
    作品编辑视图 - 处理作品信息的修改和更新
    :param request:HTTP请求对象
    :param pk:要编辑的作品主键
    :return: POST请求且表单有效: 重定向到作品详情页 其他情况: 渲染编辑表单页面
    """
    work = get_object_or_404(Work, id=pk)
    if request.user != work.photographer and not request.user.is_superuser:
        messages.error(request,"权限不足，无法编辑。")
        return redirect('works:work_detail', pk=work.id)
    if not work.id:
        messages.error(request,"作品ID为空或不存在，无法编辑。")
        return redirect('works:work_list')
    exif_info = {
        'shot_date': work.shot_date,
        'camera_model': work.camera_model,
        'image_preview': work.image.url if work.image else None
    }



    if request.method == 'POST':
        form = WorkForm(request.POST, request.FILES, instance=work)
        if form.is_valid(): #判断表单是否合法
            form.save()
            # 更新分类
            WorkCategory.objects.filter(work=work).delete()
            category_ids = request.POST.getlist('categories')
            for category_id in category_ids:
                if category_id:
                    category = get_object_or_404(Category, id=category_id)
                    WorkCategory.objects.create(work=work, category=category)

            # 如果上传了新图片，重新提取EXIF
            if request.FILES.get('image'):
                try:
                    with open(work.image.path, 'rb') as f:
                        tags = exifread.process_file(f)
                        if 'EXIF DateTimeOriginal' in tags:
                            date_str = str(tags['EXIF DateTimeOriginal'])
                            work.shot_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date()
                        if 'Image Model' in tags:
                            work.camera_model = str(tags['Image Model'])
                    work.save()
                except Exception as e:
                    messages.error(request, f"新图片EXIF提取失败: {e}")

            messages.success(request, '作品更新成功！')
            return redirect('works:work_detail', pk=work.id)
    else:
        form = WorkForm(instance=work)

    categories = Category.objects.all()
    selected_categories = work.categories.all().values_list('id', flat=True)
    return render(request, 'works/work_edit.html', {
        'form': form,
        'categories': categories,
        'selected_categories': selected_categories,
        'exif_info': exif_info,
        'work':work
    })


@login_required
def work_delete(request, pk):
    """
    :param request: HTTP请求的对象
    :param pk: 要删除作品的主键
    :return:POST请求: 重定向到作品列表页
                GET请求: 重定向到作品详情页
    """
    # 查询指定主键且属于当前用户的作品对象，不存在则返回404
    work = get_object_or_404(Work, id=pk)
    if request.user != work.photographer and not request.user.is_superuser:
        messages.error(request,"权限不足，无法删除。")
        return redirect('works:work_detail', pk=work.id)
    if request.method == 'POST':
        # 处理确认删除的POST请求

        # 尝试删除与作品关联的图片文件
        try:
            # 检查作品是否有图片且文件存在于文件系统中
            if work.image and os.path.exists(work.image.path):
                os.remove(work.image.path)  # 删除物理图片文件
        except Exception as e:
            print(f"文件删除失败: {e}")

        # 删除数据库中的作品记录
        work.delete()
        # 添加成功消息到会话中，将在重定向后的页面显示
        messages.success(request, '作品已删除！')
        # 重定向到作品列表页
        return redirect('works:work_list')
    # 处理GET请求(直接访问删除URL的情况)
    # 重定向回作品详情页，避免直接显示删除确认页面
    return redirect('works:work_detail', pk=work.id)


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


@csrf_exempt
def get_exif_info(request):
    """处理AJAX请求，提取图片EXIF信息"""
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        exif_info = {
            'shot_date': None,
            'camera_model': None,
            'iso': None,
            'shutter_speed': None,
            'aperture': None,
            'lens_mm': None,
            'success': False,
            'error': None
        }

        try:
            # 读取EXIF信息
            tags = exifread.process_file(image_file)

            if 'EXIF DateTimeOriginal' in tags:
                date_str = str(tags['EXIF DateTimeOriginal'])
                exif_info['shot_date'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date().strftime('%Y-%m-%d')

            if 'Image Model' in tags:
                exif_info['camera_model'] = str(tags['Image Model'])

            # 新增EXIF信息
            if 'EXIF ISOSpeedRatings' in tags:
                exif_info['iso'] = str(tags['EXIF ISOSpeedRatings'])

            if 'EXIF ExposureTime' in tags:
                exposure = str(tags['EXIF ExposureTime'])
                # 将快门转换为更易读的格式
                if '/' in exposure:
                    num, denom = exposure.split('/')
                    try:
                        shutter = float(num) / float(denom)
                        if shutter < 1:
                            exif_info['shutter_speed'] = f"1/{int(round(1 / shutter))}s"
                        else:
                            exif_info['shutter_speed'] = f"{shutter}s"
                    except:
                        exif_info['shutter_speed'] = exposure
                else:
                    exif_info['shutter_speed'] = exposure

            if 'EXIF FNumber' in tags:
                fnumber = str(tags['EXIF FNumber'])
                # 转换为f/格式
                if '/' in fnumber:
                    num, denom = fnumber.split('/')
                    try:
                        aperture = float(num) / float(denom)
                        exif_info['aperture'] = f"f/{aperture:.1f}"
                    except:
                        exif_info['aperture'] = f"f/{fnumber}"
                else:
                    exif_info['aperture'] = f"f/{fnumber}"

            if 'EXIF FocalLength' in tags:
                lens_mm = str(tags['EXIF FocalLength'])
                # 转换为mm格式
                if '/' in lens_mm:
                    num, denom = lens_mm.split('/')
                    try:
                        focal = float(num) / float(denom)
                        exif_info['lens_mm'] = f"{focal:.0f}mm"
                    except:
                        exif_info['lens_mm'] = f"{lens_mm}mm"
                else:
                    exif_info['lens_mm'] = f"{lens_mm}mm"

            exif_info['success'] = True
        except Exception as e:
            exif_info['error'] = str(e)

        return JsonResponse(exif_info)

    return JsonResponse({'success': False, 'error': 'Invalid request'})


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