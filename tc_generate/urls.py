"""
URL configuration for tc_generate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from tc_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
     path('uploads/', views.upload_excel, name='upload_excel'),

    path('', views.user_login, name='login'),
    path('students/', views.student_list, name='student_list'),
    path('generate_tc/<int:id>/', views.generate_tc, name='generate_tc'),
    path('bulk-tc/', views.bulk_tc, name='bulk_tc'),

path('admin-dashboard/', views.admin_dashboard,name='admin_dashboard'),
path('approve/<int:id>/', views.approve_tc),
path('reject/<int:id>/', views.reject_tc),
#path('pending/', views.pending_requests),
path('staff_dashboard/', views.staff_dashboard,name='staff_dashboard'),
path('', views.user_login),
path('register/', views.register,name='register'),

path('user-dashboard/', views.user_dashboard,name='user_dashboard'),
path('request-tc/', views.request_tc),
path('tc-template/', views.tc_template,name="tc-template"),
#path('status/', views.status_view,name='status'),

path('pending/', views.pending,name='pending'),
path('rejected/', views.rejected,name="rejected"),
path('approved/', views.approved,name='approved'),

path('stud_del/<int:id>', views.student_delete,name='stud_del'),

path('report/', views.Reports,name='reports'),
path('logout/', views.user_logout, name='logout')
]