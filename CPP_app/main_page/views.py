import json
import os
from datetime import date, datetime, timedelta

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from .models import News, User, Message, Pig, Breed, EyeColor, Breeding
from django.shortcuts import render, redirect, get_object_or_404
from .forms import (NewsForm, CustomUserCreationForm, PigWDForm,
                    ConfirmDeleteUserForm, ContactForm, ReplyForm,
                    RegistrationForm, ExhibitorCreationForm,
                    PigWZForm, ExhibitorAddPigForm, ExhibitorAddParentPigForm, ExistingPigForm)
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import escape
import html


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


@not_login_required
def register(request):
    if request.method == 'POST':
        registration_type_form = RegistrationForm(request.POST)
        if registration_type_form.is_valid():
            registration_type = registration_type_form.cleaned_data['registration_type']
            if registration_type == 'member':
                return redirect('member_register')
            else:
                return redirect('exhibitor_register')
    else:
        registration_type_form = RegistrationForm()

    return render(request, 'register.html', {'registration_type_form': registration_type_form})


@not_login_required
def member_register(request):
    min_date = datetime.now() - timedelta(days=80 * 365)
    max_date = datetime.now()
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
    return render(request, 'member_register.html', {'form': form,
                                                    'message_sent': message_sent,
                                                    'email': email,
                                                    'min_date': min_date.strftime('%Y-%m-%d'),
                                                    'max_date': max_date.strftime('%Y-%m-%d')
                                                    })


@not_login_required
def exhibitor_register(request):
    min_date = datetime.now() - timedelta(days=80 * 365)
    max_date = datetime.now()
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
    return render(request, 'exhibitor_register.html', {'form': form,
                                                       'message_sent': message_sent,
                                                       'email': email,
                                                       'min_date': min_date.strftime('%Y-%m-%d'),
                                                       'max_date': max_date.strftime('%Y-%m-%d')
                                                       })


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


@login_required
def exhibitor_add_pig(request):
    min_date = datetime.now() - timedelta(days=10 * 365)
    max_date = datetime.now()
    if request.user.role == 'WD':
        template = 'add_pig_wd.html'
    elif request.user.role == 'WZ':
        template = 'add_pig_wz.html'
    elif request.user.role == 'HP':
        return redirect('breeder_add_pig')

    if request.method == 'POST':
        if request.user.role == 'WD':
            form = PigWDForm(request.POST, request.FILES, owner=request.user.id)
        else:
            form = PigWZForm(request.POST, request.FILES, owner=request.user.id)

        if form.is_valid():
            form.save()
            return redirect('exhibitor_my_pigs')
    else:
        if request.user.role == 'WD':
            form = PigWDForm()
        else:
            form = PigWZForm()

    return render(request, template, {'form': form,
                                      'min_date': min_date.strftime('%Y-%m-%d'),
                                      'max_date': max_date.strftime('%Y-%m-%d')})


def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('Main')

    else:
        form = NewsForm()
    return render(request, 'add_news.html', {'form': form})


def exhibitor_my_pigs(request):
    if request.method == 'POST':
        delete_pig_id = request.POST.get('delete_pig_id')
        if delete_pig_id:
            try:
                pig_to_delete = Pig.objects.get(id=delete_pig_id)
                pig_to_delete.delete()
            except Pig.DoesNotExist:
                pass
    user_pigs = Pig.objects.filter(owner=request.user)
    return render(request, 'exhibitor_my_pigs.html', {'user_pigs': user_pigs})


def exhibitor_pig_detail(request, pig_id):
    pig = get_object_or_404(Pig, id=pig_id)

    if request.method == 'POST':
        delete_pig_id = request.POST.get('delete_pig_id', None)
        if delete_pig_id is not None:
            pig.delete()
            return redirect('exhibitor_my_pigs')
    return render(request, 'exhibitor_pig_detail.html', {'pig': pig})


@csrf_protect
@require_POST
def get_parent_pig_info(request):
    if request.method == 'POST':
        selected_pig_name = request.POST.get('pig_name')
        selected_pig_nickname = request.POST.get('pig_nickname')
        selected_pig = get_object_or_404(Pig, name=selected_pig_name, nickname=selected_pig_nickname)
        pig_info = {
            'name': selected_pig.name,
            'nickname': selected_pig.nickname,
            'breed': selected_pig.breed.name,
            'colors': selected_pig.colors,
        }
        if selected_pig.mother and selected_pig.father:
            pig_info['mother_name'] = selected_pig.mother.name
            pig_info['mother_nickname'] = selected_pig.mother.nickname
            pig_info['father_name'] = selected_pig.father.name
            pig_info['father_nickname'] = selected_pig.father.nickname
        return JsonResponse(pig_info)
    else:
        return JsonResponse({'error': 'Invalid request method'})


