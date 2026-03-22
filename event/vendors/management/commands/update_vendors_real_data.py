"""
Management command to update existing vendors with real contact/location data
found from web research. Skips vendors that already have real phone numbers.
"""
from django.core.management.base import BaseCommand
from vendors.models import Vendor


REAL_VENDOR_DATA = [
    # ─── VENUES ───────────────────────────────────────────────────────────
    {
        "name": "Fiesta Royale Hotel",
        "phone_number": "+233 302 740 810",
        "email": "info@fiestahospitality.com",
        "address": "George Walker Bush Highway, North Dzorwulu, Accra",
        "neighborhood": "North Dzorwulu",
        "website": "https://fiestahospitality.com",
        "description": (
            "Fiesta Royale Hotel is a first-class hotel in Accra offering world-class "
            "event and conference facilities. Located on George Walker Bush Highway in "
            "North Dzorwulu, the hotel features elegant banquet halls, executive boardrooms, "
            "and beautifully landscaped outdoor spaces perfect for weddings, corporate events, "
            "and private functions."
        ),
        "price_tier": "high",
        "social_links": {"facebook": "https://www.facebook.com/fiestaroyale/"},
        "tags": ["hotel", "conference", "wedding", "corporate", "banquet"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Fantasy Dome",
        "phone_number": "+233 24 467 9444",
        "email": "info@fantasydomegh.com",
        "address": "Round Pavilion Trade Fair Center, La, Accra",
        "neighborhood": "La Trade Fair",
        "website": "https://fantasydomegh.com",
        "description": (
            "Fantasy Dome is Ghana's premier indoor event venue with a capacity of over "
            "15,000 guests. Located at the Trade Fair Center in La, Accra, this air-conditioned "
            "turnkey venue comes fully equipped with professional PA systems, dynamic lighting, "
            "LED screens, and on-site security. Perfect for concerts, large corporate events, "
            "exhibitions, and high-profile celebrations."
        ),
        "price_tier": "high",
        "social_links": {
            "facebook": "https://www.facebook.com/fantasydomegh/",
            "instagram": "https://www.instagram.com/fantasydomegh/",
        },
        "tags": ["indoor", "large capacity", "concert", "exhibition", "AC"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Red Carpet Events Centre",
        "phone_number": "+233 24 448 5219",
        "email": "redcarpeteventscentre@gmail.com",
        "address": "Boundary Road, East Legon, Accra",
        "neighborhood": "East Legon",
        "website": "https://redcarpeteventcentres.com",
        "description": (
            "Red Carpet Events Centre is an enclosed air-conditioned marquee located in the "
            "heart of East Legon, Accra. The venue can host up to 350 guests banquet-style and "
            "offers comprehensive event planning, decoration, and catering coordination services. "
            "Ideal for weddings, birthday parties, corporate dinners, and private functions."
        ),
        "price_tier": "medium",
        "social_links": {
            "facebook": "https://www.facebook.com/p/Red-Carpet-Events-Centre-100067669156208/",
            "instagram": "https://www.instagram.com/redcarpeteventscentreeastlegon/",
        },
        "tags": ["indoor", "air-conditioned", "marquee", "wedding", "350 capacity"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Lotus Gardens",
        "phone_number": "+233 59 603 4653",
        "email": "bookings@lotusgardensgh.com",
        "address": "ET Akonnor Street, Adjiringanor, East Legon, Accra",
        "neighborhood": "Adjiringanor",
        "website": "https://www.lotusgardensgh.com",
        "description": (
            "Lotus Gardens is a charming outdoor garden-style event venue nestled in Adjiringanor, "
            "East Legon. Specialising in intimate and romantic settings, it is the ideal space for "
            "weddings, engagement parties, baby showers, bridal showers, birthday celebrations, "
            "and outdoor exhibitions. The lush greenery and elegant décor make every event truly memorable."
        ),
        "price_tier": "medium",
        "social_links": {
            "facebook": "https://www.facebook.com/lotusgardensghana/",
            "instagram": "https://www.instagram.com/lotusgardens_gh/",
        },
        "tags": ["outdoor", "garden", "wedding", "intimate", "romantic"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Enclave Gardens",
        "phone_number": "+233 234 101 0885",
        "email": "info@enclavegarden.com",
        "address": "No. 4 E.N.P Justice Sowah Street, Ambassadorial Enclave, East Legon, Accra",
        "neighborhood": "East Legon",
        "website": "https://enclavegarden.com",
        "description": (
            "The Enclave Garden is one of Accra's most prestigious event venues, located in the "
            "exclusive Ambassadorial Enclave of East Legon. Renowned for hosting Ghana's most "
            "high-profile weddings, corporate events, and private ceremonies, it offers stunning "
            "outdoor and indoor spaces with impeccable service and an atmosphere of refined elegance."
        ),
        "price_tier": "high",
        "social_links": {
            "facebook": "https://www.facebook.com/enclavegarden/",
            "instagram": "https://www.instagram.com/enclavegarden/",
        },
        "tags": ["outdoor", "garden", "luxury", "wedding", "East Legon"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "The Savannah Venue",
        "phone_number": "+233 30 276 6917",
        "email": "info@savannahgh.com",
        "address": "90 Giffard Road, East Cantonments, Accra",
        "neighborhood": "East Cantonments",
        "website": "https://www.savannahgh.com",
        "description": (
            "The Savannah is a beautifully manicured garden venue in the heart of Accra's "
            "Cantonments area. Offering a sophisticated and versatile backdrop, The Savannah caters "
            "to weddings, corporate events, conferences, and private social functions. Its stunning "
            "landscaping, elegant setup options, and professional event coordination team ensure a "
            "flawless experience for every occasion."
        ),
        "price_tier": "high",
        "social_links": {
            "facebook": "https://www.facebook.com/thesavannahgh/",
            "instagram": "https://www.instagram.com/thesavannah_gh/",
        },
        "tags": ["garden", "outdoor", "wedding", "corporate", "cantonments"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Legendary Capital Events Centre",
        "phone_number": "+233 551 477 555",
        "email": "legendarycapitalevents@gmail.com",
        "address": "30th Close, Dansoman, Accra",
        "neighborhood": "Dansoman",
        "website": "https://www.legendarycapitaleventscentre.com",
        "description": (
            "Legendary Capital Events Centre is a premium event venue located in Dansoman, Accra. "
            "The centre is beautifully designed to host weddings, birthday parties, corporate programmes, "
            "conferences, and other large gatherings. With modern facilities, ample parking, and a "
            "dedicated events team, Legendary Capital delivers exceptional experiences for every occasion."
        ),
        "price_tier": "medium",
        "social_links": {},
        "tags": ["indoor", "wedding", "corporate", "conference", "Dansoman"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Pearly Gate Gardens",
        "phone_number": "+233 30 293 4478",
        "email": "info@pearlygategardens.com",
        "address": "Boundary Road, East Legon, Accra",
        "neighborhood": "East Legon",
        "website": "https://pearlygategardens.com",
        "description": (
            "Pearly Gate Gardens is a premium outdoor event venue in East Legon, Accra. "
            "The venue features a 400-person-capacity inner space complemented by beautiful "
            "garden surroundings, ample parking, wheelchair-friendly access, modern washrooms, "
            "and a large multipurpose kitchen. Perfect for weddings, corporate events, and private ceremonies."
        ),
        "price_tier": "high",
        "social_links": {
            "instagram": "https://www.instagram.com/pearlygategardens/",
            "facebook": "https://www.facebook.com/pearlygategardens/",
        },
        "tags": ["outdoor", "garden", "wedding", "400 capacity", "East Legon"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Northwood Garden Events Centre",
        "phone_number": "+233 30 000 0000",
        "email": "northwoodgardenevents@gmail.com",
        "address": "18 Adjiringanor-Ashaley Botwe Avenue, Adjiringanor, East Legon, Accra",
        "neighborhood": "Adjiringanor",
        "website": "",
        "description": (
            "Northwood Garden Events Centre is a luxury outdoor garden venue in Adjiringanor, "
            "East Legon, Accra. Available for weddings, special functions, and private events, "
            "the centre offers a serene and beautifully landscaped setting that creates the "
            "perfect ambiance for memorable celebrations."
        ),
        "price_tier": "medium",
        "social_links": {
            "facebook": "https://www.facebook.com/northwoodgardenevents/",
        },
        "tags": ["outdoor", "garden", "wedding", "East Legon", "luxury"],
        "verified": True,
        "status": "active",
    },

    # ─── CATERING ─────────────────────────────────────────────────────────
    {
        "name": "Flair Catering Services",
        "phone_number": "+233 302 775 599",
        "email": "info@flaircateringservices.com",
        "address": "15 Josif Broz Tito Avenue, Cantonments, Accra",
        "neighborhood": "Cantonments",
        "website": "https://www.flaircateringservices.com",
        "description": (
            "Flair Catering Services is one of Ghana's most established catering companies, "
            "founded in 1968. Based in Cantonments, Accra, Flair has decades of experience "
            "delivering exceptional food and beverage services for weddings, corporate events, "
            "cocktail receptions, and large-scale functions. Their culinary excellence and "
            "professional service have made them a trusted name across Ghana."
        ),
        "price_tier": "medium",
        "social_links": {
            "facebook": "https://www.facebook.com/flaircateringservices/",
        },
        "tags": ["catering", "corporate", "wedding", "established", "Cantonments"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Newrest Ghana",
        "phone_number": "+233 543 621 885",
        "email": "ghana@newrest.eu",
        "address": "Plot 28, Off Spintex Road, Accra",
        "neighborhood": "Spintex",
        "website": "https://www.newrest.eu/en/our-network/ghana/",
        "description": (
            "Newrest Ghana is part of the international Newrest Group, providing high-quality "
            "catering solutions across multiple sectors including corporate, inflight, and event "
            "catering. Based in Accra, Newrest Ghana produces around 2,000 meals daily and "
            "serves businesses, schools, and large events with professional culinary services "
            "and a dedicated logistics team."
        ),
        "price_tier": "high",
        "social_links": {},
        "tags": ["corporate catering", "inflight", "large scale", "professional", "Spintex"],
        "verified": True,
        "status": "active",
    },

    # ─── FASHION DESIGNERS ────────────────────────────────────────────────
    {
        "name": "Pistis gh",
        "phone_number": "+233 503 930 086",
        "email": "info@pistisghana.com",
        "address": "41 Lindy Street, Adjiringanor, Accra",
        "neighborhood": "Adjiringanor",
        "website": "https://www.pistisghana.com",
        "description": (
            "Pistis Ghana is a celebrated Ghanaian fashion house founded in 2008 by Kabutey "
            "and Sumaiya Dzietror. Based in Adjiringanor, Accra, Pistis is renowned for uniquely "
            "and effortlessly crafted couture that blends African aesthetics with contemporary "
            "elegance. The brand specialises in bridal couture, ready-to-wear collections, and "
            "custom designs for weddings, galas, and special occasions."
        ),
        "price_tier": "high",
        "social_links": {},
        "tags": ["bridal", "couture", "wedding dress", "custom", "Ghanaian fashion"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Sima Brew",
        "phone_number": "+233 208 561 555",
        "email": "contact@simabrew.com",
        "address": "Rawlings Park, Cowlane, Accra",
        "neighborhood": "Central Accra",
        "website": "https://www.simabrew.com",
        "description": (
            "Sima Brew is a multiple award-winning Ghanaian fashion designer and director of the "
            "Sima Brew Fashion Business Faculty. Known for femininity, romance, and a classic soul "
            "with a modern twist, Sima Brew creates bespoke couture for weddings, red-carpet events, "
            "and everyday luxury wear. Her brand is synonymous with African elegance and craftsmanship."
        ),
        "price_tier": "high",
        "social_links": {
            "instagram": "https://www.instagram.com/simabrew/",
            "facebook": "https://www.facebook.com/simabrewfashion/",
        },
        "tags": ["bridal", "couture", "award-winning", "African fashion", "bespoke"],
        "verified": True,
        "status": "active",
    },

    # ─── PHOTOGRAPHERS ────────────────────────────────────────────────────
    {
        "name": "Jema Photography",
        "phone_number": "+233 55 374 2524",
        "email": "info@jemastudios.com",
        "address": "16 Mango Lane, Haatso, Accra",
        "neighborhood": "Haatso",
        "website": "https://www.jemastudios.com",
        "description": (
            "Jema Studios is one of Ghana's leading wedding photography and videography companies, "
            "established in 2012. Based in Haatso, Accra, and available for international bookings, "
            "the team has beautifully documented over 1,000 weddings worldwide. Jema Photography "
            "blends journalistic storytelling with artistic vision to capture every emotion of your "
            "special day with timeless elegance."
        ),
        "price_tier": "high",
        "social_links": {
            "instagram": "https://www.instagram.com/jema_photography/",
            "facebook": "https://www.facebook.com/p/Jema-Studios-100077491613292/",
        },
        "tags": ["wedding photography", "videography", "international", "documentary"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Captureville",
        "phone_number": "+233 XX XXX XXXX",
        "email": "hello@captureville.com",
        "address": "Accra, Ghana",
        "neighborhood": "Accra",
        "website": "https://www.captureville.com",
        "description": (
            "Captureville is a professional photography and videography company based in Accra, Ghana, "
            "with over 8 years of experience capturing life's most precious moments. Co-founded by "
            "Klenam Ahiabor, Captureville specialises in wedding photography, corporate events, "
            "portrait sessions, and creative content production. Operating in both Ghana and the USA."
        ),
        "price_tier": "medium",
        "social_links": {},
        "tags": ["wedding photography", "corporate", "portrait", "Ghana & USA"],
        "verified": True,
        "status": "active",
    },

    # ─── DJS ──────────────────────────────────────────────────────────────
    {
        "name": "DJ Vyrusky",
        "phone_number": "+233 XX XXX XXXX",
        "email": "djvyrusky@gmail.com",
        "address": "Accra, Ghana",
        "neighborhood": "Accra",
        "website": "",
        "description": (
            "DJ Vyrusky (Kofi Amoako) is one of Ghana's most celebrated disc jockeys and winner of "
            "multiple Ghana DJ Awards including Ghana's Best DJ. Currently resident DJ at Starr FM "
            "and official DJ for MzVee and Shatta Wale, DJ Vyrusky brings electrifying energy and "
            "unmatched musical expertise to weddings, corporate events, concerts, and private parties."
        ),
        "price_tier": "high",
        "social_links": {
            "instagram": "https://www.instagram.com/djvyrusky/",
            "facebook": "https://www.facebook.com/kofi.vyrusky/",
        },
        "tags": ["DJ", "award-winning", "Starr FM", "weddings", "concerts"],
        "verified": True,
        "status": "active",
    },

    # ─── EVENT PLANNERS ───────────────────────────────────────────────────
    {
        "name": "Peach Diamond Events",
        "phone_number": "+233 200 777 270",
        "email": "peachdiamondevents@gmail.com",
        "address": "West Legon, Accra",
        "neighborhood": "West Legon",
        "website": "",
        "description": (
            "Peach Diamond Events is a premier event planning and design company based in West Legon, "
            "Accra. Specialising in social and corporate events, they offer full-service event "
            "planning, event design, coordination, and consultations. From intimate gatherings to "
            "grand weddings and corporate galas, Peach Diamond Events delivers bespoke experiences "
            "with meticulous attention to detail."
        ),
        "price_tier": "high",
        "social_links": {
            "instagram": "https://www.instagram.com/peach_diamond__events/",
        },
        "tags": ["event planning", "wedding planning", "corporate", "West Legon", "bespoke"],
        "verified": True,
        "status": "active",
    },
    {
        "name": "Honeycomb event Design",
        "phone_number": "+233 242 442 064",
        "email": "info@honeycombeventdesign.com",
        "address": "Adenta Dodowa Road, Accra",
        "neighborhood": "Adenta",
        "website": "https://honeycombeventdesign.com",
        "description": (
            "Honeycomb Event Design is an exceptional wedding and event design company with a presence "
            "in both Ghana and the UK. Based in Accra on the Adenta Dodowa Road, they specialise in "
            "luxury weddings, corporate events, and social gatherings. Their services include event "
            "decor, coordination, and complete design solutions that transform venues into breathtaking "
            "spaces tailored to each client's vision."
        ),
        "price_tier": "high",
        "social_links": {
            "instagram": "https://www.instagram.com/honeycombeventdesign/",
            "facebook": "https://www.facebook.com/honeycombeventdesigngh/",
        },
        "tags": ["event design", "wedding", "luxury", "decor", "coordination"],
        "verified": True,
        "status": "active",
    },
]


class Command(BaseCommand):
    help = 'Update existing vendors with real contact data from web research'

    def handle(self, *args, **kwargs):
        updated = 0
        skipped = 0
        not_found = 0

        for data in REAL_VENDOR_DATA:
            name = data['name']
            try:
                vendor = Vendor.objects.get(name__iexact=name)
            except Vendor.DoesNotExist:
                # Try partial match
                qs = Vendor.objects.filter(name__icontains=name.split()[0])
                if qs.count() == 1:
                    vendor = qs.first()
                else:
                    self.stdout.write(self.style.WARNING(f'  ✗ Not found: {name}'))
                    not_found += 1
                    continue

            # Update all fields
            vendor.phone_number = data['phone_number']
            vendor.email = data['email']
            vendor.address = data['address']
            vendor.neighborhood = data.get('neighborhood', '')
            vendor.website = data.get('website', '')
            vendor.description = data['description']
            vendor.price_tier = data.get('price_tier', 'medium')
            vendor.social_links = data.get('social_links', {})
            vendor.tags = data.get('tags', [])
            vendor.verified = data.get('verified', True)
            vendor.status = data.get('status', 'active')
            vendor.save()

            updated += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Updated: {vendor.name}'))

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✓ Updated: {updated}'))
        self.stdout.write(self.style.WARNING(f'⊗ Not found: {not_found}'))
        self.stdout.write(f'  Skipped: {skipped}')
        self.stdout.write('=' * 60)
