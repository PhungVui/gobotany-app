"""Rebuild parts of our database that we generate rather than import."""

import csv
import sys

# The GoBotany settings have to be imported before most of Django.
from gobotany import settings
from django.core import management
management.setup_environ(settings)

import bulkup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction

from gobotany.core import models
from gobotany.plantoftheday.models import PlantOfTheDay
from gobotany.search.models import SubgroupResultsPage

import logging
log = logging.getLogger('gobotany.import')

class CSVReader(object):

    def __init__(self, data_file):
        self.data_file = data_file

    def read(self):
        # Open in universal newline mode in order to deal with newlines in
        # CSV files saved on Mac OS.
        with self.data_file.open('rU') as f:
            r = csv.reader(f, dialect=csv.excel, delimiter=',')
            for row in r:
                yield [c.decode('Windows-1252') for c in row]


def rebuild_default_filters(characters_csv):
    """Rebuild default filters for every pile, using CSV data where
       available or choosing 'best' characters otherwise.
    """
    from gobotany.core import importer # here to avoid import loop
    log.info('Importing default filters from characters.csv')

    # Since we do not know whether we have been called directly with
    # "-m" or whether we have been called from .importer as part of a
    # big full import:
    if isinstance(characters_csv, basestring):
        characters_csv = importer.PlainFile('.', characters_csv)

    log.info('  Clearing the DefaultFilter table')
    models.DefaultFilter.objects.all().delete()

    # Read in the file and import its data.

    db = bulkup.Database(connection)
    pile_map = db.map('core_pile', 'name', 'id')
    character_map = db.map('core_character', 'short_name', 'id')

    piles_seen = set()
    table = db.table('core_defaultfilter')
    stuff = importer.read_default_filters(characters_csv)

    for key_name, pile_name, n, character_slug in stuff:
        piles_seen.add(pile_name)
        table.get(
            key=key_name,
            pile_id=pile_map[pile_name],
            order=n,
            character_id=character_map[character_slug],
            )

    # Make sure all piles were covered, and throw in two filters that
    # appear for all piles.

    for pile in models.Pile.objects.all():
        if pile.name not in piles_seen:
            log.error('  No default filters were given for pile %r',
                      pile.name)

        table.get(key='simple', pile_id=pile.id, order=-2,
                  character_id=character_map['habitat_general'])
        table.get(key='simple', pile_id=pile.id, order=-1,
                  character_id=character_map['state_distribution'])

        table.get(key='full', pile_id=pile.id, order=-3,
                  character_id=character_map['habitat_general'])
        table.get(key='full', pile_id=pile.id, order=-2,
                  character_id=character_map['habitat'])
        table.get(key='full', pile_id=pile.id, order=-1,
                  character_id=character_map['state_distribution'])

    # And we are done.

    table.save()


def _remove_sample_species_images(pile_or_group_model):
    """Remove any sample species_images from all piles or all pile groups."""
    print '  Removing old images:'
    for pile in pile_or_group_model.objects.all():
        print '    %s ' % pile.name
        image_count = pile.sample_species_images.count()
        if image_count:
            print '      removing %d old images' % image_count
            pile.sample_species_images.clear()
        else:
            print '      none'


def rebuild_sample_pile_group_images(name=None):
    """Assign sample species images to each pile group."""

    from gobotany.core import importer  # here to avoid import loop

    fileopener = importer.get_data_fileopener(name)
    pilegroup_csv = fileopener('pile_group_info.csv')

    print 'Removing old sample pile-group images:'
    _remove_sample_species_images(models.PileGroup)

    print '  Scanning species images'
    taxontype = ContentType.objects.get_for_model(models.Taxon)
    imagedict = { image.image.name.rsplit('/')[-1]: image for image in
                  models.ContentImage.objects.filter(content_type=taxontype) }

    print '  Adding pile-group images from CSV data:'
    for row in importer.open_csv(pilegroup_csv):

        # Skip junk rows.
        if row['name'].lower() in ['all', 'unused']:
            continue

        pile_group = models.PileGroup.objects.get(name=row['name'])
        print '    PileGroup:', pile_group.name

        # Go through the image filenames specified in the CSV data and
        # look for them in the image dict.  If found, add them to the
        # pile group as sample species images.

        image_filenames = row['image_filenames'].split(';')
        for filename in image_filenames:

            print '      filename:', filename,

            # Skip unknown filenames.
            image = imagedict.get(filename, None)
            if image is None:
                print '- UNKNOWN'
                continue

            pgimage = models.PileGroupImage(
                content_image=image, pile_group=pile_group)

            # Set an ordering field, editable in the Admin.
            pgimage.order = image.id
            pgimage.save()

            print '- found'


def rebuild_sample_pile_images(name=None):
    """Assign sample species images to each pile."""

    from gobotany.core import importer  # here to avoid import loop

    fileopener = importer.get_data_fileopener(name)
    pile_csv = fileopener('pile_info.csv')

    print 'Removing old sample pile images:'
    _remove_sample_species_images(models.Pile)

    print '  Scanning species images'
    taxontype = ContentType.objects.get_for_model(models.Taxon)
    imagedict = { image.image.name.rsplit('/')[-1]: image for image in
                  models.ContentImage.objects.filter(content_type=taxontype) }

    print '  Adding pile images from CSV data:'
    for row in importer.open_csv(pile_csv):

        # Skip junk rows.
        if row['name'].lower() in ['all', 'unused']:
            continue

        pile = models.Pile.objects.get(name=row['name'].title())
        print '    Pile:', pile.name

        # Go through the image filenames specified in the CSV data and
        # look for them in the image list. If found, add them to the
        # pile as sample species images.

        image_filenames = row['image_filenames'].split(';')
        for filename in image_filenames:

            print '      filename:', filename,

            # Skip unknown filenames.
            image = imagedict.get(filename, None)
            if image is None:
                print '- UNKNOWN'
                continue

            pimage = models.PileImage(content_image=image, pile=pile)

            # Set an ordering field, editable in the Admin.
            pimage.order = image.id
            pimage.save()

            print '- found'


def rebuild_plant_of_the_day(include_plants='SIMPLEKEY'):   # or 'ALL'
    """Rebuild the Plant of the Day list without wiping it out.

    This means that plant data can be reloaded and the Plant of the Day
    list then updated to include the current list of plants, minus any
    exclusions. This will ensure any new plants (or those with changed
    names) make it into the list.

    Any records in the list that do not have their last_modified field
    showing the latest rebuild date are likely old and should be deleted.
    For now, this is left as an occasional manual maintenance task.
    """
    if include_plants not in ['SIMPLEKEY', 'ALL']:
        print '  Unknown include_plants value: %s' % include_plants
    else:
        print '  Rebuilding Plant of the Day list (%s):' % include_plants
        for partner_site in models.PartnerSite.objects.all():
            print '    Partner site: %s' % partner_site
            species = models.PartnerSpecies.objects.filter(
                partner=partner_site)
            if include_plants == 'SIMPLEKEY':
                species = species.filter(simple_key=True)
            for s in species:
                try:
                    potd = PlantOfTheDay.objects.get(
                        scientific_name=s.species.scientific_name,
                        partner_short_name=s.partner.short_name)
                    # Save the existing record so its last_updated field
                    # will be updated.
                    potd.save()
                except ObjectDoesNotExist:
                    # Create a new Plant of the Day record.
                    potd = PlantOfTheDay(
                        scientific_name=s.species.scientific_name,
                        partner_short_name=s.partner.short_name)
                    potd.save()


