from django.contrib import admin
# 增加引用 include 函式
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    # 新增應用程式的網址
    path('bothelperapp/', include('bothelperapp.urls')),
]