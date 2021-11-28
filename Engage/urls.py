"""Engage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from dashboard import views as dash_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('register/', dash_views.register, name = 'register'),
    path('signin/', auth_views.LoginView.as_view(template_name = "dashboard/signin.html"), name = 'signin'),
    path('signout/', auth_views.LogoutView.as_view(template_name = "dashboard/signout.html"), name = 'signout'),
    path('profile/', dash_views.profile, name = 'profile'),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path('accounts/', include('allauth.urls')),
    # path('<std:username>/', dash_views.profile, name = 'user_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
