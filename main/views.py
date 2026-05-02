import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect

from main.decorators import admin_required
from main.forms import LoginForm, RegistrationForm, CourseApplicationForm, ContactForm
from main.models import (
    CountStudents, CourseApplication, News, AdmissionPeriod,
    Message, Teacher,
)
from main.utils import save_uploaded_file

User = get_user_model()


def _students_count():
    last = CountStudents.objects.order_by('-id').first()
    return last.count_students if last else 0


def set_language(request, language):
    if language in ('ru', 'en'):
        request.session['language'] = language
        request.session['role'] = getattr(request.user, 'role', None) or request.session.get('role')
        messages.success(request, f'Язык изменен на {language}')
    return redirect(request.META.get('HTTP_REFERER', '/') or 'main:home')


def home(request):
    return render(request, 'index.html', {'students_count': _students_count()})


def about(request):
    universities = [
        "Kyungnam College", "Yeungnam University", "Kyungil University",
        "Konyang University", "Kyungin Women's University", "Kyung Hee University",
        "Busan University of Foreign Studies", "Kunjang University", "Kukje University",
        "Chung Cheong University", "Pai Chai University ", "Youngsan University",
        "Daekyeung University", "HANSUNG UNIVERSITY", "Songho University",
    ]
    teachers = Teacher.objects.filter(is_active=True).order_by('order', 'name')
    return render(request, 'about.html', {
        'universities': universities,
        'teachers': teachers,
        'students_count': _students_count(),
    })


def courses(request):
    form = CourseApplicationForm()
    return render(request, 'courses.html', {
        'form': form,
        'students_count': _students_count(),
    })


@require_POST
@csrf_protect
def apply_course(request):
    form = CourseApplicationForm(request.POST)
    if form.is_valid():
        try:
            CourseApplication.objects.create(
                course_type=form.cleaned_data['course_type'],
                applicant_name=form.cleaned_data['name'],
                applicant_phone=form.cleaned_data['phone'],
            )
            course_names = {'korean': 'Корейский', 'english': 'Английский', 'chinese': 'Китайский'}
            name = course_names.get(form.cleaned_data['course_type'], 'Неизвестный')
            messages.success(request, f'Заявка на {name} язык отправлена!')
        except Exception:
            messages.error(request, 'Ошибка отправки заявки')
    else:
        messages.error(request, 'Ошибка валидации формы')
    return redirect('main:courses')


@require_http_methods(['GET', 'POST'])
@csrf_protect
def contackt(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Message.objects.create(
            name=form.cleaned_data['name'],
            phone=form.cleaned_data['phone'],
            message=form.cleaned_data['message'],
        )
        messages.success(request, 'Заявка успешно отправлена!')
        return redirect('main:contackt')
    return render(request, 'contackt.html', {'form': form})


def news_list(request):
    news_list_qs = News.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'news.html', {'news_list': news_list_qs})


def news_detail(request, news_id):
    news_item = get_object_or_404(News, pk=news_id)
    return render(request, 'news_detail.html', {'news': news_item})


def corey(request):
    periods = AdmissionPeriod.objects.filter(is_active=True)
    return render(request, 'corey.html', {'admission_periods': periods})


def admission_korea(request):
    return redirect('main:corey')


@admin_required
def admin_panel(request):
    users = User.objects.all()
    applications = CourseApplication.objects.order_by('-created_at')
    news_list_qs = News.objects.order_by('-created_at')
    periods = AdmissionPeriod.objects.order_by('-created_at')
    message_entry = Message.objects.all()
    teachers = Teacher.objects.order_by('order', 'name')
    return render(request, 'admin.html', {
        'users': users,
        'applications': applications,
        'news_list': news_list_qs,
        'admission_periods': periods,
        'message_entry': message_entry,
        'teachers': teachers,
        'students_count': _students_count(),
        'admin_count': User.objects.filter(role='admin').count(),
        'new_applications_count': CourseApplication.objects.filter(status='new').count(),
    })


