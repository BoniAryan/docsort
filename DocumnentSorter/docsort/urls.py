from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('login_manager/', views.login_manager, name='login_manager'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload, name='upload'),
    path('document/<int:doc_id>/', views.document_detail, name='document_detail'),
    path('document/<int:doc_id>/download/<int:file_num>/', views.download_file, name='download_file'),

]