from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

_attrs = {'class': 'form-control'}


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={**_attrs, 'placeholder': 'Введите ваш email'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={**_attrs, 'placeholder': 'Введите пароль'}))

    def clean_email(self):
        return self.cleaned_data.get('email', '').lower().strip()


class RegistrationForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=120, widget=forms.TextInput(attrs={**_attrs, 'placeholder': 'Введите ваше ФИО'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={**_attrs, 'placeholder': 'Введите ваш email'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={**_attrs, 'placeholder': 'Введите пароль'}), min_length=6)
    confirm = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput(attrs={**_attrs, 'placeholder': 'Повторите пароль'}))

    def clean_email(self):
        return self.cleaned_data.get('email', '').lower().strip()

    def clean(self):
        data = super().clean()
        if data.get('password') != data.get('confirm'):
            raise forms.ValidationError('Пароли не совпадают')
        return data


class CourseApplicationForm(forms.Form):
    course_type = forms.CharField(label='Тип курса', max_length=20, widget=forms.TextInput(attrs=_attrs))
    name = forms.CharField(label='Имя', max_length=100, widget=forms.TextInput(attrs=_attrs))
    phone = forms.CharField(label='Телефон', max_length=20, widget=forms.TextInput(attrs=_attrs))
    submit = forms.CharField(widget=forms.HiddenInput(), required=False)


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=100, widget=forms.TextInput(attrs=_attrs))
    phone = forms.CharField(label='Телефон', max_length=20, widget=forms.TextInput(attrs=_attrs))
    message = forms.CharField(label='Сообщение', widget=forms.Textarea(attrs={**_attrs, 'rows': 4}), max_length=800)
