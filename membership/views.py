# payments/views.py
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django import template
from PIL import Image, ExifTags
from io import BytesIO
from django.db.models import Q
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse, reverse_lazy
from django.template import RequestContext
from itertools import chain

from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from detail.views import getmyphotos, get_random_img
from orchidlist.views import mypaginator

import stripe # new
import json
import string
import pytz
import django.shortcuts
import random
import os, shutil

from django.apps import apps
Genus = apps.get_model('orchiddb', 'Genus')
Genusacc = apps.get_model('orchiddb', 'Genusacc')
Intragen = apps.get_model('orchiddb', 'Intragen')
Species = apps.get_model('orchiddb', 'Species')
Hybrid = apps.get_model('orchiddb', 'Hybrid')
Accepted = apps.get_model('orchiddb', 'Accepted')
Synonym = apps.get_model('orchiddb', 'Synonym')
Comment = apps.get_model('orchiddb', 'Comment')

Subgenus = apps.get_model('orchiddb', 'Subgenus')
Section = apps.get_model('orchiddb', 'Section')
Subsection = apps.get_model('orchiddb', 'Subsection')
Series = apps.get_model('orchiddb', 'Series')
Family = apps.get_model('orchiddb', 'Family')
Subfamily = apps.get_model('orchiddb', 'Subfamily')
Tribe = apps.get_model('orchiddb', 'Tribe')
Subtribe = apps.get_model('orchiddb', 'Subtribe')
Distribution = apps.get_model('orchiddb', 'Distribution')
Region = apps.get_model('orchiddb', 'Region')
Subregion = apps.get_model('orchiddb', 'Subregion')
GeoLoc = apps.get_model('orchiddb', 'GeoLoc')
SpcImages = apps.get_model('orchiddb', 'SpcImages')
HybImages = apps.get_model('orchiddb', 'HybImages')
UploadFile = apps.get_model('orchiddb', 'UploadFile')
SpcImgHistory = apps.get_model('orchiddb', 'SpcImgHistory')
HybImgHistory = apps.get_model('orchiddb', 'HybImgHistory')
Photographer = apps.get_model('accounts', 'Photographer')
AncestorDescendant = apps.get_model('orchiddb', 'AncestorDescendant')
ReidentifyHistory = apps.get_model('orchiddb', 'ReidentifyHistory')
User = get_user_model()

imgdir = 'utils/images/'
hybdir = imgdir + 'hybrid/'
spcdir = imgdir + 'species/'
alpha_list = string.ascii_uppercase


from django.apps import apps
Species     = apps.get_model('orchiddb', 'Species')
Hybrid      = apps.get_model('orchiddb', 'Hybrid')
Accepted      = apps.get_model('orchiddb', 'Accepted')
HybImages   = apps.get_model('orchiddb', 'HybImages')
SpcImages   = apps.get_model('orchiddb', 'SpcImages')
Photographer   = apps.get_model('accounts', 'Photographer')


stripe.api_key = settings.STRIPE_SECRET_KEY # new
amount = 2000
amount_display = f'{amount/100:.2f}'
# donateamt = 0
# donateamt_display = f'{donateamt/100:.2f}'


#--- Membership Fee

class PaymentView(TemplateView):
    template_name = 'membership/membershipapp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['amount'] = amount
        context['amount_display'] = amount_display
        return context


def charge(request): # new
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        context = {'amount_display':amount_display,'namespace':'membership',}
        return render(request, 'membership/charge.html',context)

    return HttpResponseRedirect('/')

# Using Django
def my_webhook_view(request):
    # Retrieve the request's body and parse it as JSON:
    event_json = json.loads(request.body)

    # Do something with event_json

    # Return a response to acknowledge receipt of the event
    return HttpResponse(status=200)

class DonateView(TemplateView):
    template_name = 'membership/donateapp.html'
    donateamt = 1000
    donateamt_display = f'{donateamt / 100:.2f}'

    # def get(self, request, *args, **kwargs):
    #     context['donateamt'] = kwargs['donateamt']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['donateamt'] = 0
        context['donateamt_display'] = 0
        if kwargs:
            context['donateamt'] = kwargs['donateamt']
            context['donateamt_display'] = f'{ context["donateamt"] / 100:.2f}'
        return context