@require_http_methods(['GET', 'POST'])
@admin_required
@csrf_protect
def set_students(request):
    if request.method == 'POST':
        try:
            n = int(request.POST.get('student_count', 0))
            CountStudents.objects.create(count_students=n)
            messages.success(request, 'Количество студентов успешно обновлено')
        except (ValueError, TypeError):
            messages.error(request, 'Некорректное число')
    return redirect('main:admin_panel')


@require_http_methods(['GET', 'POST'])
@admin_required
@csrf_protect
def add_news(request):
    if request.method != 'POST':
        return redirect('main:admin_panel')
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    is_published = 'is_published' in request.POST
    image_url = ''
    if 'photo' in request.FILES:
        f = request.FILES['photo']
        path = save_uploaded_file(f, 'novosti')
        if path:
            image_url = path
    try:
        News.objects.create(
            title=title, content=content, image_url=image_url, is_published=is_published
        )
        messages.success(request, 'Новость успешно добавлена!')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('main:admin_panel')


@require_http_methods(['GET', 'POST'])
@admin_required
@csrf_protect
def edit_news(request, news_id):
    news_item = get_object_or_404(News, pk=news_id)
    if request.method != 'POST':
        return redirect('main:admin_panel')
    news_item.title = request.POST.get('title', '').strip()
    news_item.content = request.POST.get('content', '').strip()
    news_item.is_published = 'is_published' in request.POST
    if 'photo' in request.FILES and request.FILES['photo']:
        path = save_uploaded_file(request.FILES['photo'], 'novosti')
        if path:
            news_item.image_url = path
    try:
        news_item.save()
        messages.success(request, 'Новость успешно обновлена!')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('main:admin_panel')


@admin_required
def delete_news(request, news_id):
    news_item = get_object_or_404(News, pk=news_id)
    if news_item.image_url:
        full = os.path.join(settings.MEDIA_ROOT, news_item.image_url)
        if os.path.isfile(full):
            try:
                os.remove(full)
            except OSError:
                pass
    news_item.delete()
    messages.success(request, 'Новость успешно удалена!')
    return redirect('main:admin_panel')


@admin_required
def admin_admission_periods(request):
    periods = AdmissionPeriod.objects.order_by('-created_at')
    users = User.objects.all()
    applications = CourseApplication.objects.order_by('-created_at')
    return render(request, 'admin.html', {
        'users': users,
        'applications': applications,
        'news_list': News.objects.order_by('-created_at'),
        'admission_periods': periods,
        'message_entry': Message.objects.all(),
        'teachers': Teacher.objects.order_by('order', 'name'),
        'active_tab': 'korea-admission',
        'students_count': _students_count(),
        'admin_count': users.filter(role='admin').count(),
        'new_applications_count': applications.filter(status='new').count(),
    })


@require_POST
@admin_required
@csrf_protect
def add_admission_period(request):
    AdmissionPeriod.objects.create(
        name=request.POST.get('name', ''),
        application_start=request.POST.get('application_start', ''),
        application_end=request.POST.get('application_end', ''),
        studies_start=request.POST.get('studies_start', ''),
        is_active=request.POST.get('is_active') == 'on',
    )
    messages.success(request, 'Период поступления добавлен')
    return redirect('main:admin_admission_periods')


@require_POST
@admin_required
@csrf_protect
def edit_admission_period(request, id):
    period = get_object_or_404(AdmissionPeriod, pk=id)
    period.name = request.POST.get('name', '')
    period.application_start = request.POST.get('application_start', '')
    period.application_end = request.POST.get('application_end', '')
    period.studies_start = request.POST.get('studies_start', '')
    period.is_active = request.POST.get('is_active') == 'on'
    period.save()
    messages.success(request, 'Период поступления обновлен')
    return redirect('main:admin_admission_periods')


@require_POST
@admin_required
@csrf_protect
def delete_admission_period(request, id):
    get_object_or_404(AdmissionPeriod, pk=id).delete()
    messages.success(request, 'Период поступления удален')
    return redirect('main:admin_admission_periods')


