# -*- coding: utf-8 -*-

import string

from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.vary import vary_on_headers

from gobotany.core import botany
from gobotany.core.models import GlossaryTerm, HomePageImage, Taxon, Video
from gobotany.core.partner import which_partner
from gobotany.plantoftheday.models import PlantOfTheDay
from gobotany.simplekey.groups_order import ordered_pilegroups, ordered_piles

def per_partner_template(request, template_path):
    partner = which_partner(request)
    return '{0}/{1}'.format(partner.short_name, template_path)

# Home page

def home_view(request):
    """View for the home page of the Go Botany site."""

    home_page_images = HomePageImage.objects.order_by('order')
    # Get or generate today's Plant of the Day.
    partner = which_partner(request)
    plant_of_the_day = PlantOfTheDay.get_by_date.for_day(
        date.today(), partner.short_name)
    # Get the Taxon record of the Plant of the Day.
    plant_of_the_day_taxon = None
    try:
        plant_of_the_day_taxon = Taxon.objects.get(
            scientific_name=plant_of_the_day.scientific_name)
    except ObjectDoesNotExist:
        pass

    plant_of_the_day_image = None
    species_images = botany.species_images(plant_of_the_day_taxon)
    if species_images:
        plant_of_the_day_image = botany.species_images(
            plant_of_the_day_taxon)[0]

    return render_to_response('gobotany/home.html', {
            'home_page_images': home_page_images,
            'plant_of_the_day': plant_of_the_day_taxon,
            'plant_of_the_day_image': plant_of_the_day_image,
            }, context_instance=RequestContext(request))

# Teaching page

def teaching_view(request):
    return render_to_response('gobotany/teaching.html', {
            }, context_instance=RequestContext(request))

# About section

def about_view(request):
    return render_to_response('gobotany/about.html', {
           }, context_instance=RequestContext(request))

@vary_on_headers('Host')
def getting_started_view(request):
    youtube_id = ''
    getting_started_video = Video.objects.get(title='Getting Started')
    if getting_started_video:
        youtube_id = getting_started_video.youtube_id

    return render_to_response(
        per_partner_template(request, 'getting_started.html'), {
            'getting_started_youtube_id': youtube_id,
            }, context_instance=RequestContext(request))

def advanced_map_view(request):
    pilegroups = [(pilegroup, ordered_piles(pilegroup))
                  for pilegroup in ordered_pilegroups()]

    return render_to_response('gobotany/advanced_map.html', {
            'pilegroups': pilegroups
            }, context_instance=RequestContext(request))

def glossary_view(request, letter):
    glossary = GlossaryTerm.objects.filter(visible=True).extra(
        select={'lower_term': 'lower(term)'}).order_by('lower_term')

    terms = glossary.values_list('lower_term', flat=True)
    letters_in_glossary = [term[0] for term in terms]

    # Skip any glossary terms that start with a number, and filter to the
    # desired letter.
    glossary = glossary.filter(term__gte='a', term__startswith=letter)

    return render_to_response('gobotany/glossary.html', {
            'this_letter': letter,
            'letters': string.ascii_lowercase,
            'letters_in_glossary': letters_in_glossary,
            'glossary': glossary,
            }, context_instance=RequestContext(request))

def glossary_main_view(request):
    return redirect('site-glossary', letter='a')

def _get_video_dict(title, video):
    youtube_id = ''
    if video:
        youtube_id = video.youtube_id
    return {
        'title': title,
        'youtube_id': youtube_id
    }

def video_view(request):
    # The Getting Started video is first, followed by videos for the pile
    # groups and piles in the order that they are presented in the stepwise
    # pages at the beginning of plant identification.
    videos = []
    getting_started_video = Video.objects.get(title='Getting Started')
    if getting_started_video:
        videos.append({'title': getting_started_video.title,
                       'youtube_id': getting_started_video.youtube_id});

    for pilegroup in ordered_pilegroups():
        videos.append(_get_video_dict(pilegroup.name, pilegroup.video))
        for pile in ordered_piles(pilegroup):
            videos.append(_get_video_dict(pile.name, pile.video))

    return render_to_response('gobotany/video.html', {
           'videos': videos,
           }, context_instance=RequestContext(request))


def contributors_view(request):
    return render_to_response('gobotany/contributors.html', {
       }, context_instance=RequestContext(request))