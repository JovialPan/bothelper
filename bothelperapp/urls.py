from django.urls import path
# 引用這個資料夾中的 views 檔案
from . import views
urlpatterns = [
    path('', views.index, name = "Index")
]