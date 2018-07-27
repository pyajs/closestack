"""closestack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from .views import index, vm_template, vm_manager
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),

    # index, show README.md in html
    path('', index.index),

    # vm template
    path('template/', csrf_exempt(vm_template.VmTemplateListView.as_view())),

    # vm manager
    path('vms/', csrf_exempt(vm_manager.VmManagerListView.as_view())),
    path('vms/<int:id>/', csrf_exempt(vm_manager.VmManagerDetailView.as_view())),

    # vm actions
    path('vms/<int:id>/action', csrf_exempt(vm_manager.VmActionView.as_view())),


]
