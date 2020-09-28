from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.generic import CreateView, FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.utils.http import is_safe_url
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from datetime import datetime

from .forms import LoginForm, RegisterForm, GuestForm, ProfileForm
from .models import User, Profile, Photographer


@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('/'))

# class LoginView(FormView):
#     form_class = LoginForm
#     template_name = "accounts/login.html"
#     success_url = '/'
#     def form_valid(self):
#         request = self.request
#         next_ = request.GET.get('next')
#         next_post = request.POST.get('next')
#         redirect_path = next_ or next_post or None
#         username  = form.cleaned_data.get("username")
#         password  = form.cleaned_data.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             try:
#                 del request.session['guest_email_id']
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect("/")
#         return super(LoginView,self).form_invalid()
#

# Working. replace register_page and swap the class with reg page in project url
# class RegisterView(CreateView):
#     form_class = RegisterForm
#     template_name = "accounts/register.html"
#     success_url = '/login/'

def index(request):
    form = LoginForm(request.POST or None)
    context = {
        "form": form, 'namespace':'accounts',
        'site_key': settings.RECAPTCHA_SITE_KEY,
    }

    return render(request, 'index.html', context)


# Will be replaced by the classbase LoginView when the bug is fixed
def login_page(request):

    form = LoginForm(request.POST or None)
    context = {
        "form": form, 'namespace':'accounts',
        # 'site_key': settings.RECAPTCHA_SITE_KEY,
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    # if redirect_path == '/': redirect_path = '/dashboard/'

    # g-recaptcha
    # secret_key = settings.RECAPTCHA_SECRET_KEY
    # captcha verification
    # data = {
        # 'response': data.get('g-recaptcha-response'),
        # 'rsponse': token,
        # 'secret': secret_key
    # }

    # resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    # result_json = resp.json()
    # print("token = ",token)
    # print(result_json)

    if form.is_valid():
        username  = form.cleaned_data.get("username")
        password  = form.cleaned_data.get("password")
        token_id = request.POST.get('token_id')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            try:
                del request.session['guest_email_id']
            except:
                pass

            if is_safe_url(redirect_path, request.get_host()):
                return redirect("/detail/myphoto_browse_spc/?role=pri&display=checked")
                # return redirect(redirect_path)
            else:
                return redirect("/?role=pri&att=")
                # return redirect("dashboard/")
        else:
            # Return an 'invalid login' error message.
            print("LOGIN FAIL:  Someone is trying to login and failed!")
            print("LOGIN FAIL:  Username: {} and password: {}".format(username, password))
            return HttpResponse("invalid username or password")
    else:
        return render(request, "accounts/login.html", context)


def register_page(request):
    registered = False
    if request.method == "POST":
        user_form = RegisterForm(request.POST or None)
        profile_form = ProfileForm(request.POST or None)
        # context = {
        #     "user_form": user_form,
        #     "profile_form": profile_form,
        #     "registered":registered, 'namespace':'accounts',
        # }
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            # user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # if 'profile_pic' in request.FILES:
            #     profile.profile_pic = request.FILES['profile_pic']

            profile.save()
            registered = True
            return redirect('login')
        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = RegisterForm()
        profile_form = ProfileForm()

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "registered": registered, 'namespace':'accounts',
    }
    return render(request, "accounts/register.html", context)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form, 'namespace':'accounts',
    })


def update_profile(request):
    user = request.user
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    myprofile = Profile.objects.get(user=user)
    print("myprofile = ",myprofile)
    # print ("my id = ",myprofile.user_id)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile_obj = form.save(commit=False)
            profile_obj.created_date = myprofile.created_date
            print("my profile = ",profile_obj.photo_credit_name)
            print("current    = ",profile_obj.current_credit_name)
            print("user name = ",user.username)
            profile_obj.id = myprofile.id
            profile_obj.user = user
            profile_obj.save()
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        # foto = Photographer.objects.get(user_id=user)
        form = ProfileForm(instance=myprofile)
    context = {'form':form,'namespace':'accounts'}
    return render(request, 'accounts/update_profile.html', context)
    # return render(request, 'accounts/register.html',context)
