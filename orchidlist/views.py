from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import string
from itertools import chain
import random

# Create your views here.
from django.apps import apps
Genus = apps.get_model('orchiddb', 'Genus')
Genusacc = apps.get_model('orchiddb', 'Genusacc')
Intragen = apps.get_model('orchiddb', 'Intragen')
Species = apps.get_model('orchiddb', 'Species')
Hybrid = apps.get_model('orchiddb', 'Hybrid')
Accepted = apps.get_model('orchiddb', 'Accepted')

Subgenus = apps.get_model('orchiddb', 'Subgenus')
Section = apps.get_model('orchiddb', 'Section')
Subsection = apps.get_model('orchiddb', 'Subsection')
Series = apps.get_model('orchiddb', 'Series')

# Infragen = apps.get_model('orchiddb', 'Infragen')
Family = apps.get_model('orchiddb', 'Family')
Subfamily = apps.get_model('orchiddb', 'Subfamily')
Tribe = apps.get_model('orchiddb', 'Tribe')
Subtribe = apps.get_model('orchiddb', 'Subtribe')
Distribution = apps.get_model('orchiddb', 'Distribution')
Region = apps.get_model('orchiddb', 'Region')
Subregion = apps.get_model('orchiddb', 'Subregion')
Localregion = apps.get_model('orchiddb', 'Localregion')
GeoLoc = apps.get_model('orchiddb', 'GeoLoc')
SpcImages = apps.get_model('orchiddb', 'SpcImages')
HybImages = apps.get_model('orchiddb', 'HybImages')
UploadFile = apps.get_model('orchiddb', 'UploadFile')
AncestorDescendant = apps.get_model('orchiddb', 'AncestorDescendant')
User = get_user_model()
alpha_list = string.ascii_uppercase

# High level lists
def family(request):
    # -- List Genuses
    family_list = Family.objects.order_by('family')
    context = {'family_list': family_list, 'alpha_list': alpha_list, 'title': 'families', 'namespace':'orchidlist',}
    return render(request, 'orchidlist/family.html', context)


def subfamily(request):
    # -- List Genuses
    subfamily_list = Subfamily.objects.order_by('subfamily')
    context = {'subfamily_list': subfamily_list, 'alpha_list': alpha_list, 'title': 'subfamilies', 'namespace':'orchidlist',}
    return render(request, 'orchidlist/subfamily.html', context)


def tribe(request):
    subfamily = '';
    sf=''
    sf_list = Subfamily.objects.all()
    tribe_list = Tribe.objects.order_by('tribe')
    if 'sf' in request.GET:
        sf = request.GET['sf']
        if sf:
            sf_obj = Subfamily.objects.get(pk=sf)
            if sf_obj: tribe_list = tribe_list.filter(subfamily=sf)


    context = {'tribe_list': tribe_list, 'title': 'tribes', 'sf':sf,'sf_list':sf_list, 'namespace':'orchidlist',}
    return render(request, 'orchidlist/tribe.html', context)


def subtribe(request):
    subtribe_list = Subtribe.objects.all().order_by('subtribe')
    sf = ''
    t = ''
    sf_list = Subfamily.objects.all()
    t_list = Tribe.objects.all()
    if 'sf' in request.GET:
        sf = request.GET['sf']
        if sf:
            sf_obj = Subfamily.objects.get(pk=sf)
            if sf_obj: subtribe_list = subtribe_list.filter(subfamily=sf)
    if 't' in request.GET:
        t = request.GET['t']
        if t:
            t_obj = Tribe.objects.get(pk=t)
            if t_obj: subtribe_list = subtribe_list.filter(tribe=t)

    context = {'subtribe_list': subtribe_list,  'title': 'subtribes','t':t,'sf':sf,'sf_list':sf_list,'t_list':t_list, 'namespace':'orchidlist',}
    return render(request, 'orchidlist/subtribe.html', context)


