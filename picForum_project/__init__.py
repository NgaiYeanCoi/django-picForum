# 确保使用UTF-8编码
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'picForum_project.settings')

# 启用数据库连接池（可选）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass    