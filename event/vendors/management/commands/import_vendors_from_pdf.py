from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from categories.models import Category
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Import vendors from EventsExclusive PDF data'

    def handle(self, *args, **kwargs):
        # Get or create a default admin user for vendors
        admin_user, _ = User.objects.get_or_create(
            email='admin@ghanaevents.com',
            defaults={
                'username': 'admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        # Vendor data from PDF organized by category
        vendors_data = {
            'venues': [
                'The Underbridge', 'Enclave Gardens', 'Lotus Gardens', 'The Savannah Venue',
                'Gold Bird Event Venue', 'Red Carpet Events Centre', 'Goshen Lizani Event Centre',
                'Fiesta Royale Hotel', 'Signature Venue', 'Luna Gardens', 'Dor Events',
                'Kobi\'s Events', 'Accra Polo Club Grounds', 'Northwood Garden Events Centre',
                'East Legon Event Centre', 'L\'amour events garden', 'De Icon events centre',
                'Glass Gardens', 'Wan-Shi Gardens', 'Velvet Gree Garden', 'Fantasy Dome',
                'Legendary Capital Events Centre', 'Skybox event center', 'Rooftop Events Center',
                'Shanti Gardens', 'Bako Events center', 'Pearly Gate Gardens',
                'Berliner Platz Event Center', 'Combos & Casa', 'Velvet Green Garden',
                'Estee\'s Bee Event Centre', 'Subtle Class Event Centre', 'Stoneview Event Center',
                'East Garden Event Centre', 'Baroness Garden', 'The Garden at East Legon',
                'Zinnia Events Center', 'Jees Royal Event Center', 'The Queen\'s Court Event Centre',
                'The Fitzgerald', 'Idrowhyt Event Center', 'New Harlem Event Center',
                'The Page Center', 'Dolphins Event Center', 'M&S Eden Event Center',
                'Dreamz & Memoriez Events Garden', 'Achimota Royale Events Center',
                'The Venetian Events Centre & Rentals', 'De Gyeelette', 'Bex Events Centre',
                'Enbbie Gardens',
            ],
            'catering': [
                'City meals Ghana', 'HildeChris Catering Services', 'Joy Delicacies Catering and events',
                'Flair Catering Services', 'Atlantic Catering and Logistics', 'Nana Bee Select',
                'Newrest Ghana', 'Prestige Catering Services', 'Food Bank', 'Mens cook',
                'Zesuza Catering Service', 'Capitol Catering', 'Grill Sane Event and Catering Services',
                'Nutella Catering Services', 'SaS kitchen', 'Selley\'s Catering Services',
                'Frankev Catering Services', 'Bluespoon catering Services', 'Foodmuse kitchen',
                'Garnish and Glazel catering Services', 'Fina\'s Catering Services',
                'Aduqueen\'s Catering Services', 'Magdaib Events and Catering Services',
                'April Tilly Enterprise', 'Culinary de Phil& Events', 'Steezer\'s Kitchen',
                'M.O.D Catering Services', 'NAS Catering Services', 'Fairy Queen foods',
                'Malindis catering', 'Kadina Catering Services', 'Bisdo Events and Catering Services',
                'Jemdah Catering Services Ltd', 'Violetta Catering Services', 'Ellohim catering Services',
                'Donlincolns Catering Services', 'Tidan Catering Services', 'Nyonyo foods',
                'Mephila Catering Services', 'Silver Refined Foods', 'Magic bite Restaurant',
                'The Meal Box', 'Rych Catering Services', 'Trafix Catering Services',
                'Selipete Catering Services', 'Von Catering Services', 'Servair Ghana ltd',
                'SA catering Services', 'PrisGee Catering Services', 'Twumwoah Fresh',
            ],
            'fashion-designers': [
                'Madikah Gh', 'Davidson\'s Bridal', 'Shapes and Nelson', 'Sima Brew',
                'Royal Couture', 'Heritage Clothing', 'Juus Fashion and beauty', 'Jennifer Turkson',
                'Kimo Wa', 'FD Fashion House', 'Royal Nakor Design and fabrics', 'Onyansani',
                'Pistis gh', 'KVMAn', 'Afariwa Styles', 'Turquoise_hautecouture',
                'Sarah Christian', 'Sadia Sanusi', 'Modabertha', 'Rexkojogh',
                'HouseofPaon', 'Perfect Fit Stitches', 'Stitchperfectgh', '3d_fashion',
                'Abeveesfabrics', 'Rigmor_gh', 'Yaaowubaa', 'Seys Fashion', 'Clasikqdiane',
            ],
            'fabrics': [
                'lenpa fabrics', 'Fabrics and beyond', 'Fabrics web', 'Fabrics lots gh',
                'Lush fabrics', 'Fabrics haven', 'House of Perkie', 'Mayz Fabrics',
                'Lacesnmore', 'Nyan fabrics', 'Kejeron Fabrics', 'Daya fabrics',
                'Benewaa Fabrics', 'Ntomapa fabrics', 'Nikao fabrics', 'Emefabrics',
                'Lush fabrics gh', 'Fabricsbyjil', 'Lace n slay', 'Fabrics hubgh',
                'Lisse Fabrics', 'Snefabrics', 'Glitz allure fabrics', 'Sarah\'s Fabrics',
                'Berylluxurylaces', 'Ladel fabrics', 'Fabrics ring', 'Fabrics by Maud',
                'Spark fabrics', 'Silk haven',
            ],
            'favours': [
                'Lollistar souvenirs', 'Pakaging First Gh', 'Event Tips', 'DeritJay Sent',
                'Package Boss', 'Cyl Events and supplies', 'Most Trusted Gift shop',
                'lotty Bridals', 'Lush_n_lilies', 'Le souvenirs gh', 'Ish favors',
                'Souvenirs and gift gh', 'Beautiful.giftsgh', 'Bewishful.co',
            ],
            'photographers': [
                'parz zi', 'Jema Photography', 'mesus.studios', 'ghogphoto',
                'officialbigdealweddings', 'mcefilms', 'purpletwirlevents', 'westmadethat',
                'ansahkenphotography', 'nana_gaza', 'Perfect balloons and more', 'Phil_os_films',
                'Pixah Photo', 'Captureville', 'blaqeyeconceptgh', 'ohene_kay_photography',
                'Focusnblur', 'Dr8NN', 'Kingkwekuananse_photography', 'Chocolate shot it',
                'Logopehphotography', 'Fotokonceptgh', 'vonkwamekyere', 'Unclefi studios',
                'nanakay studios', 'Focusshotsgh', 'Nelzconcept', 'Adu Kofi',
                'Kwadwo Asante photography', 'bentxilweddings', 'King kwekuanase photography',
                'Blageyeconceptglobal', 'Raelsilver_rs', 'kaymora_studios', 'Tailored memories',
                'Bliss elevengh', 'Asap photography', 'Weddings by Quan', 'Nii Hammondstudios',
            ],
            'drinks': [
                'Berries Cocktail', 'Hernectar_juice', 'Cocktail essentials gh', 'abisfoodlab',
                'chill and serve gh', 'Kays cocktail Bar',
            ],
            'event-planners': [
                'Events By Macel', 'Essydelevents', 'Weddings withTeeJay', 'Uniquely events',
                'Stylish Sueno', 'Complete Events', 'Event buzzgh', 'Bliss experiencegh',
                'philipmerevents', 'letsbeseated', 'laalaevents', 'lionheart Events',
                'Geez Events', 'Cling Events Gh', 'crystalhaze events', 'Amasah Blankson',
                'Honeycomb event Design', 'Events Pr', 'Creative Ideas Ltd', 'Dor Ev',
                'Conceptz Ghana Event and Audiovisual', 'Eventsweb Ghana', 'Peach Diamond Events',
                'Oni Events and Planners', 'Pearly Petal Events', 'The Eventive Xperience',
                'Masab Events', 'Bemine Ghana', 'Annie The Planner', 'Events assist_gh',
                'eventellz', 'elieonaevents', 'hcevents gh', 'bba events Ghana',
                'Indigo events', 'likenevents_gh', 'Dustin events', 'UniqueeventsPlanning',
                'Detailed events', 'Innovationseventswbm', 'Whitofmiracles', 'Edwinabanda',
                'hertys events gh', 'PurpleoysterEvents', 'Stalyt_events_gh', 'Uniquefloralcentre',
                'Deen_eventsandrentals', 'Sprout affair',
                # Marketing and Communication vendors
                'Wedding memories', 'Yellow man shot', 'live weddings with Kwaku', 'Mirth media',
                'The king emzy', 'Reelsbynana kwame', 'Eventsblogafrica', 'Razakstyles',
                'Shots by her gh', 'Nextdayreelcaps', 'Ab or do', 'Yhaw focus',
                'Capturedbyhector', 'Tales on the aisle',
            ],
            'djs': [
                'Finest_ditoyor', 'Frankiee', 'DJ_ ernie', 'DJ Vyrusky', 'Deejayovuk',
                'djwallpaper', 'DJ phantom gh', 'Djfrnk', 'Djslimbeast',
            ],
        }

        total_created = 0
        total_skipped = 0

        for category_slug, vendor_names in vendors_data.items():
            # Get the category
            try:
                category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Category not found: {category_slug}. Please run: python manage.py seed_categories')
                )
                continue

            self.stdout.write(f'\nImporting {len(vendor_names)} vendors for category: {category.name}')

            for vendor_name in vendor_names:
                # Check if vendor already exists
                vendor_slug = slugify(vendor_name)
                if Vendor.objects.filter(slug=vendor_slug).exists():
                    total_skipped += 1
                    self.stdout.write(self.style.WARNING(f'  ⊗ Skipped (exists): {vendor_name}'))
                    continue

                # Create vendor with placeholder data
                vendor = Vendor.objects.create(
                    user=admin_user,
                    name=vendor_name,
                    slug=vendor_slug,
                    category=category,
                    description=f'{vendor_name} is a professional {category.name.lower()} service provider in Accra, Ghana.',
                    address='Accra, Ghana',
                    city='Accra',
                    neighborhood='',
                    phone_number='+233 XX XXX XXXX',  # Placeholder
                    email=f'{vendor_slug}@example.com',  # Placeholder
                    website='',
                    price_tier='medium',
                    rating=Decimal('0.00'),
                    reviews_count=0,
                    verified=False,
                    status='pending',  # Set to pending for admin review
                )

                total_created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {vendor_name}'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully created {total_created} vendors'))
        self.stdout.write(self.style.WARNING(f'⊗ Skipped {total_skipped} existing vendors'))
        self.stdout.write('='*60)
        self.stdout.write(f'\nNext steps:')
        self.stdout.write(f'1. Go to http://localhost:8000/admin/vendors/vendor/')
        self.stdout.write(f'2. Filter by status="pending" to see all new vendors')
        self.stdout.write(f'3. Update contact info (phone, email) for each vendor')
        self.stdout.write(f'4. Approve vendors by changing status to "active" and verified=True')
        self.stdout.write(f'5. You can bulk approve using the admin action: "Approve selected vendors"\n')