@login_required
def genera(request):
    genus = ''
    min_lengenus_req = 2
    year = ''
    year_valid = 0
    genustype = ''
    formula1 = ''
    formula2 = ''
    status = ''
    sort = ''
    prev_sort = ''
    sf  = ''
    sf_obj = ''
    t = ''
    t_obj = ''
    st = ''
    st_obj = ''
    num_show = 5
    page_length = 200
    # max_page_length = 1000
    page_range = []
    last_page = 1
    if 'role' in request.GET:
        role = request.GET['role']

    if 'genus' in request.GET:
        genus = request.GET['genus']
        if len(genus) > min_lengenus_req:
            genus = str(genus).split()
            genus = genus[0];
    if 'sf' in request.GET:
        sf = request.GET['sf']
        if sf:
            sf_obj = Subfamily.objects.get(pk=sf)
    if 't' in request.GET:
        t = request.GET['t']
        if t:
            try:
                t_obj = Tribe.objects.get(pk=t)
            except Tribe.DoesNotExist:
                pass
            if not sf_obj:
                try:
                    sf_obj = Subfamily.objects.get(pk=t_obj.subfamily)       # back fill subfamily
                except Subfamily.DoesNotExist:
                    pass
    if 'st' in request.GET:
        st = request.GET['st']
        if st:
            try:
                st_obj = Subtribe.objects.get(pk=st)
            except Subtribe.DoesNotExist:
                pass
            if st_obj:
                if not t:
                    try:
                        t_obj = Tribe.objects.get(pk=st_obj.tribe.tribe)
                    except Tribe.DoesNotExist:
                        pass
                if not sf_obj and st_obj.subfamily:
                    try:
                        sf_obj = Subfamily.objects.get(pk=st_obj.subfamily)
                    except Subtribe.DoesNotExist:
                        pass

    # Remove genus choide if subfamily, tribe or subtribe is chosen
    if sf_obj or t_obj or st_obj:
        genus = ''
    if 'year' in request.GET:
        year = request.GET['year']
        if valid_year(year):
            year_valid = 1

    if 'genustype' in request.GET:
        genustype = request.GET['genustype']

    if 'formula1' in request.GET:
        formula1 = request.GET['formula1']
    if 'formula2' in request.GET:
        formula2 = request.GET['formula2']

    if 'status' in request.GET:
        status = request.GET['status']

    genus_list = Genus.objects.all()
    if genus:
        if len(genus) >= 2:
            genus_list = genus_list.filter(genus__icontains=genus)
        elif len(genus) < 2:
            genus_list = genus_list.filter(genus__istartswith=genus)

    if status == 'synonym':
        genus_list = genus_list.filter(status='synonym')

    elif genustype:
        if genustype == 'ALL':
            if year:
                genus_list = genus_list.filter(year=year)
        elif genustype == 'hybrid':
            genus_list = genus_list.filter(type='hybrid').exclude(status='synonym')
            if formula1 != '' or formula2 != '':
                genus_list = genus_list.filter(description__icontains=formula1).filter(description__icontains=formula2)
        elif genustype == 'species':
            # If an intrageneric is chosen, start from beginning.
            genus_list = genus_list.filter(type='species').exclude(status='synonym')
            if sf_obj or t_obj or st_obj:
                if sf_obj and t_obj and st_obj:
                    genus_list = genus_list.filter(subfamily=sf_obj.subfamily).filter(tribe=t_obj.tribe).filter(subtribe=st_obj.subtribe)
                elif sf_obj and t_obj and not st_obj:
                    genus_list = genus_list.filter(subfamily=sf_obj.subfamily).filter(tribe=t_obj.tribe)
                elif sf_obj and st_obj and not t_obj:
                    genus_list = genus_list.filter(subfamily=sf_obj.subfamily).filter(subtribe=st_obj.subtribe)
                elif sf_obj and not st_obj and not t_obj:
                    genus_list = genus_list.filter(subfamily=sf_obj.subfamily)
                elif t_obj and st_obj and not sf_obj:
                    genus_list = genus_list.filter(tribe=t_obj.tribe).filter(st=st_obj.subtribe)
                elif t_obj and not st_obj and not sf_obj:
                    genus_list = genus_list.filter(tribe=t_obj.tribe)
                elif st_obj and not t_obj and not sf_obj:
                    genus_list = genus_list.filter(subtribe=st_obj.subtribe)

    if request.GET.get('sort'):
        sort = request.GET['sort']
        sort.lower()
    if sort:
        if request.GET.get('prev_sort'):
            prev_sort = request.GET['prev_sort']
        if prev_sort == sort:
            if sort.find('-',0) >= 0:
                sort = sort.replace('-','')
            else:
                sort = '-'+sort
        else:
            # sort = '-' + sort
            prev_sort = sort

    # Sort before paginator
    if sort:
        if sort == 'sf':
            genus_list = genus_list.order_by('subfamily__subfamily')
        elif sort == 't':
            genus_list = genus_list.order_by('tribe__tribe')
        elif sort == 'st':
            genus_list = genus_list.order_by('subtribe__subtribe')
        else:
            genus_list = genus_list.order_by(sort)
    total = genus_list.count()
    paginatiopaginator = ()
    my_list = ''
    if page_length > 0:
        paginator = Paginator(genus_list, page_length)
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        try:
            my_list = paginator.page(page)
            last_page = paginator.num_pages
        except(EmptyPage):
            my_list = paginator.page(1)
            last_page = 1
        # Get the index of the current page
        index = my_list.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - num_show if index >= num_show else 0
        end_index = index + num_show if index <= max_index - num_show else max_index
        # My new page range
        page_range = paginator.page_range[start_index:end_index]

    # Get Alliances
    sf_list = Subfamily.objects.all()

    t_list = Tribe.objects.all()
    if sf_obj:
        t_list = t_list.filter(subfamily=sf_obj.subfamily)

    st_list = Subtribe.objects.all()
    if t_obj:
        st_list = st_list.filter(tribe=t_obj.tribe)
    elif sf_obj:
        st_list = st_list.filter(subfamily=sf_obj.subfamily)

    sf_list = sf_list.order_by('subfamily')
    t_list  = t_list.order_by('tribe')
    st_list = st_list.order_by('subtribe')
    genus_lookup = Genus.objects.filter(pid__gt=0).filter(type='species')
    # if request.user.is_authenticated and request.user.tier.tier > 2:
    #     message = "4) After get genus lookup"
    #     print(message)
    #     return HttpResponse(message)

    # if status == 'synonym':     # For synonym, dont care if species or hybrid
    #     type = ''
    context = {'my_list': my_list,'total':total,'genus_lookup':genus_lookup,
               'sf_obj':sf_obj,'sf_list':sf_list,
               't_obj':t_obj,'t_list':t_list,
               'st_obj':st_obj,'st_list':st_list,
               'title': 'genera', 'genus': genus, 'year': year, 'genustype': genustype,'status':status,
               'formula1':formula1, 'formula2':formula2,
               'genactive': 'active', 'sort': sort, 'prev_sort': prev_sort,
               'page_range': page_range,'last_page':last_page, 'num_show':num_show, 'page_length':page_length, 'namespace':'orchidlist',}
    print("orchidlist/genus_list ",request.user)
    return render(request, 'orchidlist/genera.html', context)


def subgenus(request):
    # -- List Genuses
    subgenus_list = Subgenus.objects.order_by('subgenus')
    context = {'subgenus_list': subgenus_list, 'title': 'subgenus', 'namespace':'orchidlist',}
    return render(request, 'orchidlist/subgenus.html', context)


def section(request):
    # -- List Genuses
    section_list = Section.objects.order_by('section')
    context = {'section_list': section_list, 'title': 'section', 'namespace':'orchidlist',}
    return render(request, 'orchidlist/section.html', context)


def subsection(request):
    # -- List Genuses
    subsection_list = Subsection.objects.order_by('subsection')
    context = {'subsection_list': subsection_list, 'title': 'subsection', 'namespace':'orchidlist',}
    return render(request, 'orchidlist/subsection.html', context)


def series(request):
    # -- List Genuses
    series_list = Series.objects.order_by('series')
    context = {'series_list': series_list, 'title': 'series', 'namespace':'orchidlist',}
    return render(request, 'orchidlist/series.html', context)

