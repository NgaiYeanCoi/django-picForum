# works/models.py
import os

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField('分类名称', max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='父分类')
    description = models.TextField('分类描述', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '作品分类'
        verbose_name_plural = '作品分类'

def get_upload_path(instance, filename):
    username = instance.photographer.username if instance.photographer else 'unknown'
    # TODO:改写一下包含作品title
    # title = instance.work.title if instance.work else ''
    now = timezone.now()
    return os.path.join(
        username,
        'works',
        str(now.year),
        str(now.month),
        str(now.day),
        # title,
        filename
    )

class Work(models.Model):
    title = models.CharField('作品标题', max_length=100, blank=False, null=False)
    #views = models.PositiveIntegerField('浏览量', default=0)
    description = models.TextField('作品描述', blank=True)
    image = models.ImageField('作品图片', upload_to=get_upload_path) #ImageField会自动验证上传的文件是否为有效图像
    photographer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='摄影师')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    shot_date = models.DateField('拍摄日期', blank=True, null=True)
    camera_model = models.CharField('相机型号', max_length=100, blank=True, null=True)
    is_public = models.BooleanField('公开显示', default=False)
    iso = models.IntegerField('ISO值', blank=True, null=True,validators=[MinValueValidator(0)])
    shutter_speed = models.CharField('快门速度', max_length=50, blank=True, null=True)
    aperture = models.CharField('光圈值', max_length=10, blank=True, null=True)
    lens_mm = models.CharField('焦距(mm)', max_length=10,blank=True, null=True)

    # 多对多关系，明确指定through模型
    categories = models.ManyToManyField(Category, through='WorkCategory', verbose_name='作品分类')

    def __str__(self):
        return self.title or os.path.basename(self.image.name)

    class Meta:
        verbose_name = '摄影作品'
        verbose_name_plural = '摄影作品'
        ordering = ['-created_at']


class WorkCategory(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, verbose_name='作品')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    created_at = models.DateTimeField('关联时间', auto_now_add=True)

    def __str__(self):
        return f'{self.work.title} - {self.category.name}'

    class Meta:
        verbose_name = '作品分类关联'
        verbose_name_plural = '作品分类关联'
        db_table = 'works_workcategory'  # 指定表名