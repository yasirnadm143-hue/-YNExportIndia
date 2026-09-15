from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import Brand


BRANDS = [

    # =========================
    # MOBILE / ELECTRONICS
    # =========================
    "Samsung",
    "Apple",
    "OnePlus",
    "Xiaomi",
    "Redmi",
    "POCO",
    "realme",
    "iQOO",
    "Motorola",
    "Google",
    "Nokia",
    "OPPO",
    "vivo",
    "Nothing",
    "ASUS",
    "Lenovo",
    "Dell",
    "HP",
    "Acer",
    "MSI",
    "LG",
    "Sony",
    "TCL",
    "Haier",
    "Hisense",
    "Panasonic",
    "Philips",
    "boAt",
    "Noise",
    "Fire-Boltt",
    "JBL",
    "Bose",
    "Sennheiser",
    "Marshall",
    "Zebronics",
    "Portronics",
    "Anker",
    "TP-Link",
    "D-Link",
    "Canon",
    "Nikon",
    "GoPro",
    "DJI",

    # =========================
    # FASHION - INDIAN
    # =========================
    "Manyavar",
    "Max Fashion",
    "Biba",
    "W",
    "Libas",
    "Fabindia",
    "Raymond",
    "Peter England",
    "Louis Philippe",
    "Van Heusen",
    "Allen Solly",
    "Park Avenue",
    "Flying Machine",
    "Mufti",
    "Spykar",
    "Being Human",
    "Rare Rabbit",
    "Snitch",
    "Bewakoof",
    "Campus Sutra",
    "The Souled Store",
    "Jockey",
    "Dollar",
    "Lux",
    "VIP",
    "Skybags",
    "Safari",
    "Wildcraft",
    "American Tourister",

    # =========================
    # FASHION - INTERNATIONAL
    # =========================
    "Nike",
    "Adidas",
    "Puma",
    "Reebok",
    "Skechers",
    "Levi's",
    "Wrangler",
    "Lee",
    "U.S. Polo Assn.",
    "Tommy Hilfiger",
    "Calvin Klein",
    "GAP",
    "H&M",
    "Zara",
    "Marks & Spencer",
    "Crocs",
    "Converse",
    "Vans",
    "Under Armour",

    # =========================
    # WATCHES
    # =========================
    "Titan",
    "Fastrack",
    "Sonata",
    "Noise",
    "Fire-Boltt",
    "boAt",
    "Casio",
    "Fossil",
    "Timex",
    "Daniel Wellington",
    "Michael Kors",
    "Armani Exchange",
    "Emporio Armani",
    "Tommy Hilfiger Watches",

    # =========================
    # BEAUTY / MAKEUP
    # =========================
    "Lakme",
    "Maybelline New York",
    "L'Oreal Paris",
    "L'Oreal",
    "Revlon",
    "MAC",
    "Colorbar",
    "Swiss Beauty",
    "Mamaearth",
    "The Derma Co",
    "Dot & Key",
    "Minimalist",
    "Plum",
    "WOW Skin Science",
    "Biotique",
    "Lotus Herbals",
    "Himalaya",
    "Pond's",
    "Nivea",
    "Dove",
    "Vaseline",
    "Garnier",
    "Neutrogena",
    "Cetaphil",
    "CeraVe",
    "Avene",
    "The Ordinary",
    "Forest Essentials",
    "Kama Ayurveda",
    "Nykaa Cosmetics",
    "MARS Cosmetics",
    "Faces Canada",
    "Insight Cosmetics",
    "Sugar Cosmetics",
    "Kay Beauty",
    "Bella Vita",
    "WOW",
    "Pilgrim",
    "Earth Rhythm",

    # =========================
    # PERSONAL CARE
    # =========================
    "Colgate",
    "Closeup",
    "Sensodyne",
    "Pepsodent",
    "Oral-B",
    "Gillette",
    "Park Avenue",
    "Nivea Men",
    "Old Spice",
    "Wild Stone",
    "Denver",
    "Set Wet",
    "Beardo",
    "Bombay Shaving Company",
    "Ustraa",
    "The Man Company",

    # =========================
    # HOME / KITCHEN
    # =========================
    "Prestige",
    "Pigeon",
    "Butterfly",
    "Hawkins",
    "Bajaj",
    "Havells",
    "Crompton",
    "Usha",
    "Borosil",
    "Cello",
    "Milton",
    "Tupperware",
    "Wonderchef",
    "Wonderchef",
    "Philips",
    "Morphy Richards",
    "AGARO",
    "Kent",
    "Eureka Forbes",
    "Dyson",
    "V-Guard",
    "Orient Electric",
    "Atomberg",
    "Ola Electric",

    # =========================
    # FURNITURE / HOME
    # =========================
    "Godrej",
    "Godrej Interio",
    "Nilkamal",
    "Sleepwell",
    "Wakefit",
    "The Sleep Company",
    "Pepperfry",
    "Urban Ladder",
    "WoodenStreet",
    "IKEA",
    "Home Centre",
    "Durian",

    # =========================
    # GROCERY / FMCG
    # =========================
    "Tata",
    "Tata Sampann",
    "Aashirvaad",
    "Fortune",
    "India Gate",
    "Daawat",
    "Patanjali",
    "Dabur",
    "Himalaya",
    "Parle",
    "Britannia",
    "Sunfeast",
    "ITC",
    "Nestle",
    "Maggi",
    "Cadbury",
    "Mondelez",
    "Amul",
    "Mother Dairy",
    "Surf Excel",
    "Ariel",
    "Tide",
    "Vim",
    "Harpic",
    "Lizol",
    "Dettol",
    "Reckitt",
    "HUL",
    "Coca-Cola",
    "Pepsi",
    "Thums Up",
    "Sprite",
    "Fanta",
    "Red Bull",
    "Monster",

    # =========================
    # FOOTWEAR
    # =========================
    "Bata",
    "Relaxo",
    "Sparx",
    "Liberty",
    "Paragon",
    "Action",
    "Campus",
    "Red Tape",
    "Woodland",
    "Metro",
    "Mochi",
    "Crocs",
    "Adidas",
    "Nike",
    "Puma",
    "Skechers",

    # =========================
    # JEWELLERY / ACCESSORIES
    # =========================
    "Tanishq",
    "Kalyan Jewellers",
    "Malabar Gold & Diamonds",
    "Senco Gold",
    "CaratLane",
    "Mia by Tanishq",
    "GIVA",
    "Sukkhi",
    "Zaveri Pearls",
    "Yellow Chimes",
    "Rubans",
    "Voylla",

    # =========================
    # BABY / KIDS
    # =========================
    "Pampers",
    "Huggies",
    "MamyPoko",
    "Johnson's Baby",
    "Himalaya Baby",
    "Mamaearth Baby",
    "Mee Mee",
    "Mothercare",
    "FirstCry",

    # =========================
    # SPORTS / FITNESS
    # =========================
    "Decathlon",
    "Yonex",
    "Cosco",
    "Nivia",
    "Vector X",
    "Strauss",
    "HRX",
    "Cultsport",
    "Adidas",
    "Nike",
    "Puma",

    # =========================
    # AUTOMOTIVE
    # =========================
    "Castrol",
    "Motul",
    "Mobil",
    "Shell",
    "Bosch",
    "Mann-Filter",
    "Exide",
    "Amaron",
    "MRF",
    "CEAT",
    "Apollo Tyres",
    "JK Tyre",
    "Michelin",

    # =========================
    # COMPUTER / ACCESSORIES
    # =========================
    "Logitech",
    "Razer",
    "Corsair",
    "Kingston",
    "SanDisk",
    "Western Digital",
    "Seagate",
    "Transcend",
    "Rapoo",
    "Redragon",
    "HyperX",
    "SteelSeries",
]


class Command(BaseCommand):
    help = "Seed major Indian-market brands into the Brand table"

    def handle(self, *args, **options):
        created = 0
        existing = 0

        # Remove duplicate names from this seed list
        unique_brands = []
        seen = set()

        for name in BRANDS:
            key = name.strip().lower()
            if key and key not in seen:
                seen.add(key)
                unique_brands.append(name.strip())

        for name in unique_brands:
            slug = slugify(name)

            brand = Brand.objects.filter(name__iexact=name).first()

            if brand:
                existing += 1
                continue

            Brand.objects.create(
                name=name,
                slug=slug,
                is_active=True,
            )
            created += 1

        self.stdout.write("")
        self.stdout.write("====================================")
        self.stdout.write("       BRAND DATABASE SETUP")
        self.stdout.write("====================================")
        self.stdout.write(f"Seed list: {len(unique_brands)}")
        self.stdout.write(f"New brands: {created}")
        self.stdout.write(f"Already existed: {existing}")
        self.stdout.write(f"Total brands in DB: {Brand.objects.count()}")
        self.stdout.write("====================================")