@login_required
def species_list(request):
    species = spc = genus = ''
    # this_species_list = Species.objects.none()
    subgenus = section = subsection = series = ''
    subgenus_obj = section_obj = subsection_obj = series_obj = ''
    region_obj = subregion_obj = ''
    # region_list = subregion_list = []
    # min_lenspecies_req = 2
    year = ''
    year_valid = 0
    status = author = dist= alpha = prev_alpha = ''
    sort = prev_sort = ''
    num_show = 5
    page_length = 500
    # max_page_length = 1000
    # Initialize
    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
    if request.GET.get('prev_alpha'):
        prev_alpha = request.GET['prev_alpha']
        if alpha == prev_alpha:
            alpha = ''
            prev_alpha = ''
        else:
            prev_alpha = alpha
    if 'year' in request.GET:
        year = request.GET['year']
        if valid_year(year):
            year_valid = 1
    if 'status' in request.GET:
        status = request.GET['status']

    # Get regions
    if 'region' in request.GET:
        region = request.GET['region']
        if region:
            try:
                region_obj = Region.objects.get(id=region)
            except Region.DoesNotExist:
                # print("Region = ", region)
                pass
    if 'subregion' in request.GET:
        subregion = request.GET['subregion']
        if subregion:
            try:
                subregion_obj = Subregion.objects.get(code=subregion)
            except Subregion.DoesNotExist:
                # print("Subregion = ", subregion)
                pass
    region_list = Region.objects.exclude(id=0)
    if region_obj:
        subregion_list = Subregion.objects.filter(region=region_obj.id)
    else:
        subregion_list = Subregion.objects.all()

    # Get list for display
    this_species_list = Species.objects.exclude(status='pending').filter(type='species')
    if status != 'synonym':
        this_species_list = this_species_list.exclude(status='synonym')
    # elif status == 'accepted':
    #     this_species_list = this_species_list.exclude(status='synonym')


    if 'gen' in request.GET:
        gen = request.GET['gen']
        if not gen:
            gen = 0

        # print("0. >>> hybrid genus = ", gen)
        try:
            genus = Genus.objects.get(pk=gen)
        except Genus.DoesNotExist:
            genus = ''
    else:
        gen = ''

    if 'genus' in request.GET:
        genus = request.GET['genus']
        # print("0. >>> hybrid genus = ", genus, len(this_species_list))
        try:
            gen = Genus.objects.get(genus=genus).pid
        except Genus.DoesNotExist:
            gen = ''

    intragen_list = Intragen.objects.all()
    if gen:
        this_species_list = this_species_list.filter(gen=gen)
        intragen_list = intragen_list.filter(gen=gen)

    species_list = []
    hybrid_list = []
    if genus:
        if genus[0] != '%' and genus[-1] != '%':
            this_species_list = this_species_list.filter(genus__icontains=genus)
            intragen_list = intragen_list.filter(genus__icontains=genus)
            # print("2. >>> hybrid specieslist = ", gen, len(this_species_list))

        elif genus[0] == '%' and genus[-1] != '%':
            mygenus = genus[1:]
            this_species_list = this_species_list.filter(genus__iendswith=mygenus)
            intragen_list = intragen_list.filter(genus__iendswith=genus)

        elif genus[0] != '%' and genus[-1] == '%':
            mygenus = genus[:-1]
            this_species_list = this_species_list.filter(genus__istartswith=mygenus)
            intragen_list = intragen_list.filter(genus__istartswith=genus)
        elif genus[0] == '%' and genus[-1] == '%':
            mygenus = genus[1:-1]
            this_species_list = this_species_list.filter(genus__icontains=mygenus)
            intragen_list = intragen_list.filter(genus__icontains=genus)

    if 'subgenus' in request.GET:
        subgenus = request.GET['subgenus']
        if subgenus:
            try:
                subgenus_obj = Subgenus.objects.get(pk=subgenus)
            except Subgenus.DoesNotExist:
                # print("\t>>>>>>>>>>>>> Subgenus = ", subgenus)
                pass
            if gen:
                temp_subgen_list = Accepted.objects.filter(subgenus=subgenus).filter(gen=gen).distinct().values_list('pid',flat=True)
            else:
                temp_subgen_list = Accepted.objects.filter(subgenus=subgenus).distinct().values_list('pid',flat=True)
    if 'section' in request.GET:
        section = request.GET['section']
        # print("section = ",section)
        if section:
            try:
                section_obj = Section.objects.get(pk=section)
            except Section.DoesNotExist:
                # print("\t>>>>>>>>> Section = ", section)
                section_obj = ''
            if gen:
                temp_sec_list = Accepted.objects.filter(section=section).filter(gen=gen).distinct().values_list('pid', flat=True)
            else:
                temp_sec_list = Accepted.objects.filter(section=section).distinct().values_list('pid', flat=True)
    if 'subsection' in request.GET:
        subsection = request.GET['subsection']
        # print(">>subsection = ",subsection,' -- ',request.user)
        if subsection:
            try:
                subsection_obj = Subsection.objects.get(pk=subsection)
            except Subsection.DoesNotExist:
                # print("\t>>>>>>>>> Subsection = ", subsection)
                pass
            if gen:
                temp_subsec_list = Accepted.objects.filter(subsection=subsection).filter(gen=gen).distinct().values_list('pid', flat=True)
            else:
                temp_subsec_list = Accepted.objects.filter(subsection=subsection).distinct().values_list('pid', flat=True)
    if 'series' in request.GET:
        series = request.GET['series']
        # print(">>Series = ",series,' -- ',request.user)
        if series:
            try:
                series_obj = Series.objects.get(pk=series)
            except Series.DoesNotExist:
                # print("\t>>>>>>>>> Series = ", series)
                pass
            if gen:
                temp_ser_list = Accepted.objects.filter(series=series).filter(gen=gen).distinct().values_list('pid', flat=True)
            else:
                temp_ser_list = Accepted.objects.filter(series=series).distinct().values_list('pid', flat=True)

    if 'spc' in request.GET:
        spc = request.GET['spc']
        if len(spc) == 1:
            alpha = ''
        species = spc

    if 'author' in request.GET:
        author = request.GET['author']

    if 'dist' in request.GET:
        dist = request.GET['dist']

    if alpha != 'ALL':
        alpha = alpha[0:1]

    if request.GET.get('sort'):
        sort = request.GET['sort']
        sort.lower()
    if sort:
        if request.GET.get('prev_sort'):
            prev_sort = request.GET['prev_sort']
        if prev_sort == sort:
            if sort.find('-',0) >= 0:
                sort = sort.replace('-','')
            else:
                sort = '-'+sort
        else:
            # sort = '-' + sort
            prev_sort = sort
    if subgenus:
        this_species_list = this_species_list.filter(pid__in=temp_subgen_list)
    if section:
        this_species_list = this_species_list.filter(pid__in=temp_sec_list)
    if subsection:
        this_species_list = this_species_list.filter(pid__in=temp_subsec_list)
    if series:
        this_species_list = this_species_list.filter(pid__in=temp_ser_list)

    if species:
        # if species[0] != '%' and species[-1] != '%':
        if len(species) >= 2:
            this_species_list = this_species_list.filter(species__icontains=species)
        else:
            this_species_list = this_species_list.filter(species__istartswith=species)

    elif alpha:
        if len(alpha) == 1:
            this_species_list = this_species_list.filter(species__istartswith=alpha)

    if author:
        this_species_list = this_species_list.filter(author__icontains=author)

    if dist:
        this_species_list = this_species_list.filter(distribution__icontains=dist)

    if year_valid:
        year = int(year)
        this_species_list = this_species_list.filter(year=year)

    if region_obj:
        pid_list = Distribution.objects.filter(region_id=region_obj.id).values_list('pid',flat=True).distinct()
        this_species_list = this_species_list.filter(pid__in=pid_list)
    if subregion_obj:
        pid_list = Distribution.objects.filter(subregion_code=subregion_obj.code).values_list('pid',flat=True).distinct()
        this_species_list = this_species_list.filter(pid__in=pid_list)

    if sort:
        if sort == 'classification':
            this_species_list = this_species_list.order_by('subgenus','section','subsection','series')
        elif sort == '-classification':
            this_species_list = this_species_list.order_by('-subgenus','-section','-subsection','-series')
        else:
            try:
                this_species_list = this_species_list.order_by(sort)
            except:
                # print("\t>>>>>>>>>>>>> Sort by ",sort)
                pass
    else:
        this_species_list = this_species_list.order_by('genus','species')
    total = this_species_list.count()
    # print("1. >>> species this_species_list = ",len(this_species_list), page_length,num_show, "gen = ", gen,".")
    page_range, page_list,last_page, next_page,prev_page, page_length,page,first_item,last_item = mypaginator(request,this_species_list,page_length,num_show)

    subgenus_list = intragen_list.filter(subgenus__isnull=False).values_list('subgenus','subgenus').distinct().order_by('subgenus')
    if gen: subgenus_list = subgenus_list.filter(gen=gen)
    elif genus: subgenus_list = subgenus_list.filter(genus__istartswith=genus)

    section_list = intragen_list.filter(section__isnull=False)
    if gen: section_list = section_list.filter(gen=gen)
    elif genus: section_list = section_list.filter(genus__istartswith=genus)
    # print("gen = ", gen)
    # print("section = ", section)

    subsection_list = intragen_list.filter(subsection__isnull=False)
    if gen: subsection_list = subsection_list.filter(gen=gen)
    elif genus: subsection_list = subsection_list.filter(genus__istartswith=genus)

    series_list = intragen_list.filter(series__isnull=False)
    if gen: series_list = series_list.filter(gen=gen)
    elif genus: series_list = series_list.filter(genus__istartswith=genus)

    if subgenus:
        section_list = section_list.filter(subgenus=subgenus)
        subsection_list = subsection_list.filter(subgenus=subgenus)
        series_list = series_list.filter(subgenus=subgenus)

    if section:
        subsection_list = subsection_list.filter(section=section)
        series_list = series_list.filter(section=section)

    section_list = section_list.values_list('section','section').distinct().order_by('section')
    subsection_list = subsection_list.values_list('subsection','subsection').distinct().order_by('subsection')
    series_list = series_list.values_list('series','series').distinct().order_by('series')

    # Sort by classification
    classtitle = ''
    if not subgenus_list: subgenus_obj = ''
    else: classtitle = classtitle + 'Subgenus'
    if not section_list: section_obj = ''
    else: classtitle = classtitle + ' Section'
    if not subsection_list: subsection_obj = ''
    else: classtitle = classtitle + ' Subsection'
    if not series_list: series_obj = ''
    else: classtitle = classtitle + ' Series'
    if classtitle == '':
        classtitle = 'Classification'
    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']
    print("orchidlist/species ",request.user,genus)
    genus_list = Genus.objects.all()
    print("1. >>>>> genus_list = ",len(genus_list))
    context = {'page_list': page_list, 'total':total,'alpha_list': alpha_list, 'alpha': alpha,'spc':spc,
               'gen':gen, 'role':role, 'species':species,
               'subgenus_list':subgenus_list,'subgenus_obj':subgenus_obj,
               'section_list': section_list, 'section_obj': section_obj,'genus':genus,
               'subsection_list': subsection_list, 'subsection_obj': subsection_obj,
               'series_list': series_list, 'series_obj': series_obj,
               'classtitle':classtitle,
               'year': year, 'status':status,
               'author':author,'dist':dist,
               'region_obj':region_obj,'region_list':region_list,'subregion_obj':subregion_obj, 'subregion_list':subregion_list,
               'genactive': 'active', 'sort': sort, 'prev_sort': prev_sort,
               'page_range': page_range,'last_page':last_page, 'num_show':num_show, 'page_length':page_length,
               'level':'list', 'title': 'species_list','namespace':'orchidlist',
               }
    return render(request, 'orchidlist/species.html', context)

