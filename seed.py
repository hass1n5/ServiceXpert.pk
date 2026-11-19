"""Create the database and fill it with the real service catalogue.

    python seed.py            # only seeds an empty database
    python seed.py --reset    # wipes sparkle.db and starts fresh
"""

import random
import sys
from datetime import datetime, timedelta, timezone

from app import DEFAULT_SETTINGS, create_app
from extensions import db
from models import Booking, Category, Service, Setting, Testimonial, User, slugify

CLEANING = [
    (
        "House Cleaning",
        "Poore ghar ki deep cleaning — kitchen, bedrooms, lounge aur balcony.",
        "Ghar ki har manzil, har kamra. Hamari team furniture ke neeche, "
        "fans, exhausts, switchboards aur skirting tak jati hai — wo jagahein "
        "jo rozana ki safai mein reh jati hain. Shifting se pehle ya baad mein, "
        "ya Eid se pehle ki mukammal safai ke liye sab se zyada book hone wali service.",
        "Kitchen cabinets andar bahar se\nBathroom deep scrub aur descaling\n"
        "Fans, lights aur exhaust cleaning\nWindows, grills aur sills\n"
        "Floor scrubbing aur mopping\nFurniture dusting aur polish",
        6500, 8500, "4–6 ghante", "home", True,
    ),
    (
        "Office Cleaning",
        "Workstations, meeting rooms aur common areas ki professional safai.",
        "Office ki safai kaam ke auqat ke baad ya weekend par, taake staff ka "
        "din zaya na ho. Workstations, keyboards, chairs, glass partitions, "
        "pantry aur washrooms — sab covered. Monthly contract par rate kam ho jata hai.",
        "Workstation aur desk sanitising\nGlass partitions aur doors\n"
        "Pantry aur kitchenette\nWashroom deep clean\nCarpet vacuum\n"
        "Dustbin clearance",
        9500, 12000, "5–8 ghante", "office", True,
    ),
    (
        "Water Tank Cleaning",
        "Underground aur overhead tanks ki dewatering, scrubbing aur disinfection.",
        "Tank mein jami silt, kai (algae) aur bacteria paani ko kharab kar dete "
        "hain. Hum tank khali karte hain, deewaron aur farsh ko mechanically "
        "scrub karte hain, phir food-grade disinfectant se treat karte hain. "
        "Saal mein do dafa karwana behtareen hai.",
        "Tank dewatering\nSilt aur sludge removal\nHigh-pressure wall scrubbing\n"
        "Food-grade disinfection\nFinal rinse aur refill\nBefore/after pictures",
        4500, 6000, "2–3 ghante", "drop", True,
    ),
    (
        "Carpet Cleaning",
        "Rugs, carpets aur sofas ki shampoo aur hot-water extraction.",
        "Carpet ke reshon mein dhool, mitti aur dust mites baith jate hain. "
        "Hum pehle deep vacuum karte hain, phir carpet shampoo aur hot water "
        "extraction se andar tak safai karte hain. Sukhne mein 4–6 ghante lagte hain.",
        "Deep vacuum\nStain pre-treatment\nCarpet shampoo\n"
        "Hot water extraction\nDeodorising\nSofa aur cushions (optional)",
        3500, 4500, "2–4 ghante", "sparkle", True,
    ),
    (
        "Washroom Cleaning",
        "Tiles, commode, basin aur fittings ki descaling aur sanitisation.",
        "Paani ke daagh, calcium deposits aur peeli tiles — washroom sab se "
        "pehle ganda dikhta hai. Hospital-grade disinfectant aur acid-free "
        "descalers se hum tiles, grout, commode, shower aur fittings ko nayi "
        "halat mein le aate hain.",
        "Tile aur grout scrubbing\nCommode deep sanitisation\n"
        "Basin aur mirror polish\nShower aur taps descaling\n"
        "Drain cleaning\nOdour treatment",
        2500, 3200, "1–2 ghante", "drop", False,
    ),
    (
        "Restaurant Cleaning",
        "Kitchen, exhaust hood aur dining area ki hygiene cleaning.",
        "Food business mein safai sirf shakal ka masla nahi — licence ka masla "
        "hai. Hum kitchen ki degreasing, exhaust hood aur duct cleaning, cold "
        "storage, dining area aur washrooms sab cover karte hain. Kaam band "
        "hone ke baad raat ko bhi ho sakta hai.",
        "Kitchen degreasing\nExhaust hood aur duct\nBurners aur griddles\n"
        "Cold storage cleaning\nDining area aur seating\nFloor scrubbing",
        15000, 18000, "6–10 ghante", "office", False,
    ),
    (
        "Commercial Cleaning",
        "Showrooms, banks, schools aur factories ke liye contract cleaning.",
        "Bari jagahon ke liye planned cleaning — roz, haftawar ya mahana "
        "schedule par. Team, supervisor aur machinery hamari, aap sirf schedule "
        "batayein. Ride-on scrubbers aur high-rise glass cleaning bhi available hai.",
        "Daily ya weekly contract\nRide-on floor scrubbing\n"
        "High-rise glass cleaning\nWashroom upkeep\nWaste management\n"
        "Supervisor aur reporting",
        25000, 30000, "Contract par", "office", False,
    ),
    (
        "Blind Cleaning",
        "Vertical, roller aur wooden blinds ki on-site ya off-site cleaning.",
        "Blinds par jami dhool allergy ka sab se bara sabab hoti hai. Halke "
        "ganday blinds on-site ultrasonic method se saaf ho jate hain; zyada "
        "ganday blinds utar kar workshop le jaate hain aur dho kar wapas "
        "install karte hain.",
        "On-site dusting aur wash\nUltrasonic deep clean (off-site)\n"
        "Stain treatment\nTrack aur mechanism cleaning\n"
        "Re-installation\nFabric-safe chemicals",
        2800, 3500, "1–3 ghante", "sparkle", False,
    ),
]

