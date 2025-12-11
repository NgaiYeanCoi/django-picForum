import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from works.models import Work


class ShareLink(models.Model):
    """分享链接模型"""
    work = models.ForeignKey(Work, on_delete=models.CASCADE, verbose_name='作品')
    share_code = models.CharField('分享码', max_length=32, unique=True, default=uuid.uuid4().hex[:32]) #生成uuid
    password = models.CharField('访问密码', max_length=128, blank=True, null=True)
    expires_at = models.DateTimeField('过期时间', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    accessed_count = models.IntegerField('访问次数', default=0)
    last_accessed_at = models.DateTimeField('最后访问时间', blank=True, null=True)

    def __str__(self):
        return f"{self.work.title} - {self.share_code}"

    class Meta:
        verbose_name = '分享链接'
        verbose_name_plural = '分享链接'

    def is_expired(self):
        """检查链接是否过期"""
        return self.expires_at and timezone.now() > self.expires_at

    def generate_share_url(self, request):
        """生成完整分享URL"""
        base_url = request.build_absolute_uri('/')
        return f"{base_url}shares/{self.share_code}/"

    @classmethod
    def create_share_link(cls, work, user, expires_days=7, password=None):
        """
        创建分享链接的快捷方法
        :param work: 请求的作品
        :param user: 请求的用户
        :param expires_days: 过期天数默认为7
        :param password: 密码默认为空
        :return: share_link分享链接
        """

        expires_at = timezone.now() + timezone.timedelta(days=expires_days) if expires_days else None
        
        # 如果有密码，进行哈希处理
        if password:
            import hashlib
            password = hashlib.sha256(password.encode()).hexdigest()
            
        share_link = cls(
            work=work,
            created_by=user,
            expires_at=expires_at,
            password=password
        )
        share_link.save()
        return share_link    