@login_required
def hybrid_list(request):
    species = ''
    spc = ''
    genus = ''
    # min_lenspecies_req = 2
    year = ''
    year_valid = 0
    status = ''
    author = ''
    originator = ''
    seed_genus = ''
    pollen_genus = ''
    seed = ''
    pollen = ''
    alpha = ''

    prev_alpha = ''
    sort = ''
    prev_sort = ''

    num_show = 5
    page_length = 100
    # max_page_length = 1000
    page_range = []
    last_page = 1

    if 'alpha' in request.GET:
        alpha = request.GET['alpha']

    if request.GET.get('prev_alpha'):
        prev_alpha = request.GET['prev_alpha']
        if alpha == prev_alpha:
            alpha = ''
            prev_alpha = ''
        else:
            prev_alpha = alpha

    if 'year' in request.GET:
        year = request.GET['year']
        if valid_year(year):
            year_valid = 1

    if 'status' in request.GET:
        status = request.GET['status']

    this_species_list = Species.objects.exclude(status='pending').filter(type='hybrid')
    if status == 'synonym':
        this_species_list = this_species_list.filter(status='synonym')
    elif status == 'accepted':
        this_species_list = this_species_list.exclude(status='synonym')
    # print("0. >>> hybrid specieslist = ",len(this_species_list))

    if 'genus' in request.GET:
        genus = request.GET['genus']
        # print("0. >>> hybrid genus = ", genus, len(this_species_list))
        try:
            gen = Genus.objects.get(genus=genus).pid
        except Genus.DoesNotExist:
            gen = ''
    # print("1. >>> hybrid gen = ", gen)


    # print ("hybrid gen = ",gen)

    hybrid_list = []
    species_list = []
    if genus:
        if genus[0] != '%' and genus[-1] != '%':
            this_species_list = this_species_list.filter(genus__icontains=genus)
            # print("2. >>> hybrid specieslist = ", gen, len(this_species_list))

        elif genus[0] == '%' and genus[-1] != '%':
            mygenus = genus[1:]
            this_species_list = this_species_list.filter(genus__iendswith=mygenus)

        elif genus[0] != '%' and genus[-1] == '%':
            mygenus = genus[:-1]
            this_species_list = this_species_list.filter(genus__istartswith=mygenus)
        elif genus[0] == '%' and genus[-1] == '%':
            mygenus = genus[1:-1]
            this_species_list = this_species_list.filter(genus__icontains=mygenus)

    if 'spc' in request.GET:
        spc = request.GET['spc']
        if len(spc) == 1:
            alpha = ''
        species = spc

    if 'author' in request.GET:
        author = request.GET['author']
    # print("2. >>> hybrid registrant = ",author)
    if 'originator' in request.GET:
        originator = request.GET['originator']

    if 'seed' in request.GET:
        seed = request.GET['seed']

    if 'pollen' in request.GET:
        pollen = request.GET['pollen']

    if 'seed_genus' in request.GET:
        seed_genus = request.GET['seed_genus']
    # print('seed_genus = ',seed_genus)

    if 'pollen_genus' in request.GET:
        pollen_genus = request.GET['pollen_genus']
    # print('pollen_genus = ',pollen_genus)
    if alpha != 'ALL':
        alpha = alpha[0:1]

    if request.GET.get('sort'):
        sort = request.GET['sort']
        sort.lower()
    if sort:
        if request.GET.get('prev_sort'):
            prev_sort = request.GET['prev_sort']
        if prev_sort == sort:
            if sort.find('-',0) >= 0:
                sort = sort.replace('-','')
            else:
                sort = '-'+sort
        else:
            # sort = '-' + sort
            prev_sort = sort
    # if len(species) >= min_lenspecies_req:  # if filter by species, force sort to be 'species'
    #     sort = 'species'
    #     prev_sort = ''

    if species:
        # if species[0] != '%' and species[-1] != '%':
        if len(species) >= 2:
            this_species_list = this_species_list.filter(species__icontains=species)
        else:
            this_species_list = this_species_list.filter(species__istartswith=species)
        # print("3. >>> hybrid specieslist = ", len(this_species_list))

    elif alpha:
        if len(alpha) == 1:
            this_species_list = this_species_list.filter(species__istartswith=alpha)

    if author and not originator:
        this_species_list = this_species_list.filter(author__icontains=author)
    if author and originator:
        this_species_list = this_species_list.filter(Q(author__icontains=author) | Q(originator__icontains=originator))
    if originator and not author:
        this_species_list = this_species_list.filter(originator__icontains=originator)
    # print("0. >>> hybrid specieslist = ",len(this_species_list))

    # print(species_list.count(), seed_genus)
    if seed_genus:
        this_species_list = this_species_list.filter(Q(hybrid__seed_genus=seed_genus) | Q(hybrid__pollen_genus=seed_genus))
        # print(seed_genus,this_species_list.count())
    if pollen_genus:
        this_species_list = this_species_list.filter(Q(hybrid__seed_genus=pollen_genus) | Q(hybrid__pollen_genus=pollen_genus))
        # print(pollen_genus, this_species_list.count())

    if seed:
        this_species_list = this_species_list.filter(Q(hybrid__seed_species__icontains=seed) | Q(hybrid__pollen_species__icontains=seed))

    if pollen:
        this_species_list = this_species_list.filter(Q(hybrid__seed_species__icontains=pollen) | Q(hybrid__pollen_species__icontains=pollen))

    if year_valid:
        year = int(year)
        this_species_list = this_species_list.filter(year=year)

    # # Add the following to clear the list if no filter given
    # if not genus and not spc and not seed and not pollen and not year and not author and not originator and not dist \
    #         and not ancestor and not subgenus and not section and not subsection and not series:
    #     this_species_list = Species.objects.none()

    if sort:
        this_species_list = this_species_list.order_by(sort)
    else:
        this_species_list = this_species_list.order_by('genus','species')
    total = this_species_list.count()

    paginatiopaginator = ()
    my_list = ''
    if page_length > 0:
        paginator = Paginator(this_species_list, page_length)
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        try:
            my_list = paginator.page(page)
            last_page = paginator.num_pages
        except(EmptyPage):
            my_list = paginator.page(1)
            last_page = 1
        # Get the index of the current page
        index = my_list.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - num_show if index >= num_show else 0
        end_index = index + num_show if index <= max_index - num_show else max_index
        # My new page range
        page_range = paginator.page_range[start_index:end_index]
    if genus or spc or seed_genus or pollen_genus or seed or pollen or year or author or originator or alpha:
        genus_list = Genus.objects.exclude(status='synonym').filter(Q(num_species__gte=0) | Q(num_hybrid__gte=0))
    else:
        genus_list = {}

    print("orchidlist/hybrid  ",request.user,genus)
    context = {'my_list': my_list, 'total':total,'alpha_list': alpha_list, 'genus_list':genus_list,'alpha': alpha,'spc':spc,
               'genus':genus,'year': year, 'status':status,
               'author':author,'originator':originator,'seed':seed,'pollen':pollen,'seed_genus':seed_genus,'pollen_genus':pollen_genus,
               'genactive': 'active', 'sort': sort, 'prev_sort': prev_sort,
               'page_range': page_range,'last_page':last_page, 'num_show':num_show, 'page_length':page_length,
               'level': 'list','title': 'hybrid_list', 'namespace':'orchidlist',
               }
    return render(request, 'orchidlist/hybrid.html', context)


