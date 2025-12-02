from django.contrib import admin
from django.urls import path
from analytics import views  # Import your views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload_file, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'), # <--- Added this line
    path('', views.dashboard, name='home'), # <--- Added this so Homepage goes to dashboard
]