PEST = [
    (
        "General Fumigation",
        "Poore ghar ya office ki mukammal fumigation, har qism ke keeray ke liye.",
        "Ek hi treatment mein cockroach, makhi, machhar, chiunti aur spiders — "
        "sab par kaam. Odourless aur family-safe chemicals istemal hote hain, "
        "is liye treatment ke 2–3 ghante baad ghar wapas istemal kiya ja sakta hai. "
        "Har service 30 din ki warranty ke sath aati hai.",
        "Poore ghar ki spray\nCorners, cracks aur drains\n"
        "Odourless family-safe chemical\n30 din ki warranty\n"
        "Free follow-up visit\nPets ke liye mehfooz options",
        3500, 4500, "1–2 ghante", "shield", True,
    ),
    (
        "Cockroach Treatment",
        "Gel baiting aur residual spray se lal aur German cockroach ka khatma.",
        "Cockroach sirf ganda nahi karta, khane ko zehreela bhi banata hai. "
        "Hum gel baiting (kitchen ke liye, bina bo ke) aur residual spray ka "
        "combination use karte hain, jo nests aur ande dono tak pohnchta hai. "
        "Do hafte baad free follow-up.",
        "Gel baiting kitchen mein\nResidual spray har jagah\n"
        "Drain aur manhole treatment\nEgg-cycle follow-up\n"
        "45 din ki warranty\nKhane ke bartan cover karne ki zarurat nahi",
        3000, 4000, "1 ghanta", "bug", True,
    ),
    (
        "Bed Bugs Treatment",
        "Mattress, beds aur furniture se khatmal ka mukammal safaya.",
        "Khatmal (bed bugs) gaddon ki silwaton, bed frames aur sofa ki darzon "
        "mein chhupte hain. Hum heat-assisted treatment aur targeted spray se "
        "andon samet khatma karte hain. Pehli visit ke 14 din baad dusri visit "
        "lazmi hoti hai — wo included hai.",
        "Mattress aur bed frame treatment\nSofa aur cushions\n"
        "Skirting aur furniture joints\n14 din baad free 2nd visit\n"
        "60 din ki warranty\nChaadar dhone ki guidance",
        6000, 7500, "2–3 ghante", "bug", True,
    ),
    (
        "Termite Treatment",
        "Deemak ke liye pre-construction aur post-construction treatment.",
        "Deemak lakri, darwazon aur almari ko andar hi andar khokhla kar deti "
        "hai. Free survey ke baad hum drill-fill-seal method se deewaron aur "
        "farsh mein chemical barrier banate hain. Construction se pehle wali "
        "soil treatment bhi karte hain.",
        "Free survey aur inspection\nDrill, fill aur seal method\n"
        "Soil barrier treatment\nWooden fixtures treatment\n"
        "5 saal tak warranty plans\nWritten report",
        12000, 15000, "3–5 ghante", "shield", True,
    ),
    (
        "Dengue Spray",
        "Machhar aur dengue larva ke liye fogging aur breeding-site treatment.",
        "Dengue machhar saaf khare paani mein anda deta hai — tanks, gamlay, "
        "coolers, chhat par para saman. Hum breeding spots khatam karte hain, "
        "phir thermal fogging aur residual spray karte hain. Barish ke mausam "
        "mein har 3 hafte repeat karwana behtar hai.",
        "Breeding site survey\nLarvicide treatment\nThermal fogging\n"
        "Lawn aur boundary spray\nWHO-approved chemicals\n21 din ki warranty",
        4000, 5000, "1–2 ghante", "spray", True,
    ),
    (
        "Disinfection Services",
        "Virus aur bacteria ke khilaf ULV fogging aur surface sanitisation.",
        "Schools, clinics, offices aur gharon ke liye hospital-grade "
        "disinfection. ULV fogging hawa mein mojood zarrat tak pohnchti hai, "
        "jab ke door handles, switches aur railings jaise high-touch points "
        "alag se wipe kiye jate hain. Certificate bhi issue hota hai.",
        "ULV cold fogging\nHigh-touch point wiping\n"
        "Hospital-grade disinfectant\nNon-toxic, residue-free\n"
        "Same-day service\nDisinfection certificate",
        5000, 6500, "1–2 ghante", "spray", False,
    ),
]