def browsegen(request):
    gen = 0
    type = ''
    genus = ''
    display = ''
    total = 0
    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']

    alpha = ''
    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
        if alpha == 'ALL':
            alpha = None
    if 'display' in request.GET:
        display = request.GET['display']
    if 'type' in request.GET:
        type = request.GET['type']
    else:
        type = 'species'

    my_full_list = []
    if type == 'species':
        dir = 'utils/images/species/'
        gen_list = Genus.objects.filter(num_species__gt=0).exclude(genus='na')
        if alpha:
            gen_list = gen_list.filter(genus__istartswith=alpha)
        if not gen_list:
            return HttpResponseRedirect("/orchidlist/browsegen/?role=" + role + "&type=hybrid")
        for x in gen_list:
            y = Species.objects.filter(gen=x).filter(type='species').exclude(status='synonym')
            if display == 'checked':
                y = y.filter(num_image__gt=0)
            y = y.order_by('-num_image','?')[0:1]
            if len(y):
                y = y[0]
                if y.get_best_img():
                    y.image_file = dir + y.get_best_img().image_file
                elif display != 'checked':
                    y.image_file = dir + 'noimage_light.jpg'
                my_full_list.append(y)
    else:
        dir = 'utils/images/hybrid/'
        gen_list = Genus.objects.filter(num_hybrid__gt=0).exclude(genus='na')
        if alpha:
            gen_list = gen_list.filter(genus__istartswith=alpha)
        if not gen_list:
            return HttpResponseRedirect("/orchidlist/browsegen/?role=" + role + "&type=species")
        for x in gen_list:
            y = Species.objects.filter(gen=x).filter(type='hybrid').exclude(status='synonym')
            if display == 'checked':
                y = y.filter(num_image__gt=0)
            y = y.order_by('-num_image','?')[0:1]
            if len(y):
                y = y[0]
                if y.get_best_img():
                    y.image_file = dir + y.get_best_img().image_file
                    my_full_list.append(y)
                elif display != 'checked':
                    y.image_file = dir + 'noimage_light.jpg'
                    my_full_list.append(y)
    num_show = 5
    page_length = 20
    page_range, page_list,last_page, next_page,prev_page, page_length,page,first_item,last_item = mypaginator(request,my_full_list,page_length,num_show)
    context = {
        'page_list': page_list,'type': type, 'gen': gen, 'genus':genus,
        'page': page, 'page_range': page_range, 'last_page': last_page, 'num_show': num_show, 'page_length': page_length,
        'alpha':alpha, 'alpha_list':alpha_list, 'display':display,
        'first': first_item, 'last': last_item, 'next_page': next_page, 'prev_page': prev_page,
        'level': 'detail', 'title': 'browsegen', 'section': 'My Collection', 'namespace': 'detail', 'role':role,
               }
    print("orchidlist/browsegen   ",request.user, genus)
    return render(request, 'orchidlist/browse_gen.html', context)


