# works/forms.py
from django import forms
from .models import Work


class WorkForm(forms.ModelForm):
    """作品表单"""
    class Meta:
        model = Work
        fields = ['title', 'description', 'image', 'shot_date', 'camera_model',
                  'iso', 'shutter_speed', 'aperture', 'lens_mm', 'is_public']

        # 设置字段标签
        labels = {
            'title': '作品标题',
            'description': '作品描述',
            'image': '作品图片',
            'shot_date': '拍摄日期',
            'camera_model': '相机型号',
            'iso': 'ISO值',
            'shutter_speed': '快门速度',
            'aperture': '光圈值',
            'focal_length': '焦距(mm)',
            'is_public': '公开显示',
        }

        # 设置帮助文本
        help_texts = {
            'image': '支持JPG、PNG格式，最大50MB',
            'shot_date': '格式：YYYY-MM-DD',
            'iso': '如：100, 200, 400等',
            'shutter_speed': '如：1/125, 1/250, 1/500等',
            'aperture': '如：2.8, 4.0, 5.6等',
            'lens_mm': '单位：毫米(mm)',
        }

        # 设置widgets
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'shot_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'camera_model': forms.TextInput(attrs={'class': 'form-control'}),
            'iso': forms.NumberInput(attrs={'class': 'form-control', 'min': 50, 'max': 102400}),
            'shutter_speed': forms.TextInput(attrs={'class': 'form-control'}),
            'aperture': forms.NumberInput(attrs={'class': 'form-control', 'min': 1.0, 'max': 32.0, 'step': 0.1}),
            'lens_mm': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 1000}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_shutter_speed(self):
        """验证快门速度格式"""
        value = self.cleaned_data.get('shutter_speed')
        if value:
            # 允许格式如：允许 1/125 格式或 1/125s 格式
            import re
            if not re.match(r'^(1/)?\d+(\.\d+)?\s?s?$', value):
                raise forms.ValidationError("请输入有效的快门速度格式，如：1/125或1/125s")
        return value

    def clean_aperture(self):
        """验证光圈值范围"""
        value = self.cleaned_data.get('aperture')
        if value:
            import re
            if not re.match(r'^f/?\d+(\.\d+)?$', value):
                raise forms.ValidationError("请输入有效的光圈格式格式，如：2.8或f2.8")
        return value