REVIEWS = [
    ("Ayesha Siddiqui", "Lahore", "House Cleaning", 5,
     "Shifting se pehle poore ghar ki cleaning karwai. Team waqt par aayi aur "
     "kitchen cabinets andar se bhi saaf kiye. Rate bhi munasib tha."),
    ("Hamza Tariq", "Karachi", "Cockroach Treatment", 5,
     "Kitchen mein cockroach ka bohat masla tha. Gel treatment ke teen din "
     "baad hi farq nazar aana shuru ho gaya. Follow-up visit bhi free thi."),
    ("Nimra Khan", "Islamabad", "Water Tank Cleaning", 4,
     "Underground tank saalon baad saaf karwaya. Before-after tasveerein "
     "bhejin jo dekh kar andaza hua kitni mitti thi."),
    ("Bilal Ahmed", "Faisalabad", "Termite Treatment", 5,
     "Deemak ne almari kharab kar di thi. Survey free tha aur pandrah mahine "
     "guzar gaye hain, dobara koi nishan nahi mila."),
    ("Sana Yousaf", "Multan", "Dengue Spray", 5,
     "Barish ke baad lawn mein machhar bohat ho gaye the. Fogging ke baad "
     "shaam ko bahar baithna mumkin ho gaya."),
    ("Usman Ghani", "Jhang", "Office Cleaning", 5,
     "Hamare office ka monthly contract inke sath hai. Staff tameez wala hai "
     "aur kaam chhutti ke baad karte hain, is liye koi disturbance nahi hoti."),
]

CITIES = ["Lahore", "Karachi", "Islamabad", "Rawalpindi", "Faisalabad",
          "Multan", "Jhang", "Gujranwala", "Sialkot", "Peshawar"]

NAMES = ["Ali Raza", "Fatima Noor", "Zain Abbas", "Mahnoor Raza", "Danish Iqbal",
         "Rabia Aslam", "Talha Mehmood", "Iqra Shahid", "Hassan Javed",
         "Komal Bashir", "Owais Anjum", "Sadia Kamran"]