@require_http_methods(['GET', 'POST'])
@admin_required
@csrf_protect
def admin_teachers(request):
    if request.method == 'POST':
        if 'add_teacher' in request.POST:
            name = request.POST.get('name', '').strip()
            role = request.POST.get('role', '').strip()
            tags = request.POST.get('tags', '').strip()
            is_founder = 'is_founder' in request.POST
            order = int(request.POST.get('order') or 0)
            photo_path = ''
            if 'photo' in request.FILES and request.FILES['photo']:
                photo_path = save_uploaded_file(request.FILES['photo'], 'teachers') or ''
            Teacher.objects.create(
                name=name, role=role, tags=tags, photo=photo_path,
                is_founder=is_founder, order=order,
            )
            messages.success(request, 'Учитель успешно добавлен')
            return redirect('main:admin_teachers')
        if 'edit_teacher' in request.POST:
            tid = request.POST.get('teacher_id')
            teacher = Teacher.objects.filter(pk=tid).first()
            if teacher:
                teacher.name = request.POST.get('edit_name', '').strip()
                teacher.role = request.POST.get('edit_role', '').strip()
                teacher.tags = request.POST.get('edit_tags', '').strip()
                teacher.is_founder = 'edit_is_founder' in request.POST
                teacher.order = int(request.POST.get('edit_order') or 0)
                if 'photo' in request.FILES and request.FILES['photo']:
                    path = save_uploaded_file(request.FILES['photo'], 'teachers')
                    if path:
                        teacher.photo = path
                teacher.save()
                messages.success(request, 'Учитель успешно обновлен')
            return redirect('main:admin_teachers')

    teachers = Teacher.objects.order_by('order', 'name')
    users = User.objects.all()
    applications = CourseApplication.objects.order_by('-created_at')
    return render(request, 'admin.html', {
        'users': users,
        'applications': applications,
        'news_list': News.objects.order_by('-created_at'),
        'admission_periods': AdmissionPeriod.objects.order_by('-created_at'),
        'message_entry': Message.objects.all(),
        'teachers': teachers,
        'active_tab': 'teachers',
        'students_count': _students_count(),
        'admin_count': users.filter(role='admin').count(),
        'new_applications_count': applications.filter(status='new').count(),
    })


@admin_required
def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, pk=id)
    if teacher.photo:
        full = os.path.join(settings.MEDIA_ROOT, teacher.photo)
        if os.path.isfile(full):
            try:
                os.remove(full)
            except OSError:
                pass
    teacher.delete()
    messages.success(request, 'Учитель успешно удален')
    return redirect('main:admin_teachers')


@require_POST
@admin_required
@csrf_protect
def update_status(request):
    app_id = request.POST.get('application_id')
    new_status = request.POST.get('status')
    if app_id and new_status in ('new', 'contacted', 'approved'):
        app = CourseApplication.objects.filter(pk=app_id).first()
        if app:
            app.status = new_status
            app.save()
            messages.success(request, '✅ Статус обновлен')
            return redirect('main:admin_panel')
    messages.error(request, '❌ Ошибка обновления')
    return redirect('main:admin_panel')


@require_http_methods(['GET', 'POST'])
@csrf_protect
def sign_up(request):
    if request.user.is_authenticated:
        return redirect('main:home')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Этот email уже используется!')
            return render(request, 'sign-up.html', {'form': form})
        try:
            user = User.objects.create_user(
                email=email,
                password=form.cleaned_data['password'],
                name=form.cleaned_data['name'].strip(),
                role='student',
            )
            messages.success(request, 'Регистрация успешна! Теперь войдите в систему.')
            return redirect('main:login')
        except Exception:
            messages.error(request, 'Произошла ошибка при регистрации.')
    return render(request, 'sign-up.html', {'form': form})


@require_http_methods(['GET', 'POST'])
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы!')
        return redirect('main:home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        from django.contrib.auth import authenticate
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user is not None:
            auth_login(request, user)
            request.session['role'] = user.role
            request.session['user_id'] = user.pk
            messages.success(request, f'Добро пожаловать, {user.name}!')
            next_url = request.GET.get('next') or 'main:home'
            return redirect(next_url)
        messages.error(request, 'Неверная почта или пароль')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect('main:login')


@require_POST
@admin_required
@csrf_protect
def delete_message(request, message_id):
    msg = get_object_or_404(Message, pk=message_id)
    msg.delete()
    messages.success(request, 'Сообщение удалено')
    return redirect('main:admin_panel')