def donate(request,donateamt=None): # new
    donateamt_display = ''
    if donateamt:
        donateamt_display = f'{donateamt / 100:.2f}'
    # if request.GET.get('donateamt'):
    #     donateamt_display = request.GET['donateamt']
        # donateamt_display = f'{request.GET["donateamt"] / 100:.2f}'

    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=donateamt,
            currency='usd',
            description='Donation',
            source=request.POST['stripeToken']
        )
        context = {'donateamt_display':donateamt_display,'namespace':'membership',}
        return render(request, 'membership/donate.html',context)
    return render(request, 'membership/donate.html',{})

#
def species(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    user = request.user
    author = Photographer.objects.get(user_id=user)
    if request.user.is_authenticated and request.user.tier.tier < 2:
        message = 'You dont have access to private page. Plese update your profile.'
        return HttpResponse(message)
    gen = 0
    genus = ''
    myspecies_list, myhybrid_list = sidebar(author)
    alpha = ''
    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
        if alpha == 'ALL':
            alpha = None

    offspring_list = []
    offspring_count = 0
    tab = ''
    pid = 0
    image_list = ()
    if 'pid' in request.GET:
        pid = request.GET['pid']
        pid = int(pid)
    if 'tab' in request.GET:
        tab = request.GET['tab']
    if not tab:
        tab = "sum"

    # Reroute to correct type

    try:
        species = Species.objects.get(pk=pid)
    except Species.DoesNotExist:
        message = 'Species does not exist! Use arrow key to go back to previous page.'
        return HttpResponse(message)
    genus = Genus.objects.get(pk=species.gen.pid)
    gen = genus.pid

    # Address is in error
    if species.type=='hybrid':
        if species.status == 'synonym':
            synonym = Synonym.objects.get(pk=pid)
            accepted = Species.objects.get(pk=synonym.acc_id)
            return HttpResponseRedirect("/membership/" + str(accepted.pid) + "/hybrid/?tab=sum")
        else:
            return HttpResponseRedirect("/membership/" + str(pid) + "/hybrid/?tab=" + tab)
    # Another eror
    if species.status == 'synonym':
        synonym = Synonym.objects.get(pk=pid)
        return HttpResponseRedirect("/membership/" + str(synonym.acc_id) + "/species/?tab=sum")
        # if request.user.is_authenticated and request.user.tier.tier > 2: print("6) Redirect if synonym = ",synonym.spid, synonym.acc_id)
    # Now, species is an accepted species
    if tab == "spc":
        # Variety filter
        image_list = SpcImages.objects.filter(pid=pid).filter(Q(author=author) | Q(rank__gt=0))
        print("1) image list = ", image_list.count())
        print("num images = ",image_list.count())

        for img in image_list:
            if img.image_file and img.image_file[0:3]=="spc":
                if os.path.exists("/home/chariya/webapps/static_media/utils/images/species/%s" % img.image_file):
                    img.image_file = img.image_file
                    # img.image_file = "/static/utils/images/species/" + img.image_file
                else:
                    img.image_file = "noimage_light.jpg"
            else:
                img.image_file = img.image_url
        image_list = image_list.order_by('-rank','?')
        print("2) image list = ", image_list.count())
        num_show = 5
        page_length = 100
        page_range, page_list, last_page, next_page, prev_page, page_length, page, first_item, last_item = mypaginator(
            request, image_list, page_length, num_show)
    else:
        page_list = []
        # Ancestor
        seed_list = Hybrid.objects.filter(seed_id=pid).order_by('pollen_genus', 'pollen_species')
        pollen_list = Hybrid.objects.filter(pollen_id=pid)
        # Remove duplicates. i.e. if both parents are synonym.
        temp_list = pollen_list
        for x in temp_list:
            if x.seed_status() == 'syn' and x.pollen_status() == 'syn':
                pollen_list = pollen_list.exclude(pid=x.pid_id)
        pollen_list = pollen_list.order_by('seed_genus', 'seed_species')
        offspring_list = chain(list(seed_list),list(pollen_list))
        offspring_count = len(seed_list) + len(pollen_list)
        if offspring_count > 5000:
            offspring_list = ()

    context = {'pid': pid, 'species': species, 'my_list': page_list,
               'myspecies_list':myspecies_list, 'myhybrid_list':myhybrid_list,
               'title': 'species', 'tab':tab,'spc':'active',
               'type':'species', 'genus':genus,
               'offspring_list':offspring_list,'offspring_count':offspring_count,
               'page': page, 'page_range': page_range, 'last_page': last_page,'prev_page': prev_page,'next_page':next_page,'num_show': num_show, 'page_length': page_length,
               'level':'membership', 'namespace':'membership',
               }
    return render(request, 'membership/species_detail.html', context)


def hybrid(request):
    author = Photographer.objects.get(pk=request.user)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    if not request.user.is_authenticated or request.user.tier.tier < 2:
        send_url = "%s?tab=%s&type=hybrid" % (reverse('detail:hybrid'), 'sum')
        return HttpResponseRedirect("/orchidlist/browsegen/")

    # initialization
    tab = ''
    id = 0
    image_list = {}
    ancspc_list = ()
    des_list = []
    offspring_list = []
    offspring_count = 0
    ps_list=pp_list=ss_list=sp_list=seedimg_list=pollimg_list=()
    myspecies_list, myhybrid_list = sidebar(author)

    if 'pid' in request.GET:
        pid = request.GET['pid']
    if 'tab' in request.GET:
        tab = request.GET['tab']

    if not tab: tab = 'hyb'
    try:
        species = Species.objects.get(pk=pid)
    except Species.DoesNotExist:
        message = 'This hybrid does not exist! Use arrow key to go back to previous page.'
        return HttpResponse(message)
    genus = Genus.objects.get(pk=species.gen.pid)
    gen = genus.pid

    # Now hybrid, but might be a synonym
    try:
        hybrid = Hybrid.objects.get(pk=pid)
    except Hybrid.DoesNotExist:
        try:
            synonym = Synonym.objects.get(pk=pid)
        except Synonym.DoesNotExist:
            message = 'This hybrid does not exist! Use arrow key to go back to previous page.'
            return HttpResponse(message)
        accepted = Species.objects.get(pk=synonym.acc_id)
        if accepted.type == 'hybrid':
            return HttpResponseRedirect("/membership/" + str(accepted.pid) + "/hybrid/?tab=sum")
        elif accepted.type == 'species':
            return HttpResponseRedirect("/membership/" + str(accepted.pid) + "/species/?tab=sum")
    # Done rerouting

    image_list = HybImages.objects.filter(pid=pid).filter(author=author)
    image_list = image_list.order_by('-rank', '?')
    print("image list = ",image_list.count())
    if tab == "hyb":
        seed_list = Hybrid.objects.filter(seed_id=pid).order_by('pollen_genus', 'pollen_species')
        pollen_list = Hybrid.objects.filter(pollen_id=pid)
        # Remove duplicates. i.e. if both parents are synonym.
        temp_list = pollen_list
        for x in temp_list:
            if x.seed_status() == 'syn' and x.pollen_status() == 'syn':
                pollen_list = pollen_list.exclude(pid=x.pid_id)
        pollen_list = pollen_list.order_by('seed_genus', 'seed_species')
        offspring_list = chain(list(seed_list),list(pollen_list))
        offspring_count = len(seed_list) + len(pollen_list)
        if offspring_count > 5000:
            offspring_list = ()

        if hybrid.seed_id and hybrid.seed_id.type == 'species':
            seed_obj = Species.objects.get(pk=hybrid.seed_id.pid)
            seedimg_list = SpcImages.objects.filter(pid=seed_obj.pid).order_by('-rank', '?')[0:3]
        elif hybrid.seed_id and hybrid.seed_id.type == 'hybrid':
            seed_obj = Hybrid.objects.get(pk=hybrid.seed_id)
            if seed_obj:
                seedimg_list = HybImages.objects.filter(pid=seed_obj.pid.pid).order_by('-rank', '?')[0:3]
                assert isinstance(seed_obj, object)
                if seed_obj.seed_id:
                    ss_type = seed_obj.seed_id.type
                    if ss_type == 'species':
                        ss_list = SpcImages.objects.filter(pid=seed_obj.seed_id.pid).order_by('?')[:1]
                    elif ss_type == 'hybrid':
                        ss_list = HybImages.objects.filter(pid=seed_obj.seed_id.pid).order_by('?')[:1]
                if seed_obj.pollen_id:
                    sp_type = seed_obj.pollen_id.type
                    if sp_type == 'species':
                        sp_list = SpcImages.objects.filter(pid=seed_obj.pollen_id.pid).order_by('?')[:1]
                    elif sp_type == 'hybrid':
                        sp_list = HybImages.objects.filter(pid=seed_obj.pollen_id.pid).order_by('?')[:1]

        # Pollen
        if hybrid.pollen_id and hybrid.pollen_id.type == 'species':
            pollen_obj = Species.objects.get(pk=hybrid.pollen_id.pid)
            pollimg_list = SpcImages.objects.filter(pid=pollen_obj.pid).order_by('-rank', '?')[0:3]
        elif hybrid.pollen_id and hybrid.pollen_id.type == 'hybrid':
            pollen_obj = Hybrid.objects.get(pk=hybrid.pollen_id)
            pollimg_list = HybImages.objects.filter(pid=pollen_obj.pid.pid).order_by('-rank', '?')[0:3]
            if pollen_obj.seed_id:
                ps_type = pollen_obj.seed_id.type
                if ps_type == 'species':
                    ps_list = SpcImages.objects.filter(pid=pollen_obj.seed_id.pid).order_by('?')[:1]
                elif ps_type == 'hybrid':
                    ps_list = HybImages.objects.filter(pid=pollen_obj.seed_id.pid).order_by('?')[:1]
            if pollen_obj.pollen_id:
                pp_type = pollen_obj.pollen_id.type
                if pp_type == 'species':
                    pp_list = SpcImages.objects.filter(pid=pollen_obj.pollen_id.pid).order_by('?')[:1]
                elif pp_type == 'hybrid':
                    pp_list = HybImages.objects.filter(pid=pollen_obj.pollen_id.pid).order_by('?')[:1]

        ancspc_list = AncestorDescendant.objects.filter(did=pid).filter(anctype='species').order_by('-pct')
        for x in ancspc_list:
            x.img = ''
            if x.aid.pid:
                x.img = get_random_img(aid.pid)

    context = {'hybrid':hybrid, 'species':species,'genus':species.genus, 'image_list':image_list,
                   'des_list':des_list, 'offspring_list': offspring_list,'offspring_count':offspring_count,
                   'tab':tab,'hyb':'active','ancspc_list':ancspc_list,
                   'type':'hybrid',
                   'myspecies_list': myspecies_list, 'myhybrid_list': myhybrid_list,
                   'seedimg_list':seedimg_list,'pollimg_list':pollimg_list,
                   'ss_list':ss_list,'sp_list':sp_list,
                   'ps_list':ps_list,'pp_list':pp_list,
                   'level':'membership', 'title':'hybrid','section':'Public Area','role':'pub','namespace':'membership',
                }

    return render(request, 'membership/hybrid_detail.html', context)


def browsegen(request):
    print("user = ",request.user)

    if not request.user.is_authenticated or request.user.tier.tier < 2:
        send_url = "%s?tab=%s" % (reverse('orchidlist:browsegen'), 'sum')
        return HttpResponseRedirect("/orchidlist/browsegen/")
    try:
        author = Photographer.objects.get(user_id=request.user)
    except Photographer.DoesNotExist:  # incase the account has not been synced (rare).
        return HttpResponseRedirect("/orchidlist/browsegen/")

    alpha = ''
    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
        if alpha == 'ALL':
            alpha = None

    spc_list = list(SpcImages.objects.filter(author=author).values_list('pid', flat=True).distinct())
    hyb_list = list(HybImages.objects.filter(author=author).values_list('pid', flat=True).distinct())

    spc_list = Species.objects.exclude(status='synonym').filter(type='species').filter(pid__in=spc_list).order_by('genus','species')
    hyb_list  = Species.objects.exclude(status='synonym').filter(type='hybrid').filter(pid__in=hyb_list).order_by('genus','species')

    myspecies_list = []
    myhybrid_list = []
    genus_list = []
    prevgenus = ''
    for x in spc_list:
        myspecies_list.append([x,prevgenus])
        if x.genus != prevgenus:
            genus_list.append(SpcImages.objects.filter(pid=x.pid).filter(author=author).order_by('?')[0:1])
            prevgenus = x.genus
    prevgenus = ''
    for x in hyb_list:
        myhybrid_list.append([x,prevgenus])
        if x.genus != prevgenus:
            genus_list.append(HybImages.objects.filter(pid=x.pid).filter(author=author).order_by('?')[0:1])
            prevgenus = x.genus

    num_show = 5
    page_length = 12
    page_range, page_list,last_page, next_page,prev_page, page_length,page,first_item,last_item = mypaginator(request,genus_list,page_length,num_show)

    context = {'page_list':page_list,
               'myspecies_list':myspecies_list,'myhybrid_list':myhybrid_list,
               'tab':'brg', 'brg':'active',
               'page_range': page_range, 'last_page': last_page, 'num_show': num_show, 'page_length': page_length,'page':page,
               'first':first_item,'last':last_item,'next_page':next_page,'prev_page':prev_page,
               'level':'membership','title':'browse','section':'membership', 'namespace':'membership',
               }
    return render(request, 'membership/browsegen.html', context)


def browse(request):
    type = 'species'
    if 'type' in request.GET:
        type = request.GET['type']
    if 'genus' in request.GET:
        genus = request.GET['genus']

    if not request.user.is_authenticated or request.user.tier.tier < 2:
        send_url = "%s?tab=%s" % (reverse('orchidlist:browsegen'), 'sum')
        return HttpResponseRedirect("/orchidlist/browsegen/")
    try:
        author = Photographer.objects.get(user_id=request.user)
    except Photographer.DoesNotExist:  # incase the account has not been synced (rare).
        return HttpResponseRedirect("/orchidlist/browse/")

    if request.user.tier.tier < 2:
        message = 'You dont have access to private page. Plese update your profile.'
        return HttpResponse(message)
    gen = 0
    genus = ''
    myspecies_list, myhybrid_list = sidebar(author)

    brs = ''
    brh = ''
    tab = ''
    my_full_list = []

    if type == 'hybrid':
        tab = 'brh'
        brh = 'active'
        pid_list = HybImages.objects.filter(author=author)
    elif type == 'species':
        tab = 'brs'
        brs = 'active'
        pid_list = SpcImages.objects.filter(author=author)
    if gen:
        pid_list = pid_list.filter(gen=gen)
    pid_list = pid_list.values_list('pid',flat=True).distinct()
    pid_list = Species.objects.filter(pid__in=pid_list).order_by('genus','species')
    for x in pid_list:
        img = x.get_best_img()
        if img:
            my_full_list.append(img)

    num_show = 5
    page_length = 12
    page_range, page_list,last_page, next_page,prev_page, page_length,page,first_item,last_item = mypaginator(request,my_full_list,page_length,num_show)
    context = {
                'page_list':page_list,'type':type,'genus':genus,
               'myspecies_list':myspecies_list,'myhybrid_list':myhybrid_list,
               'tab':tab, 'brs':brs,'brh':brh,
               'page_range': page_range, 'last_page': last_page, 'num_show': num_show, 'page_length': page_length,'page':page,
               'first':first_item,'last':last_item,'next_page':next_page,'prev_page':prev_page,
               'level':'membership','title':'browse','section':'membership', 'namespace':'membership',
               }
    return render(request, 'membership/browse.html', context)


def sidebar (author):
    spc_list = list(SpcImages.objects.filter(author=author).values_list('pid', flat=True).distinct())
    hyb_list = list(HybImages.objects.filter(author=author).values_list('pid', flat=True).distinct())

    spc_list = Species.objects.exclude(status='synonym').filter(type='species').filter(pid__in=spc_list).order_by(
        'genus', 'species')
    hyb_list = Species.objects.exclude(status='synonym').filter(type='hybrid').filter(pid__in=hyb_list).order_by(
        'genus', 'species')
    myspecies_list = []
    myhybrid_list = []
    prevgenus = ''
    for x in spc_list:
        myspecies_list.append([x, prevgenus])
        prevgenus = x.genus
    prevgenus = ''
    for x in hyb_list:
        myhybrid_list.append([x, prevgenus])
        prevgenus = x.genus
    return myspecies_list, myhybrid_list
