# works/models.py
import os

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField('分类名称', max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='父分类')
    description = models.TextField('分类描述', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '作品分类'
        verbose_name_plural = '作品分类'


class Work(models.Model):
    title = models.CharField('作品标题', max_length=100, blank=True)
    description = models.TextField('作品描述', blank=True)
    image = models.ImageField('作品图片', upload_to='works/%Y/%m/%d')
    photographer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='摄影师')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    shot_date = models.DateField('拍摄日期', blank=True, null=True)
    camera_model = models.CharField('相机型号', max_length=100, blank=True)
    is_public = models.BooleanField('公开显示', default=False)

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
        db_table = 'works_workcategory'  # 明确指定表名