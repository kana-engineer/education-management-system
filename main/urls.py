from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('apply-course/', views.apply_course, name='apply_course'),
    path('contackt/', views.contackt, name='contackt'),
    path('news/', views.news_list, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('corey/', views.corey, name='corey'),
    path('admission-korea/', views.admission_korea, name='admission_korea'),
    path('set_language/<str:language>/', views.set_language, name='set_language'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('admin/set_students/', views.set_students, name='set_students'),
    path('admin/news/add/', views.add_news, name='add_news'),
    path('admin/news/edit/<int:news_id>/', views.edit_news, name='edit_news'),
    path('admin/news/delete/<int:news_id>/', views.delete_news, name='delete_news'),
    path('admin/admission-periods/', views.admin_admission_periods, name='admin_admission_periods'),
    path('admin/admission-periods/add/', views.add_admission_period, name='add_admission_period'),
    path('admin/admission-periods/edit/<int:id>/', views.edit_admission_period, name='edit_admission_period'),
    path('admin/admission-periods/delete/<int:id>/', views.delete_admission_period, name='delete_admission_period'),
    path('admin/teachers/', views.admin_teachers, name='admin_teachers'),
    path('admin/teachers/delete/<int:id>/', views.delete_teacher, name='delete_teacher'),
    path('update-status/', views.update_status, name='update_status'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
]