@csrf_protect
@require_POST
def get_pig_info(request):
    if request.method == 'POST':
        selected_pig_name = request.POST.get('pig_name').strip() if request.POST.get('pig_name') else None
        selected_pig_nickname = request.POST.get('pig_nickname').strip() if request.POST.get('pig_nickname') else None
        selected_pig = Pig.objects.filter(name=selected_pig_name, nickname=selected_pig_nickname).first()
        if selected_pig is not None:
            pig_info = {
                'name': selected_pig.name,
                'nickname': selected_pig.nickname,
                'breed': selected_pig.breed.name,
                'colors': selected_pig.colors,
                'sex': selected_pig.sex,
                'breeder': selected_pig.breeder,
                'birth_date': selected_pig.birth_date if selected_pig.birth_date is not None else None,
                'birth_weight': selected_pig.birth_weight if selected_pig.birth_weight is not None else None,
                'eye_color': selected_pig.eye_color.name if selected_pig.eye_color and selected_pig.eye_color.name is not None else None
            }
            if selected_pig.mother and selected_pig.father:
                pig_info['mother_name'] = selected_pig.mother.name
                pig_info['mother_nickname'] = selected_pig.mother.nickname
                pig_info['father_name'] = selected_pig.father.name
                pig_info['father_nickname'] = selected_pig.father.nickname
            return JsonResponse(pig_info)
        else:
            return JsonResponse({'message': "Pig with the given name and nickname doesn't exist"})
    else:
        return JsonResponse({'error': 'Invalid request method'})


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Breed):
            return obj.name
        elif isinstance(obj, EyeColor):
            return obj.name
        elif isinstance(obj, Breeding):
            return obj.name
        return super().default(obj)

    def decode(self, json_string):
        return json.loads(json_string)


def breeder_add_pig(request):
    parent_forms = [ExhibitorAddParentPigForm(prefix=f'parent_{i}') for i in range(14)]
    pig_form = ExhibitorAddPigForm(prefix='pig')
    existing_pig_form = ExistingPigForm()
    all_male_pigs = [f"{pig.name}   {pig.nickname}" for pig in
                     Pig.objects.filter(sex='Male').exclude(nickname__exact='')]
    all_female_pigs = [f"{pig.name}   {pig.nickname}" for pig in
                       Pig.objects.filter(sex='Female').exclude(nickname__exact='')]
    if request.method == 'POST':
        pig_form = ExhibitorAddPigForm(request.POST, prefix='pig')
        parent_forms = [ExhibitorAddParentPigForm(request.POST, prefix=f'parent_{i}') for i in range(14)]
        existing_pig_form = ExistingPigForm(request.POST)

        if pig_form.is_valid() and all(form.is_valid() for form in parent_forms):
            user_breeding = Breeding.objects.filter(owners=request.user).first()
            pig_form.cleaned_data['owner'] = user_breeding
            data = {
                'exhibitor_pig': pig_form.cleaned_data,
                'exhibitor_parents': [{'id': i + 1, **form.cleaned_data} for i, form in enumerate(parent_forms)]
            }
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # TODO
            json_file_path = os.path.join(base_dir, 'waiting_pig_list.json')
            line_count = 0
            with open(json_file_path, 'r') as json_file:
                lines = json_file.readlines()
                if lines:
                    last_line = json.loads(lines[-1])
                    last_id = last_line.get('id')
                    if last_id is not None:
                        line_count = last_id
                    else:
                        print("Brak klucza 'id' w ostatniej linii.")

            user_name = request.user.username if request.user.is_authenticated else "niezalogowany"
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing_data = []
            with open('waiting_pig_list.json', 'a') as json_file:
                existing_data.append(data)
                line_count += 1
                json_data = json.dumps({
                    'id': line_count,
                    'user_name': user_name,
                    'timestamp': current_date,
                    'data': data
                }, cls=CustomJSONEncoder)

                json_file.write(json_data + '\n')
        else:
            print("Formularz nie jest poprawny. Sprawdź błędy:")
            for field, errors in pig_form.errors.items():
                print(f"{field}: {', '.join(errors)}")
    return render(request, 'breeder_add_pig.html', {'parent_forms': parent_forms,
                                                    'pig_form': pig_form,
                                                    'existing_pig_form': existing_pig_form,
                                                    'all_male_pigs': all_male_pigs,
                                                    'all_female_pigs': all_female_pigs})


