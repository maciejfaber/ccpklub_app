from datetime import date
from django.http import HttpResponse
from django.template import loader
from .models import News, User, Message
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewsForm, CustomUserCreationForm, ConfirmDeleteUserForm, ContactForm, ReplyForm, RegistrationAsForm, ExhibitorCreationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@login_required
def my_profile(request):
    user = request.user
    return render(request, 'my_profile.html', {'user': user})


def not_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Main')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def not_admin_user(user):
    return not user.is_superuser


def main(request):
    if request.user.is_authenticated and 'logout' in request.path:
        messages.success(request, "Zostałeś wylogowany.")
        return redirect('logout')
    elif request.user.is_authenticated:
        template = loader.get_template('main.html')
        news_list = News.objects.all().order_by('-creation_date')
        context = {'news_list': news_list,
                   'first_name': request.user.first_name,
                   'last_name': request.user.last_name}
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('main.html')
        news_list = News.objects.all().order_by('-creation_date')
        context = {'news_list': news_list}
        return HttpResponse(template.render(context, request))


@login_required(login_url='Main')
def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('Main')
    else:
        form = NewsForm()
    return render(request, 'add_news.html', {'form': form})


@not_login_required
def register_as(request):
    if request.method == 'POST':
        registration_type_form = RegistrationAsForm(request.POST)
        if registration_type_form.is_valid():
            registration_type = registration_type_form.cleaned_data['registration_type']
            if registration_type == 'member':
                return redirect('register')
            else:
                return redirect('exhibitor_register')
    else:
        registration_type_form = RegistrationAsForm()

    return render(request, 'register_as.html', {'registration_type_form': registration_type_form})


@not_login_required
def register(request):
    message_sent = False
    email = None
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            form.save()
            message_sent = True
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form, 'message_sent': message_sent, 'email': email})


@not_login_required
def exhibitor_register(request):
    message_sent = False
    email = None
    if request.method == 'POST':
        form = ExhibitorCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            form.save()
            message_sent = True
    else:
        form = ExhibitorCreationForm()
    return render(request, 'exhibitor_register.html', {'form': form, 'message_sent': message_sent, 'email': email})


@not_login_required
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Main')
        else:
            messages.error(request, 'Nazwa użytkownika lub hasło są niepoprawne!')
    return render(request, 'login.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Zaktualizuj sesję użytkownika
            messages.success(request, 'Twoje hasło zostało zmienione.')
            return redirect('my_profile')  # Przekierowanie na stronę "Moje dane" lub inną stronę
        else:
            messages.error(request, 'Proszę popraw błędy w formularzu.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


class InactiveUserListView(View):
    template_name = 'inactive_user_list.html'

    def get(self, request):
        inactive_users = User.objects.filter(is_active=False)
        return render(request, self.template_name, {'inactive_users': inactive_users})


class UserDetailsView(View):
    template_name = 'user_details.html'

    @staticmethod
    def generate_registration_number():
        current_year = date.today().year
        last_user = (User.objects.filter(registration_number__startswith=f'CCP/M/{current_year}/')
                     .order_by('-registration_number').first())
        if last_user:
            last_number = int(last_user.registration_number.split('/')[-1])
            new_number = str(last_number + 1).zfill(3)

        else:
            new_number = '001'

        return f'CCP/M/{current_year}/{new_number}'

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return render(request, self.template_name, {'user': user})

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        action = request.POST.get('action')

        if action == 'accept':
            user.is_active = True
            user.save()

            # Wysyłanie e-maila po zaakceptowaniu użytkownika
            subject = 'Twój konto został zaakceptowany'
            message = (f'Twoje konto na stronie zostało zaakceptowane. Twój login to: '
                       f'"{user.username}" Możesz się teraz zalogować używając hasła podanego podczas rejestracji.')
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return redirect('inactive_user_list')
        elif action == 'delete':
            return redirect('confirm_delete_user', user_id=user.id)


class ConfirmDeleteUserView(View):
    template_name = 'confirm_delete_user.html'

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        form = ConfirmDeleteUserForm()
        return render(request, self.template_name, {'user': user, 'form': form})

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        form = ConfirmDeleteUserForm(request.POST)

        if form.is_valid():
            # Pobierz powód usunięcia z formularza
            reason_for_deletion = form.cleaned_data['reason_for_deletion']

            # Wysyłanie e-maila z powodem usunięcia
            subject = 'Twoje konto zostało usunięte'
            message = f'Twoje konto na stronie zostało usunięte z powodu: {reason_for_deletion}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Usunięcie użytkownika
            user.delete()

            return redirect('inactive_user_list')

        return render(request, self.template_name, {'user': user, 'form': form})


def contact(request):
    message_sent = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            form = ContactForm()
            message_sent = True
    else:
        form = ContactForm()

    return render(request, 'contact_form.html', {'form': form, 'message_sent': message_sent})


def message_list(request):
    messages = Message.objects.all().order_by('-timestamp')
    unread_messages_count = Message.objects.filter(reply_sent=False).count()
    total_messages_count = messages.count()

    return render(request, 'message_list.html', {'messages': messages,
                                                 'unread_messages_count': unread_messages_count,
                                                 'total_messages_count': total_messages_count})


def reply_or_detail_message(request, message_id):
    original_message = get_object_or_404(Message, pk=message_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            recipient_list = [original_message.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            html_content = render_to_string('email.html',
                                            {'title': title, 'content': content,
                                             'original_message': original_message})
            if send_mail(title, '', from_email, recipient_list, html_message=html_content, fail_silently=False):
                original_message.reply_sent = True
                original_message.save()

            return redirect('message_list')
    else:
        form = ReplyForm()

    return render(request, 'reply_or_detail_message.html', {'form': form, 'original_message': original_message})
