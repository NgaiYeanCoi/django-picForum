# django-picForum
## 介绍
django-picForum 是一个基于 Django 框架开发的摄影作品论坛  
该项目还在建设当中，欢迎你们提交Pull Request或Issues与我一起维护这个项目

## 已经实现的功能
- [X] 用户认证：支持用户注册、登录、修改密码和退出登录
- [X] 作品管理：上传、删除自己的作品
- [X] EXIF信息提取：上传作品时，自动提取图片的 EXIF 信息，如拍摄日期、相机型号、ISO、快门速度、光圈和焦段
- [X] 搜索功能：可以通过标题关键词模糊搜索作品
- [X] 水印功能：为上传的照片上打上水印
- [X] 作品编辑视图：处理作品信息的修改和更新


## TODO:
- [ ] 实现作品分类：管理，用户可以根据分类筛选作品
- [X] 实现作品分享链接：为作品生成分享链接，设置链接的有效期和密码
- [X] 加入公共区-首页(设置为公开后其他用户可以查看，还差权限没做好)
- [ ] 实现公开作品点击量搜集
- [X] 分页导航
- [ ] 管理后台需要更多功能：筛选所有已分享作品、未公开的作品等；



## 安装部署

### 环境
- Python3.x以上
- MySQL数据库

### 安装步骤
#### 1.克隆仓库
```bash
git clone https://github.com/NgaiYeanCoi/django-picForum.git
cd django-picForum
```
#### 2.创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```
#### 3.安装依赖
- 在使用前先安装第三方依赖库
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

- pillow~=11.2.1
- Django~=5.2.1
- asgiref~=3.8.1
- sqlparse~=0.5.3
- mysqlclient~=2.2.7
- ExifRead~=3.3.1
- django-extensions~=4.1

#### 4.配置数据库
- 在根目录下picForum_project/settings.py 中配置数据库信息：
```python
# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'photographer_portfolio',#数据库名可以自定义
        'USER': 'root',#数据库用户名
        'PASSWORD': '10086',#密码
        'HOST': 'localhost',
        'PORT': '3306',#端口
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```
#### 5.创建数据库

- 1. 手动建数据库
```mysql
# photographer_portfolio可以自定义，但必须与picForum_project/settings.py保持一致
CREATE DATABASE photographer_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- 2. 数据库迁移
```bash
python manage.py makemigrations  # 生成初始迁移文件
python manage.py migrate         # 创建所有表
```
#### 6.创建超级用户
```bash
python manage.py createsuperuser #后按照提示输入用户名密码
```

#### 7.运行
- 准备就绪后执行:
```bash
python manage.py runserver 127.0.0.1:8000
```
- 浏览器访问http://127.0.0.1:8000

### 文件结构
```plaintext
django-picForum/
├── .gitignore                      # Git 忽略文件
├── manage.py                       # Django 项目的管理脚本
├── requirements.txt                # 项目依赖文件
├── accounts/                       # 用户认证相关应用
│   ├── __init__.py                 # 初始化文件
│   ├── apps.py                     # 应用配置文件
│   ├── models.py                   # 模型文件，定义与用户认证相关的数据模型
│   ├── views.py                    # 视图文件，处理用户认证相关的业务逻辑
│   └── admin.py                    # 管理后台配置文件
├── picForum_project/               # 项目配置目录
│   ├── __init__.py                 # 初始化文件，确保使用 UTF-8 编码并可启用数据库连接池
│   ├── settings.py                 # 项目设置文件，包含项目的各种配置信息，如数据库、静态文件等
│   ├── urls.py                     # 项目 URL 配置文件，定义项目的 URL 路由规则
│   └── wsgi.py                     # WSGI 配置文件，用于部署 Django 项目到服务器
├── shares/                         # 作品分享相关应用
│   ├── __init__.py                 # 初始化文件
│   ├── apps.py                     # 应用配置文件，定义应用的基本信息
│   ├── models.py                   # 模型文件，定义与作品分享相关的数据模型
│   ├── views.py                    # 视图文件，处理作品分享相关的业务逻辑
│   └── admin.py                    # 管理后台配置文件
├── works/                          # 作品管理相关应用
│   ├── __init__.py                 # 初始化文件
│   ├── apps.py                     # 应用配置文件，定义应用的基本信息
│   ├── models.py                   # 模型文件，定义与作品管理相关的数据模型
│   ├── views.py                    # 视图文件，处理作品管理相关的业务逻辑
│   ├── urls.py                     # 应用 URL 配置文件，定义作品管理应用的 URL 路由规则
│   ├── forms.py                    # 表单文件，定义与作品管理相关的表单
│   └── admin.py                    # 管理后台配置文件
├── templates/                      # 模板文件目录，存放 HTML 模板文件
│   ├── base.html                   # 基础模板文件，包含项目的通用布局和样式
│   ├── index.html                  # 首页模板文件，展示项目的首页内容
│   ├── registration/               # 用户注册和登录相关模板
│   │   ├── login.html              # 用户登录页面模板
│   │   ├── password_change.html    # 用户修改密码页面模板
│   │   ├── password_change_done.html # 用户修改密码成功页面模板
│   │   └── register.html           # 用户注册页面模板
│   └── works/                      # 作品相关模板
│       ├── work_detail.html        # 作品详情页面模板
│       ├── work_list.html          # 作品列表页面模板
│       ├── work_upload.html        # 作品上传页面模板
│       └── work_edit.html          # 作品编辑页面模板
```

## 后期会加的功能 ~~（如果自己不懒）~~
- [ ] 还在考虑当中...

### 作者
[NgaiYeanCoi](https://github.com/NgaiYeanCoi)

### 许可证
[MIT License](https://github.com/NgaiYeanCoi/django-picForum/blob/main/LICENSE)