def display_waiting_pigs(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # TODO
    json_file_path = os.path.join(base_dir, 'waiting_pig_list.json')
    data = []
    with open(json_file_path, 'r') as json_file:
        for line in json_file:
            try:
                row_data = json.loads(line)
                pig_id = row_data.get('id')
                adding = row_data.get('user_name')
                timestamp = row_data.get('timestamp')
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                pig_name = row_data.get('data', {}).get('exhibitor_pig', {}).get('name')
                pig_nickname = row_data.get('data', {}).get('exhibitor_pig', {}).get('nickname')

                data.append((pig_id, pig_name, pig_nickname, adding, timestamp))
            except json.JSONDecodeError as e:
                return render(request, 'json_error.html', {'error_message': str(e)})

    data.sort(key=lambda x: x[4], reverse=False)

    return render(request, 'waiting_pig_list.html', {'waiting_pigs': data})


# def display_waiting_pig_details(request, pig_id):
#     parent_forms = [ExhibitorAddParentPigForm(prefix=f'parent_{i}') for i in range(14)]
#     pig_form = ExhibitorAddPigForm(prefix='pig')
#
#     with open('waiting_pig_list.json', 'r') as json_file:
#         for line in json_file:
#             try:
#                 row_data = json.loads(line)
#                 current_pig_id = row_data.get('id')
#
#                 if current_pig_id == pig_id:
#                     return render(request, 'waiting_pig_list_details.html', {'parent_forms': parent_forms,
#                                                                              'pig_form': pig_form,
#                                                                              'pig_data': row_data})
#             except json.JSONDecodeError as e:
#                 return render(request, 'json_error.html', {'error_message': str(e)})
#
#     return HttpResponse("Nie znaleziono świńki o podanym ID.")


def add_parent_pig(pig_data, sex, mother, father):
    print(pig_data)
    pig_info = Pig.objects.filter(name=pig_data['name'], nickname=pig_data['nickname'], breed=pig_data['breed']).first()
    if mother:
        mother_data = Pig.objects.filter(name=mother['name'], nickname=mother['nickname'], breed=mother['breed']).first()
    else:
        mother_data = None
    if father:
        father_data = Pig.objects.filter(name=father['name'], nickname=father['nickname'], breed=father['breed']).first()
    else:
        father_data = None
    if pig_info:
        if pig_info.mother and pig_info.father:
            print("Świnka ma dodanych rodziców")
        if father_data and mother_data:
            pig_info.mother = mother_data
            pig_info.father = father_data
            pig_info.save()
    else:
        if mother and father:
            pig = Pig(
                name=pig_data['name'],
                nickname=pig_data['nickname'],
                sex=sex,
                breed=pig_data['breed'],
                colors=pig_data['colors'],
                mother=mother_data,
                father=father_data,
            )
            pig.save()
        else:
            pig = Pig(
                name=pig_data['name'],
                nickname=pig_data['nickname'],
                sex=sex,
                breed=pig_data['breed'],
                colors=pig_data['colors'],
            )
            pig.save()


def add_pig(pig_data, mother, father):
    pig_info = Pig.objects.filter(name=pig_data['name'], nickname=pig_data['nickname'], breed=pig_data['breed']).first()
    if mother:
        mother_data = Pig.objects.filter(name=mother['name'], nickname=mother['nickname'], breed=mother['breed']).first()
    else:
        mother_data = None
    if father:
        father_data = Pig.objects.filter(name=father['name'], nickname=father['nickname'], breed=father['breed']).first()
    else:
        father_data = None
    if pig_info:
        if not pig_info.mother and not pig_info.father:
            pig_info.mother = mother_data
            pig_info.father = father_data
        if not pig_info.birth_date:
            pig_info.birth_date = pig_data['birth_date']
        if not pig_info.birth_weight:
            pig_info.birth_weight = pig_data['birth_weight']
        if not pig_info.eye_color:
            pig_info.eye_color = pig_data['eye_color']
        if not pig_info.owner:
            pig_info.owner = pig_data['owner']
        if not pig_info.breeder:
            pig_info.breeder = pig_data['breeder']
        pig_info.save()
    else:
        if mother and father:
            pig = Pig(
                name=pig_data['name'],
                nickname=pig_data['nickname'],
                sex=pig_data['sex'],
                breed=pig_data['breed'],
                colors=pig_data['colors'],
                mother=mother_data,
                father=father_data,
                birth_date=pig_data['birth_date'],
                birth_weight=pig_data['birth_weight'],
                eye_color=pig_data['eye_color'],
                breeder=pig_data['breeder'],
                owner=pig_data['owner'],
            )
            pig.save()
        else:
            pig = Pig(
                name=pig_data['name'],
                nickname=pig_data['nickname'],
                sex=pig_data['sex'],
                breed=pig_data['breed'],
                colors=pig_data['colors'],
                birth_date=pig_data['birth_date'],
                birth_weight=pig_data['birth_weight'],
                eye_color=pig_data['eye_color'],
                breeder=pig_data['breeder'],
                owner=pig_data['owner'],
            )
            pig.save()


def display_waiting_pig_details(request, pig_id):
    parent_forms = [ExhibitorAddParentPigForm(prefix=f'parent_{i}') for i in range(14)]
    pig_form = ExhibitorAddPigForm(prefix='pig')
    if request.method == 'POST':
        pig_form = ExhibitorAddPigForm(request.POST, prefix='pig')
        parent_forms = [ExhibitorAddParentPigForm(request.POST, prefix=f'parent_{i}') for i in range(14)]
        if pig_form.is_valid() and all(form.is_valid() for form in parent_forms):
            pig_data = pig_form.cleaned_data
            parent_data = [form.cleaned_data for form in parent_forms]
            parents_complete = [
                parent_data[i]['name'] != '' and
                parent_data[i]['nickname'] != '' and
                parent_data[i]['breed'] is not None and
                parent_data[i]['colors'] != "['','','','','']"
                for i in range(14)
            ]
            for i in range(14):
                if not parents_complete[i]:
                    parent_data[i] = None

            pig_info = Pig.objects.filter(name=pig_data['name'],
                                          nickname=pig_data['nickname'],
                                          breed=pig_data['breed']).first()

            if pig_info and pig_info.owner != '' and pig_info.owner is not None and pig_info.owner != pig_data.get('owner'):
                    print("Edytujący świnkę nie jest jej właścicielem")
                    print("Nie można edytować nie swojej świnki")
                    print("Należy wysłać użytkownikowi maila z informacją o właścicielu")  #TODO
            else:
                if parents_complete[0] and parents_complete[1]:
                    if parents_complete[2] and parents_complete[3]:
                        if parents_complete[6] and parents_complete[7]:
                            add_parent_pig(parent_data[6], 'Female')
                            add_parent_pig(parent_data[7], 'Male')
                        if parents_complete[8] and parents_complete[9]:
                            add_parent_pig(parent_data[8], 'Female')
                            add_parent_pig(parent_data[9], 'Male')
                        add_parent_pig(parent_data[2], 'Female', parent_data[6], parent_data[7])
                        add_parent_pig(parent_data[3], 'Male', parent_data[8], parent_data[9])
                    if parents_complete[4] and parents_complete[5]:
                        if parents_complete[10] and parents_complete[11]:
                            add_parent_pig(parent_data[10], 'Female')
                            add_parent_pig(parent_data[11], 'Male')
                        if parents_complete[12] and parents_complete[13]:
                            add_parent_pig(parent_data[12], 'Female')
                            add_parent_pig(parent_data[13], 'Male')
                        add_parent_pig(parent_data[4], 'Female', parent_data[10], parent_data[11])
                        add_parent_pig(parent_data[5], 'Male', parent_data[12], parent_data[13])
                    add_parent_pig(parent_data[0], 'Female', parent_data[2], parent_data[3])
                    add_parent_pig(parent_data[1], 'Male', parent_data[4], parent_data[5])
                add_pig(pig_data, parent_data[0], parent_data[1])
            print("Można usunąć wiersz z pliku json") #TODO
            return redirect('waiting_pig_list')
        else:
            print("Pig form is not valid")
    with open('waiting_pig_list.json', 'r') as json_file:
        for line in json_file:
            try:
                row_data = json.loads(line)

                current_pig_id = row_data.get('id')

                if current_pig_id == pig_id:
                    return render(request, 'waiting_pig_list_details.html', {'parent_forms': parent_forms,
                                                                             'pig_form': pig_form,
                                                                             'pig_data': row_data})
            except json.JSONDecodeError as e:
                return render(request, 'json_error.html', {'error_message': str(e)})

    return render(request, 'waiting_pig_list_details.html', {'parent_forms': parent_forms, 'pig_form': pig_form})


@method_decorator(csrf_exempt, name='dispatch')
class delete_waiting_pig(View):
    def post(self, request, *args, **kwargs):
        try:
            pig_id_to_remove = request.POST.get('pig_id')

            if not pig_id_to_remove.isdigit():
                raise ValueError('Nieprawidłowe pig_id.')

            pig_id_to_remove = int(pig_id_to_remove)

            with open('waiting_pig_list.json', 'r') as json_file, open('temp_waiting_pig_list.json',
                                                                       'w') as temp_file:
                for line in json_file:
                    try:
                        row_data = json.loads(line)
                        current_pig_id = row_data.get('id')

                        if current_pig_id != pig_id_to_remove:
                            temp_file.write(json.dumps(row_data) + '\n')
                    except json.JSONDecodeError as e:
                        return JsonResponse({'status': 'error', 'error_message': str(e)})

            with open('waiting_pig_list.json', 'w') as json_file:
                json_file.writelines(open('temp_waiting_pig_list.json').readlines())

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error_message': str(e)})

