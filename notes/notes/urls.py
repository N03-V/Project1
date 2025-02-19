from django.contrib import admin
from django.urls import path
 
from document.views import *
 
urlpatterns = [
    path('login/' , login_page, name='login'),
    path('register/', register_page, name='register'),
    path('custom_logout/' ,custom_logout, name='logout'),
    path('', editor, name='editor'),
    path('delete_note/<int:docid>/', delete_note, name='delete_note'),
    path('admin/', admin.site.urls),
]