def seed(reset=False):
    app = create_app()

    with app.app_context():
        if reset:
            db.drop_all()
            print("Purana data hata diya.")

        db.create_all()

        if db.session.scalar(db.select(db.func.count(User.id))):
            print("Database mein data pehle se hai. --reset use karein fresh start ke liye.")
            return

        random.seed(11)

        admin = User(name="Site Admin", email="admin@servicexpert.pk",
                     phone="0300-1234567", city="Lahore", role="admin")
        admin.set_password("admin1234")

        client = User(name="Ayesha Siddiqui", email="client@servicexpert.pk",
                      phone="0321-9087341", city="Lahore",
                      address="House 42, Block C, Johar Town", role="client")
        client.set_password("client1234")

        db.session.add_all([admin, client])

        cleaning = Category(
            name="Deep Cleaning Services",
            slug="deep-cleaning-services",
            tagline="Ghar, office aur commercial jagahon ki mukammal safai",
            description="Trained staff, professional machinery aur eco-friendly "
                        "chemicals ke sath har qism ki deep cleaning.",
            accent="green",
            sort_order=1,
        )
        pest = Category(
            name="Pest Control Services",
            slug="pest-control-services",
            tagline="Keeray, deemak aur machharon ka mehfooz aur mukammal khatma",
            description="Government-approved chemicals aur licensed operators — "
                        "warranty ke sath fumigation aur pest control.",
            accent="blue",
            sort_order=2,
        )
        db.session.add_all([cleaning, pest])
        db.session.flush()

        services = []
        for group, category in ((CLEANING, cleaning), (PEST, pest)):
            for order, row in enumerate(group, start=1):
                name, summary, description, includes, price, old, duration, icon, featured = row
                service = Service(
                    category_id=category.id,
                    name=name,
                    slug=slugify(name),
                    summary=summary,
                    description=description,
                    includes=includes,
                    price_from=price,
                    old_price=old,
                    duration=duration,
                    icon=icon,
                    rating=round(random.uniform(4.5, 5.0), 1),
                    is_featured=featured,
                    is_active=True,
                    sort_order=order,
                )
                services.append(service)
        db.session.add_all(services)
        db.session.flush()

        now = datetime.now(timezone.utc)
        statuses = ["new"] * 4 + ["contacted"] * 3 + ["scheduled"] * 3 + \
                   ["completed"] * 8 + ["cancelled"]

        used = set()
        for i in range(34):
            ref = f"BK-{random.randint(100000, 999999)}"
            while ref in used:
                ref = f"BK-{random.randint(100000, 999999)}"
            used.add(ref)

            service = random.choice(services)
            status = random.choice(statuses)
            db.session.add(
                Booking(
                    reference=ref,
                    name=random.choice(NAMES),
                    phone=f"03{random.randint(10, 49)}-{random.randint(1000000, 9999999)}",
                    email=None if random.random() < 0.4 else "customer@example.com",
                    city=random.choice(CITIES),
                    address=f"House {random.randint(1, 400)}, Block {random.choice('ABCDE')}",
                    preferred_date=(now + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
                    message=random.choice([
                        "Weekend par ho sakta hai?",
                        "Do bedrooms aur ek lounge hai.",
                        "Jaldi chahiye, mehmaan aa rahe hain.",
                        None, None,
                    ]),
                    service_id=service.id,
                    user_id=client.id if random.random() < 0.25 else None,
                    status=status,
                    quoted_price=service.price_from if status == "completed" else None,
                    created_at=now - timedelta(days=random.randint(0, 13),
                                               hours=random.randint(0, 23)),
                )
            )

        for name, city, service_name, rating, text in REVIEWS:
            db.session.add(
                Testimonial(name=name, city=city, service=service_name,
                            rating=rating, body=text, is_published=True)
            )

        for key, value in DEFAULT_SETTINGS.items():
            Setting.put(key, value)

        db.session.commit()

        print("Sab data taiyar hai.")
        print(f"  Services : {len(services)}")
        print("  Admin    ->  admin@servicexpert.pk  /  admin1234   (/admin/login)")
        print("  Client   ->  client@servicexpert.pk    /  client1234  (/login)")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