def browse(request,gen=None):
    import collections
    subgenus = ''
    section = ''
    type = ''
    subsection = ''
    series = ''
    subgenus_obj = ''
    section_obj = ''
    subsection_obj = ''
    series_obj = ''
    img_list = []
    genus = ''
    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']
    if 'subgenus' in request.GET:
        subgenus = request.GET['subgenus']
        if subgenus:
            subgenus_obj = Subgenus.objects.get(pk=subgenus)
    if 'section' in request.GET:
        section = request.GET['section']
        if section:
            try:
                section_obj = Section.objects.get(pk=section)
            except Section.DoesNotExist:
                section_obj = ''
    if 'subsection' in request.GET:
        subsection = request.GET['subsection']
        if subsection:
            try:
                subsection_obj = Subsection.objects.get(pk=subsection)
            except Subsection.DoesNotExist:
                subsection_obj = ''
    if 'series' in request.GET:
        series = request.GET['series']
        if series:
            series_obj = Series.objects.get(pk=series)

    if gen:
        try:
            genus = Genus.objects.get(pk=gen)
        except Genus.DoesNotExist:
            pass
    if not gen and not genus and 'genus' in request.GET:
        genus = request.GET['genus']
        try:
            genus = Genus.objects.get(genus=genus)
            gen = genus.pid
        except Genus.DoesNotExist:
            pass
    if not gen and not genus and 'gen' in request.GET:
        gen = request.GET['gen']
        genus = ''
        if gen:
            try:
                genus = Genus.objects.get(pk=gen)
            except Genus.DoesNotExist:
                genus = ''
                gen = ''
    if not gen and not genus:
        # No genus is given, send it to browsegen
        print("1. >>>>> No genus given. Return to Browsegen ")
        return HttpResponseRedirect("/orchidlist/browsegen/?display=checked")

    print("orchidlist/browse  ",request.user,genus)

    if 'display' in request.GET:
        display = request.GET['display']
    else:
        display = False

    if 'type' in request.GET:
        type = request.GET['type']
    else:
        type = 'species'

    intragen_list = subgenus_list = section_list = subsection_list = series_list = []
    intragen_list = Intragen.objects.filter(gen=gen)
    subgenus_list = intragen_list.exclude(subgenus__isnull=True).exclude(subgenus__exact='').filter(
        gen=gen).distinct().values('subgenus').order_by('subgenus')
    section_list = intragen_list.exclude(section__isnull=True).exclude(section__exact='').filter(
        gen=gen).distinct().values('section').order_by('section')
    subsection_list = intragen_list.exclude(subsection__isnull=True).exclude(subsection__exact='').filter(
        gen=gen).distinct().values('subsection').order_by('subsection')
    series_list = intragen_list.exclude(series__isnull=True).exclude(series__exact='').filter(
        gen=gen).distinct().values('series').order_by('series')
    if subgenus:
        section_list = section_list.filter(subgenus=subgenus)
        subsection_list = subsection_list.filter(subgenus=subgenus)
        series_list = series_list.filter(subgenus=subgenus)
    if section:
        subsection_list = subsection_list.filter(section=section)
        series_list = series_list.filter(section=section)
    pid_list = ()
    if type == 'species':
        pid_list = Accepted.objects.filter(gen=gen)
        if pid_list:
            if subgenus:
                pid_list = pid_list.filter(subgenus=subgenus)
            if section:
                pid_list = pid_list.filter(section=section)
            if subsection:
                pid_list = pid_list.filter(subsection=subsection)
            if series:
                pid_list = pid_list.filter(series=series)

    img_list = Species.objects.filter(gen=gen).exclude(status='synonym')

    if pid_list:
        img_list = img_list.filter(pid__in=pid_list)
    if display=='checked':
        img_list = img_list.filter(num_image__gt=0)

    my_full_list = []

    # img_list = Species.objects.filter(gen=gen).exclude(status='synonym')
    alpha = ''
    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
        if alpha == 'ALL':
            alpha = ''
    if img_list:
        if type == 'species':
            dir = 'utils/images/species/'
            img_list = img_list.filter(type__iexact='species')
        else:
            dir = 'utils/images/hybrid/'
            img_list = img_list.filter(type__iexact='hybrid')
        if display == "checked":
            img_list = img_list.filter(num_image__gt=0)
        if alpha:
            img_list = img_list.filter(species__istartswith=alpha)

        img_list = img_list.order_by('genus','species')
        for x in img_list:
            if x.get_best_img():
                x.image_file = dir + x.get_best_img().image_file
                my_full_list.append(x)
            else:
                x.image_file = dir + 'noimage_light.jpg'
                my_full_list.append(x)
    total = len(my_full_list)

    num_show = 5
    page_length = 20
    page_range, page_list,last_page, next_page,prev_page, page_length,page,first_item,last_item = mypaginator(request,my_full_list,page_length,num_show)
    genus_list = Genus.objects.all()
    context = {
        'page_list': page_list,'type': type, 'gen': gen, 'genus':genus,'alpha':alpha,'display':display,
        'genus_list':genus_list,'subgenus_list': subgenus_list, 'subgenus_obj': subgenus_obj,
        'section_list': section_list, 'section_obj': section_obj, 'genus': genus,
        'subsection_list': subsection_list, 'subsection_obj': subsection_obj,
        'series_list': series_list, 'series_obj': series_obj,
        'page_range': page_range, 'last_page': last_page, 'num_show': num_show, 'page_length': page_length,
        'page': page,'alpha':alpha,'alpha_list':alpha_list,'total':total,
        'first': first_item, 'last': last_item, 'next_page': next_page, 'prev_page': prev_page,
        'level': 'browse', 'title': 'browse', 'section': 'list', 'namespace': 'orchidlist','role':role,
               }
    return render(request, 'orchidlist/browse.html', context)


def browsedist(request):
    dist_list = get_distlist()
    context = {'dist_list':dist_list,
                }
    print("orchidlist/browsedist  ",request.user,dist_list[0].region_name,dist_list[0].regcard)
    return render(request, 'orchidlist/browsedist.html', context)

