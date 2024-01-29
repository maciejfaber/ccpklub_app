import json
import os
from datetime import date, datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.detail import SingleObjectMixin

from .models import News, User, Message, Pig, Breed, EyeColor, Breeding
from django.shortcuts import render, redirect, get_object_or_404
from .forms import (NewsForm, CustomUserCreationForm, PigWDForm,
                    ContactForm, ReplyForm,
                    RegistrationForm, ExhibitorCreationForm,
                    PigWZForm, ExhibitorAddPigForm, ExhibitorAddParentPigForm, ExistingPigForm, BreedingForm,
                    UserActionForm)
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DetailView, FormView, CreateView
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def not_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Main')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self, queryset=None):
        return self.request.user


class MainView(ListView):
    model = News
    queryset = News.objects.all().order_by('-creation_date')


class RegisterView(FormView):
    template_name = 'main_page/register_form.html'
    form_class = RegistrationForm

    @method_decorator(not_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        registration_type = form.cleaned_data['registration_type']
        if registration_type == 'member':
            return redirect('member_register')
        else:
            return redirect('exhibitor_register')


class MemberRegisterView(FormView):
    template_name = 'main_page/member_register.html'
    form_class = CustomUserCreationForm

    @method_decorator(not_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        context = {'success_message': email}
        return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ExhibitorRegisterView(FormView):
    template_name = 'main_page/exhibitor_register.html'
    form_class = ExhibitorCreationForm

    @method_decorator(not_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        context = {'success_message': email}
        return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('Main')
    success_message = 'Zalogowano pomyślnie.'

    @method_decorator(not_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required
def logout_view(request):
    logout(request)
    return redirect('Main')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'main_page/change_password.html'
    success_url = reverse_lazy('my_profile')


class InactiveUserListView(LoginRequiredMixin, ListView):
    model = User
    queryset = User.objects.filter(is_active=False)
    template_name = 'main_page/inactive_user_list.html'
    context_object_name = 'inactive_users'


class UserDetailsView(LoginRequiredMixin, DetailView, FormView):

    model = User
    template_name = 'user_details.html'
    context_object_name = 'user'
    form_class = UserActionForm

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, id=user_id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return self.render_to_response(self.get_context_data(object=self.object, form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        print(form)
        print(self.form_valid(form))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = self.get_object()
        action = form.cleaned_data['action']
        email_content = form.cleaned_data['email_content']
        subject = ''
        message = ''
        if action == 'accept':
            user.is_active = True
            user.registration_number = self.generate_registration_number()
            user.save()
            subject = 'Twój konto został zaakceptowany'
            message = (f'Twoje konto na stronie zostało zaakceptowane. Twój login to: '
                       f'"{user.username}" Możesz się teraz zalogować używając hasła podanego podczas rejestracji.\n'
                       f'{email_content}')
        elif action == 'delete':
            user.delete()
            subject = 'Twój konto został usunięte'
            message = (f'Twoje konto na stronie zostało usunięte.\n'
                       f'{email_content}')

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return HttpResponseRedirect(reverse_lazy('inactive_user_list'))

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


class ContactView(FormView):
    template_name = "contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        form.save()
        context = {'message_sent': True}
        return self.render_to_response(context)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'message_list.html'
    context_object_name = 'messages'
    ordering = ['-timestamp']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_messages_count'] = Message.objects.filter(reply_sent=False).count()
        context['total_messages_count'] = Message.objects.count()
        return context


class ReplyOrDetailMessageView(LoginRequiredMixin, FormView):
    template_name = 'reply_or_detail_message.html'
    form_class = ReplyForm
    success_url = reverse_lazy('message_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message_id = self.kwargs['message_id']
        context['original_message'] = get_object_or_404(Message, pk=message_id)
        return context

    def form_valid(self, form):
        original_message = get_object_or_404(Message, pk=self.kwargs['message_id'])
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

        return super().form_valid(form)


class AddNewsView(LoginRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'add_news.html'
    success_url = reverse_lazy('Main')


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
            form = PigWDForm(request.POST, request.FILES, owner=request.user)
        else:
            form = PigWZForm(request.POST, request.FILES, owner=request.user)

        if form.is_valid():
            form.save()
            return redirect('exhibitor_my_pigs')
    else:
        if request.user.role == 'WD':
            form = PigWDForm(owner=request.user)
        else:
            form = PigWZForm(owner=request.user)

    return render(request, template, {'form': form,
                                      'min_date': min_date.strftime('%Y-%m-%d'),
                                      'max_date': max_date.strftime('%Y-%m-%d')})


class ExhibitorMyPigsView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Pig
    template_name = 'exhibitor_my_pigs.html'
    context_object_name = 'user_pigs'

    def get(self, request, *args, **kwargs):
        user_pigs = Pig.objects.filter(owner=self.request.user, is_active=True)
        return render(request, self.template_name, {self.context_object_name: user_pigs})

    def post(self, request, *args, **kwargs):
        delete_pig_id = request.POST.get('delete_pig_id')
        if delete_pig_id:
            pig_to_delete = get_object_or_404(Pig, id=delete_pig_id, owner=self.request.user)
            pig_to_delete.is_active = False
            pig_to_delete.save()
            messages.success(request, 'Świnia została usunięta.')
        else:
            messages.error(request, 'Nie udało się usunąć świnii.')

        return redirect(reverse_lazy('exhibitor_my_pigs'))


class ExhibitorPigDetailView(LoginRequiredMixin, View):
    template_name = 'exhibitor_pig_detail.html'

    def get(self, request, pig_id):
        pig = get_object_or_404(Pig, id=pig_id)
        return render(request, self.template_name, {'pig': pig})

    def post(self, request, pig_id):
        pig = get_object_or_404(Pig, id=pig_id)
        delete_pig_id = request.POST.get('delete_pig_id', None)

        if delete_pig_id is not None:
            pig.is_active = False
            pig.save()
            return redirect('exhibitor_my_pigs')

        return render(request, self.template_name, {'pig': pig})


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


@login_required
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
            user_breeding = Breeding.objects.filter(owners=request.user).values('name').first()
            pig_form.cleaned_data['owner'] = user_breeding['name']
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


@login_required
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


def add_parent_pig(pig_data, sex, mother, father):
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
    breeding = Breeding.objects.filter(name=pig_data['owner']).values('owners')
    owner_ids = [item['owners'] for item in breeding]
    owners = User.objects.filter(id__in=owner_ids)
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
        if not pig_info.breeder:
            pig_info.breeder = pig_data['breeder']
        if not pig_info.owner:
            pig_info.save()
            for owner in owners:
                pig_info.owner.add(owner)
        else:
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
                is_in_breeding=True
            )
            pig.save()
            for owner in owners:
                pig.owner.add(owner)
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
                is_in_breeding=True
            )
            pig.save()
            for owner in owners:
                pig.owner.add(owner)


@login_required
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

            if pig_info and pig_info.owner.all().exists() and pig_info.owner != pig_data.get('owner'):
                    print("Edytujący świnkę nie jest jej właścicielem")
                    print("Nie można edytować nie swojej świnki")
                    print("Należy wysłać użytkownikowi maila z informacją o właścicielu")  #TODO
            else:
                if parents_complete[0] and parents_complete[1]:
                    if parents_complete[2] and parents_complete[3]:
                        if parents_complete[6] and parents_complete[7]:
                            add_parent_pig(parent_data[6], 'Female', None, None)
                            add_parent_pig(parent_data[7], 'Male', None, None)
                        if parents_complete[8] and parents_complete[9]:
                            add_parent_pig(parent_data[8], 'Female', None, None)
                            add_parent_pig(parent_data[9], 'Male', None, None)
                        add_parent_pig(parent_data[2], 'Female', parent_data[6], parent_data[7])
                        add_parent_pig(parent_data[3], 'Male', parent_data[8], parent_data[9])
                    if parents_complete[4] and parents_complete[5]:
                        if parents_complete[10] and parents_complete[11]:
                            add_parent_pig(parent_data[10], 'Female', None, None)
                            add_parent_pig(parent_data[11], 'Male', None, None)
                        if parents_complete[12] and parents_complete[13]:
                            add_parent_pig(parent_data[12], 'Female', None, None)
                            add_parent_pig(parent_data[13], 'Male', None, None)
                        add_parent_pig(parent_data[4], 'Female', parent_data[10], parent_data[11])
                        add_parent_pig(parent_data[5], 'Male', parent_data[12], parent_data[13])
                    add_parent_pig(parent_data[0], 'Female', parent_data[2], parent_data[3])
                    add_parent_pig(parent_data[1], 'Male', parent_data[4], parent_data[5])
                add_pig(pig_data, parent_data[0], parent_data[1])
            print("Można usunąć wiersz z pliku json") #TODO
            try:
                pig_id = int(pig_id)
                with open('waiting_pig_list.json', 'r') as json_file, open('temp_waiting_pig_list.json', 'w') as temp_file:
                    for line in json_file:
                        try:
                            row_data = json.loads(line)
                            current_pig_id = row_data.get('id')
                            if current_pig_id != pig_id:
                                temp_file.write(json.dumps(row_data) + '\n')
                        except json.JSONDecodeError as e:
                            return JsonResponse({'status': 'error', 'error_message': str(e)})
                with open('waiting_pig_list.json', 'w') as json_file:
                    json_file.writelines(open('temp_waiting_pig_list.json').readlines())
            except Exception as e:
                return JsonResponse({'status': 'error', 'error_message': str(e)})
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


class add_breeding(View):
    message_sent = False
    def get(self, request):
        form = BreedingForm(request=request)
        return render(request, 'add_breeding.html', {'form': form})

    def post(self, request, message_sent=None):
        form = BreedingForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            message_sent = True
        return render(request, 'add_breeding.html', {'form': form, 'message_sent': message_sent})


class BreederMyPigsView(LoginRequiredMixin, ListView):
    model = Pig
    template_name = 'breeder_my_pigs.html'
    context_object_name = 'user_pigs'

    def get_queryset(self):
        return Pig.objects.filter(owner=self.request.user, is_active=True)


class BreederPigDetailView(LoginRequiredMixin, DetailView):
    model = Pig
    template_name = 'breeder_pig_detail.html'
    context_object_name = 'pig'

    def post(self, request, *args, **kwargs):
        delete_pig_id = request.POST.get('delete_pig_id', None)
        if delete_pig_id is not None:
            pig = self.get_object()
            pig.is_active = False
            pig.dave()
            return redirect('breeder_my_pigs')
        return super().get(request, *args, **kwargs)