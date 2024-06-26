from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.main, name = 'main'),
    path('addtask/', views.addtask, name='addtask'),
    path('removetask/<int:task_id>/', views.removetask, name="removetask"),
    path('taskdetails/<int:task_id>/', views.taskdetails, name='taskdetails'),
    path('taskupdate/<int:task_id>/', views.taskupdate, name='taskupdate'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.singup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('mark-completed/<int:task_id>/', views.markedcomplete, name='mark_task_completed'),
]