# All access - at least role = pub
def progeny(request, pid):
    alpha = ''
    sort = ''
    prev_sort = ''
    num_show = 5
    page_length = 30
    page_range = []
    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']

    try:
        species = Species.objects.get(pk=pid)
    except Species.DoesNotExist:
        message = 'This hybrid does not exist! Use arrow key to go back to previous page.'
        return HttpResponse(message)
    genus = species.genus
    des_list = AncestorDescendant.objects.filter(aid=pid)
    if 'page' in request.GET:
        page = request.GET['page']

    if 'sort' in request.GET:
        sort = request.GET['sort']
        sort.lower()

    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
        if alpha == 'ALL' or alpha == 'all':
            alpha = ''
        des_list = des_list.filter(did__pid__species__istartswith=alpha)

    if sort:
        if request.GET.get('prev_sort'):
            prev_sort = request.GET['prev_sort']
        if prev_sort == sort:
            if sort.find('-',0) >= 0:
                sort = sort.replace('-','')
            else:
                sort = '-'+sort
        else:
            # sort = '-' + sort
            prev_sort = sort

    if sort:
        if sort == 'pct':
            des_list = des_list.order_by('-pct','did__pid__genus','did__pid__species')
        elif sort == '-pct':
            des_list = des_list.order_by('pct','did__pid__genus','did__pid__species')
        elif sort == 'img':
            des_list = des_list.order_by('-did__pid__num_image','did__pid__genus','did__pid__species')
        elif sort == '-img':
            des_list = des_list.order_by('did__pid__num_image','did__pid__genus','did__pid__species')
        elif sort == 'name':
            des_list = des_list.order_by('did__pid__genus','did__pid__species')
        elif sort == '-name':
            des_list = des_list.order_by('-did__pid__genus', '-did__pid__species')
        elif sort == 'seed':
            des_list = des_list.order_by('did__seed_id__genus','did__seed_id__species')
        elif sort == 'pollen':
            des_list = des_list.order_by('did__pollen_id__genus','did__pollen_id__species')

        elif sort == '-seed':
            des_list = des_list.order_by('-did__seed_id__genus','-did__seed_id__species')
        elif sort == '-pollen':
            des_list = des_list.order_by('-did__pollen_id__genus','-did__pollen_id__species')
    else:
        des_list = des_list.order_by('did__pid__genus','did__pid__species')
    total = des_list.count()

    page_range, page_list, last_page, next_page, prev_page, page_length, page, first_item, last_item = mypaginator(
            request, des_list, page_length, num_show)

    print("orchidlist/progeny ",request.user, role, " - ", species)
    context = {'des_list':page_list, 'species':species, 'total':total,'alpha':alpha,'alpha_list':alpha_list,
                'sort': sort, 'prev_sort': prev_sort,'tab':'pro','pro':'active',
               'genus':genus, 'page':page,
               'page_range': page_range,'last_page':last_page,'next_page':next_page, 'prev_page':prev_page, 'num_show':num_show, 'first':first_item, 'last':last_item,
               'level':'orchidlist','title':'progeny','section':'Public Area','role':role,'namespace':'detail',
               }
    return render(request, 'orchidlist/progeny.html', context)


# All access - at least role = pub
def progenyimg(request, pid=None):
    num_show = 5
    page_length = 30
    page_range = []

    try:
        species = Species.objects.get(pk=pid)
    except Species.DoesNotExist:
        message = 'This hybrid does not exist! Use arrow key to go back to previous page.'
        return HttpResponse(message)
    genus = species.genus
    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']

    des_list = AncestorDescendant.objects.filter(aid=pid).filter(pct__gt=20)
    des_list = des_list.order_by('-pct')

    img_list = []
    for x in des_list:
        offspring = Hybrid.objects.get(pk=x.did.pid_id)
        offimg = HybImages.objects.filter(pid=x.did.pid_id).filter(rank__gt=3).order_by('?')
        if offimg:
            x.img = offimg[:1][0]
            x.offspring = offspring
            x.pollen = offspring.pollen_id
            x.seed = offspring.seed_id
            img_list.append(x)

    total = len(img_list)
    page_range, page_list, last_page, next_page, prev_page, page_length, page, first_item, last_item = mypaginator(
            request, img_list, page_length, num_show)

    print("orchidlist/progenyimg",request.user, role, " - ", species)
    context = {'des_list':page_list, 'species':species,
                'tab':'proimg','proimg':'active',
               'genus':genus, 'total':total,
               'page_range': page_range,'last_page':last_page, 'num_show':num_show, 'first':first_item, 'last':last_item,
               'level':'orchidlist','title':'progenyimg','section':'Public Area','role':role,'namespace':'detail',
               }
    return render(request, 'orchidlist/progenyimg.html', context)


def get_distlist ():
    dist_list = Localregion.objects.exclude(id=0).order_by('continent_name','region_name','name')
    prevcon = ''
    prevreg = ''
    mydist_list = dist_list
    for x in mydist_list:
        x.concard = x.continent_name.replace(" ", "")
        x.regcard = x.region_name.replace(" ", "")
        x.prevcon = prevcon
        x.prevreg = prevreg
        # mydist_list.append([x, prevcon, prevreg,card] )
        prevcon = x.continent_name
        prevreg = x.region_name

    return mydist_list


