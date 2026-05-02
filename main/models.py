from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('role', 'admin')
        return self.create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True, max_length=120)
    name = models.CharField('Имя', max_length=120)
    role = models.CharField('Роль', max_length=20, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    @property
    def is_admin(self):
        return self.role == 'admin'

    def save(self, *args, **kwargs):
        self.is_staff = self.role == 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class CountStudents(models.Model):
    count_students = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Счётчик студентов'
        verbose_name_plural = 'Счётчики студентов'


class CourseApplication(models.Model):
    course_type = models.CharField(max_length=20)
    applicant_name = models.CharField(max_length=100)
    applicant_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на курс'
        verbose_name_plural = 'Заявки на курсы'
        db_table = 'course_applications'


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']


class AdmissionPeriod(models.Model):
    name = models.CharField(max_length=100)
    application_start = models.CharField(max_length=50)
    application_end = models.CharField(max_length=50)
    studies_start = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Период поступления'
        verbose_name_plural = 'Периоды поступления'
        ordering = ['-created_at']


class Message(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.CharField(max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=300, blank=True)
    is_founder = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',')] if self.tags else []

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['order', 'name']