def rebuild_split_remaining_non_monocots():
    """Split the Remaining Non-Monocots pile into two piles, one with
    alternate-leaved plants and the other with plants having non-alternate
    leaves. This is for making smaller and faster results sets in the Full
    and Simple keys from what was one very large pile. Doing this in code
    avoids having to split the piles by hand and make a lot of attendant
    Access database changes. This might be temporary pending an eventual
    move to using the Admin site for maintaining plant data.
    """
    log.info('Splitting the Remaining Non-Monocots pile in two')

    split_piles = ['Alternate Remaining Non-Monocots',
                   'Non-Alternate Remaining Non-Monocots']
    for pile_name in split_piles:
        # Delete any existing split Remaining Non-Monocots piles along
        # with their default filters. Also delete any existing
        # SubgroupResultsPage records for the split piles.
        try:
            pile = models.Pile.objects.get(name=pile_name)

            default_filters = models.DefaultFilter.objects.filter(
                pile=pile)
            for default_filter in default_filters:
                default_filter.delete()
            if len(default_filters) > 0:
                log.info('Deleted default filters for pile: %s' % pile_name)
            else:
                log.info(
                    'No default filters to delete for pile: %s' % pile_name)

            subgroup_results_pages = SubgroupResultsPage.objects.filter(
                subgroup=pile)
            for subgroup_results_page in subgroup_results_pages:
                subgroup_results_page.delete()
            if len(subgroup_results_pages) > 0:
                log.info('Deleted subgroup results pages for pile: %s' %
                         pile_name)
            else:
                log.info('No subgroup results pages to delete for pile: %s' %
                         pile_name)

            pile.delete()
            log.info('Deleted pile: %s' % pile_name)
        except ObjectDoesNotExist:
            log.info('No pile exists: %s' % pile_name)

    # Create a pile for alternate-leaved plants.
    try:
        alt_pile = models.Pile.objects.get(name='Remaining Non-Monocots')
        alt_pile.pk = None
        alt_pile.name = 'Alternate ' + alt_pile.name
        alt_pile.slug = 'alternate-' + alt_pile.slug
        alt_pile.save()
        log.info('Created pile: %s' % alt_pile.name)
    except ObjectDoesNotExist:
        log.error('Remaning Non-Monocots pile does not exist')
        return

    # Create a pile for non-alternate-leaved plants.
    try:
        non_alt_pile = models.Pile.objects.get(name='Remaining Non-Monocots')
        non_alt_pile.pk = None
        non_alt_pile.name = 'Non-Alternate ' + non_alt_pile.name
        non_alt_pile.slug = 'non-alternate-' + non_alt_pile.slug
        non_alt_pile.save()
        log.info('Created pile: %s' % non_alt_pile.name)
    except ObjectDoesNotExist:
        log.error('Remaning Non-Monocots pile does not exist')
        return

    # Create default filters for each of the split piles.
    try:
        master_pile = models.Pile.objects.get(name='Remaining Non-Monocots')
        default_filters = models.DefaultFilter.objects.filter(
            pile=master_pile)
        for default_filter in default_filters:
            for pile_name in split_piles:
                try:
                    pile = models.Pile.objects.get(name=pile_name)
                    default_filter.pk = None
                    default_filter.pile = pile
                    default_filter.save()
                    log.info('Created default filter for %s: %s (key: %s)' %
                             (pile.name,
                              default_filter.character.friendly_name,
                              default_filter.key.capitalize()))
                except ObjectDoesNotExist:
                    log.error('%s pile does not exist')
                    return
    except ObjectDoesNotExist:
        log.error('Remaining Non-Monocots pile does not exist')
        return

    # Alter the data as needed (set plants, images, labels, etc.).

    # Main heading on the results page
    alt_pile.friendly_title = ('Other herbaceous, flowering plants with '
                               'alternate leaves')
    non_alt_pile.friendly_title = ('Other herbaceous, flowering plants with '
                                   'opposite, whorled or no leaves')

    # Pile subheading on the page
    # This is currently blank in the big pile, so leave it that way for
    # the split piles.

    # Key characteristics section
    alt_pile.key_characteristics = ('This very diverse group is generally '
        'not woody, grass-like, or aquatic, and does not have composite '
        'flower heads. These plants have alternate leaves that join the '
        'stem at different levels, not opposite each other or in whorls; '
        'be sure to look at the arrangement of leaves in the lower half of '
        'the flowering stem.')
    non_alt_pile.key_characteristics = ('These species are herbaceous plants '
        'with only all basal, opposite, or whorled leaves; they are not '
        'aquatic, grass-like, and do not have composite flower heads. Some '
        'species are parasitic or lack green leaves.')

    # Exceptions
    alt_pile.notable_exceptions = ('Leaf arrangement can vary from the '
        'bottom to top of the stem, or in young vs. older plants, so try to '
        'look at several plants. Some crowded leaves may look opposite or '
        'whorled, but look closely to see whether there is actually space '
        'between them on the stem. Some species have narrow leaves where '
        'it\'s hard to see the veins, so look for other features such as '
        'petal number, presence of leaf teeth, etc.')
    non_alt_pile.notable_exceptions = ('Leaf arrangement can vary from the '
        'bottom to top of the stem, or in young vs. older plants, so try to '
        'look at several plants. Some crowded leaves may look opposite or '
        'whorled, but look closely to see whether there is actually space '
        'between them on the stem. Some species have narrow leaves where '
        'it\'s hard to see the veins, so look for other features such as '
        'petal number, presence of leaf teeth, etc. Some species (such as '
        'teasel or pincushions) have flower heads that look like those of '
        'the aster family, but look closely: the flowers usually have four '
        'tooth-like lobes (a rare condition in the aster family) and the '
        'fruit is partially enclosed in a tubular bract.')

    # Video
    # This is temporarily left the same for both of the split piles but
    # two different videos are likely warranted.

    # Get the species to use in each of the piles.
    alt_species = master_pile.species.filter(
        character_values__value_str='alternate')
    non_alt_species = master_pile.species.exclude(
        character_values__value_str='alternate')

    # Set the species in each of the split piles.
    for pile, pile_species in [(alt_pile, alt_species),
                               (non_alt_pile, non_alt_species)]:
        pile.species.add(*pile_species)
        log.info('%s pile: added %d species.' % (pile.name,
                                                 pile_species.count()))

    # TODO: Set sample species images for the Level 2 pages.

    # Save all the changes.
    alt_pile.save()
    non_alt_pile.save()

    # Create SubgroupResultsPage model instances
    for pile_name in split_piles:
        for key in ['Simple']: #, 'Full']: # not needed just yet for Full Key
            try:
                pile = models.Pile.objects.get(name=pile_name)
                title = '%s: %s Key' % (pile.friendly_title, key)
                subgroup_results_page, created = \
                    SubgroupResultsPage.objects.get_or_create(
                        title=title,
                        main_heading=pile.friendly_title,
                        subgroup=pile)
                log.info('Created SubgroupResultsPage for %s (key: %s)' %
                         (pile.name, key))
            except ObjectDoesNotExist:
                log.error('%s pile does not exist')
                return

    # Default filters:
    # - omit Leaf Arrangement from the Alternate pile


def main():
    from .importer import start_logging
    start_logging()

    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: rebuild THING {args}"
        exit(2)
    thing = sys.argv[1]
    function_name = 'rebuild_' + thing
    if function_name in globals():
        function = globals()[function_name]
        wrapped_function = transaction.commit_on_success(function)
        wrapped_function(*sys.argv[2:])
    else:
        print >>sys.stderr, "Error: rebuild target %r unknown" % thing
        exit(2)

if __name__ == '__main__':
    main()