def xbrowse(request,gen=None):
    import collections
    type = ''
    genus = ''
    hybrid_list = []
    img_list = []
    subgenus = ''
    section = ''
    subsection = ''
    series = ''
    subgenus_obj = ''
    section_obj = ''
    subsection_obj = ''
    series_obj = ''
    subgenus_list = []
    section_list = []
    subsection_list = []
    series_list = []
    if 'subgenus' in request.GET:
        subgenus = request.GET['subgenus']
        if subgenus:
            subgenus_obj = Subgenus.objects.get(pk=subgenus)
    if 'section' in request.GET:
        section = request.GET['section']
        # print("section = ",section)
        if section:
            try:
                section_obj = Section.objects.get(pk=section)
            except Section.DoesNotExist:
                section_obj = ''
    if 'subsection' in request.GET:
        subsection = request.GET['subsection']
        if subsection:
            try:
                subsection_obj = Subsection.objects.get(pk=subsection)
            except Subsection.DoesNotExist:
                subsection_obj = ''
            # print("subsection = ",subsection_obj.subsection)
            # print("subsection list = ",subsection_list.count())
    if 'series' in request.GET:
        series = request.GET['series']
        if series:
            series_obj = Series.objects.get(pk=series)
    if 'gen' in request.GET:
        gen = request.GET['gen']
        if not gen:
            gen = 0
        intragen_list = Intragen.objects.filter(gen=gen)
        subgenus_list = intragen_list.exclude(subgenus__isnull=True).exclude(subgenus__exact='').filter(gen=gen).distinct().values('subgenus').order_by('subgenus')
        section_list = intragen_list.exclude(section__isnull=True).exclude(section__exact='').filter(gen=gen).distinct().values('section').order_by('section')
        subsection_list = intragen_list.exclude(subsection__isnull=True).exclude(subsection__exact='').filter(gen=gen).distinct().values('subsection').order_by('subsection')
        series_list = intragen_list.exclude(series__isnull=True).exclude(series__exact='').filter(gen=gen).distinct().values('series').order_by('series')
        if subgenus:
            section_list = section_list.filter(subgenus=subgenus)
            subsection_list = subsection_list.filter(subgenus=subgenus)
            series_list = series_list.filter(subgenus=subgenus)
        if section:
            subsection_list = subsection_list.filter(section=section)
            series_list = series_list.filter(section=section)

    # subgenus_list = intragen_list.exclude(subgenus__isnull=True).exclude(subgenus__exact='').filter(gen=gen).distinct().values('subgenus')
    # section_list = intragen_list.exclude(section__isnull=True).exclude(section__exact='').filter(gen=gen).distinct().values('section')
    # subsection_list = intragen_list.exclude(subsection__isnull=True).exclude(subsection__exact='').filter(gen=gen).distinct().values('subsection')
    # series_list = intragen_list.exclude(series__isnull=True).exclude(series__exact='').filter(gen=gen).distinct().values('series')

    pid_list = []
    if 'type' in request.GET:
        type = request.GET['type']
    else:
        type = 'species'
    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']

    if gen:
        genus = Genus.objects.get(pk=gen)
        genus_list = Genus.objects.exclude(status='synonym').filter(Q(num_species__gte=0) | Q(num_hybrid__gte=0))
        species_list = Species.objects.filter(gen=wgenus.pid).exclude(status='synonym').filter(type='species')
        if type == 'species':
            pid_list = Accepted.objects.filter(gen=gen)
            if subgenus:
                pid_list = pid_list.filter(subgenus=subgenus)
            if section:
                pid_list = pid_list.filter(section=section)
            if subsection:
                pid_list = pid_list.filter(subsection=subsection)
            if series:
                pid_list = pid_list.filter(series=series)
        else:
            pid_list = Hybrid.objects.filter(gen=gen)

        species_list = species_list.order_by('species', 'infraspr', 'infraspe')
        hybrid_list = Species.objects.filter(gen=genus.pid).exclude(status='synonym').filter(type='hybrid').order_by('species')
        img_list = Species.objects.filter(gen=gen).exclude(status='synonym').filter(num_image__gt=0)

        if pid_list:
            img_list = img_list.filter(pid__in=pid_list)
        # elif subgenus or section or subsection or series:
        else:
            img_list = []
    else:
        # send_url = "%s?" % (reverse('orchidlist:browsegen'))
        return HttpResponseRedirect("/orchidlist/browsegen")

    img_list = Species.objects.filter(gen=gen).exclude(status='synonym')
    alpha = ''
    if 'alpha' in request.GET:
        alpha = request.GET['alpha']
        if alpha == 'ALL':
            alpha = ''
    if alpha:
        img_list = img_list.filter(species__istartswith=alpha)
    if type == 'species':
        dir = 'utils/images/species/'
        img_list = img_list.filter(type__iexact='species')
    else:
        dir = 'utils/images/hybrid/'
        img_list = img_list.filter(type__iexact='hybrid')

    num_show = 5
    page_length = 20
    if img_list:
        if alpha:
            img_list = img_list.filter(species__istartswith=alpha)
        img_list = img_list.order_by('genus','species')
        total = len(img_list)

        page_range, page_list, last_page, next_page, prev_page, page_length, page, first_item, last_item = mypaginator(
            request, img_list, page_length, num_show)

        my_list = []

        for x in page_list:
            # print("x = ", x)
            img = x.get_best_img()
            if img:
                x.image_file = dir + img.image_file
                my_list.append(x)
            elif request.user.is_authenticated and request.user.tier.tier > 2:
                x.image_file = dir + 'noimage_light.jpg'
                my_list.append(x)
        page_list = my_list
    else:
        page_list = ()
        page_range = 0
        last_page = 0
        next_page = 0
        prev_page = 0
        page = 0
        first_item = ''
        last_item = ''

    context = {
        'page_list': page_list,'type': type, 'gen': gen, 'genus':genus,'alpha':alpha,
        'subgenus_list': subgenus_list, 'subgenus_obj': subgenus_obj,
        'section_list': section_list, 'section_obj': section_obj, 'genus': genus,
        'subsection_list': subsection_list, 'subsection_obj': subsection_obj,
        'series_list': series_list, 'series_obj': series_obj,
        'page_range': page_range, 'last_page': last_page, 'num_show': num_show, 'page_length': page_length,
        'page': page,'alpha':alpha,'alpha_list':alpha_list,'total':total,
        # 'genus_browse_list':genus_browse_list,
        'first': first_item, 'last': last_item, 'next_page': next_page, 'prev_page': prev_page,
        'level': 'browse', 'title': 'browsespc', 'section': 'list', 'namespace': 'orchidlist','role':role,
               }
    print("orchidlist/browse ",request.user)
    return render(request, 'orchidlist/browse.html', context)


def valid_year(year):
    if year and year.isdigit() and 1700 <= int(year) <= 2020:
        return year

def mypaginator(request,full_list,page_length,num_show):
    paginator = ()
    page_list = []
    first_item = 0
    last_item = 0
    next_page = 0
    prev_page = 0
    last_page = 0
    # print("2. >>> full_list = ",len(full_list),page_length,num_show)

    total = len(full_list)
    if page_length > 0:
        paginator = Paginator(full_list, page_length)
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1
        if page == 0:
            page = 1
        try:
            page_list = paginator.page(page)
            last_page = paginator.num_pages
        except(EmptyPage):
            page_list = paginator.page(1)
            last_page = 1
        next_page = page+1
        if next_page > last_page:
            next_page = last_page
        prev_page = page - 1
        if prev_page < 1:
            prev_page = 1


        first_item = (page - 1)* page_length + 1
        last_item = first_item + page_length - 1
        if last_item > total:
            last_item = total
        # Get the index of the current page
        index = page_list.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - num_show if index >= num_show else 0
        end_index = index + num_show if index <= max_index - num_show else max_index
        # My new page range
        page_range = paginator.page_range[start_index:end_index]
    # print("page_length = ",page_length)
    # print("page_list = ",len(page_list))
    # print("page = ",page)
    # print("page_range = ",page_range)
    # print("next_page = ",next_page)
    return(page_range, page_list,last_page,next_page,prev_page, page_length,page,first_item,last_item)
