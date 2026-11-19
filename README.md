# ServiceXpert.pk — Cleaning & Pest Control Website

Poori website: public site (Home, About Us, Services, Contact Us + har
service ka apna page), client login/register/dashboard, aur admin panel
(bookings, services, clients, reviews, logo/favicon upload, WhatsApp settings).

Rang aur font admin se badalte hain — **12 themes** aur **138 Google Fonts**
(Urdu/Arabic fonts samet), bina koi code chhoo'e. WhatsApp par booking bhejne
ke liye forms ke sath poora **chat widget** bhi hai.

Backend: **Python (Flask)**. Database: **SQLite** (koi extra setup nahi
chahiye — ek file mein sab data save hota hai).

---

## 1. Setup (pehli baar)

Terminal / Command Prompt mein project folder ke andar jaa kar:

```bash
# 1. Python packages install karein
pip install -r requirements.txt

# 2. Database banayein aur demo data (14 services, bookings, reviews) daalein
python seed.py --reset

# 3. Server chalayein
python app.py
```

Ab browser mein kholein: **http://127.0.0.1:5000**

> Agar `pip` kaam na kare to `pip3` try karein. Agar `python` kaam na kare
> to `python3` try karein — yeh Windows vs Mac/Linux ka farq hota hai.

---

## 2. Demo logins

| Kis ke liye | Email | Password | Kahan se login karein |
|---|---|---|---|
| **Admin (aap)** | `admin@sparklecare.pk` | `admin1234` | `/admin/login` |
| Client (customer) | `client@example.com` | `client1234` | `/login` |

Admin login link website ke footer mein aur upar ki utility bar mein
"Admin" likha hua milega. Isay customers se chhupa kar rakhein — agar
chahein to yeh URL kisi aur (jaise `/panel-login`) mein badla ja sakta hai
(`auth.py` mein).

---

## 3. Sab se pehle yeh karein: apni company ki tafseelat daalein

1. Admin panel kholein → **Site settings**
2. Yahan se badlein:
   - **Logo aur Favicon** — apni company ka logo upload karein (png/jpg/svg)
   - **WhatsApp number** — jahan customer ki bookings aani chahiye
     (jaise `03001234567`)
   - Phone, email, pata, kaam ke auqat
   - Facebook / Instagram links
   - Home page ka hero title aur text
   - About Us ka content
   - Google Map embed code (Google Maps → Share → Embed a map → code
     copy karein)
   - **Rang aur font** — 12 themes aur 138 fonts (neeche section 4 dekhein)
   - **WhatsApp chat widget** — on/off, naam, greeting message
   - Hero ke neeche ke numbers (rating, jobs, staff, warranty)
3. **"Tamam settings save karein"** dabayein

Website turant update ho jayegi — refresh kar ke dekhein.

---

## 4. Rang aur font badalna

Admin panel → **Site settings** → *Rang aur font*

**12 themes** — Emerald & Gold (default), Ocean Blue, Royal Purple, Sunset
Orange, Crimson Red, Teal & Coral, Midnight Navy, Forest & Lime, Rose Pink,
Amber & Earth, Slate Corporate, Fresh Aqua.

Theme sirf ek rang nahi badalti — poori website, admin panel, login pages,
favicon aur mobile browser ka color, sab ek sath badal jate hain. Kisi bhi
card par click karein aur save dabayein.

**138 fonts** — Google Fonts ki poori list, 6 groups mein bant kar:

| Group | Kis kaam ke liye |
|---|---|
| Sans serif | Aam istemal, sab se ziada parhne mein aasan |
| Display / headline | Sirf badi headings ke liye (Bebas Neue, Anton, Oswald) |
| Serif | Classic aur sanjeeda look (Playfair Display, Merriweather) |
| Handwriting | Logo jaisa andaz (Pacifico, Caveat) |
| Monospace | Technical look |
| **Urdu / Arabic** | Noto Nastaliq Urdu, Gulzar, Amiri, Cairo, Jameel-style |

Heading aur body text ke liye alag-alag font chun sakte hain. Select karte
hi neeche **preview** mein asli font nazar aa jata hai — save se pehle.

> Mashwara: heading ke liye koi mazboot font (Outfit, Montserrat, Playfair
> Display) aur body ke liye koi saada font (Inter, Open Sans) — dono ek jaisa
> mat rakhein.

---

## 5. WhatsApp chat widget + Sparkle Bot (free, no API key)

Website ke neeche daayein kone mein sabz WhatsApp button hai. Click karne par
poora chat box khulta hai:

- Aapka logo, business ka naam aur "typing…" ka andaz
- Greeting message (settings se badalta hai)
- Services ke **quick reply buttons** — click karte hi message likha jata hai
- Customer apna naam aur message likh kar bhejta hai

Ab jab customer koi message bhejta hai, sabse pehle **Sparkle Bot** khud
jawab deta hai — koi OpenAI/Anthropic API key ya monthly cost nahi lagti,
sab kuch website ke apne data (services, price, timing, address) se seedha
jawab deta hai. Ye samajh sakta hai:

- Kisi **service ka naam** ("carpet cleaning ka rate?") → price, waqt aur
  tafseel
- **Category** ka naam ("pest control services kya hain?") → us category ki
  services list
- **Rate/price**, **auqat-e-kaar**, **address/location** ke general sawal
- **Salam/greeting**, **shukriya**, aur "booking karni hai" jaise iraday
- Jo sawal samajh na aaye, uspar maazrat kar ke seedha WhatsApp handoff
  offer karta hai

Bot ke jawab ke sath ek chhota button bhi milta hai — *"Team ko WhatsApp par
bhejein"* — jis se customer chahe to wahi baat seedha aapki business
WhatsApp par bhi forward kar sakta hai. Bot kabhi customer ko atka hua nahi
chhorta: jahan uska jawab kaam na aaye, wahan hamesha insaan tak rasai ka
raasta deta hai.

Code: `static/js/chatbot.js` (matching engine — service/keyword se jawab
banata hai) + `static/js/site.js` (widget ki UI, bubbles dikhana). Data
`app.py` se har page par `bot_catalog` ke through JSON mein widget tak
pohonchta hai, is liye Settings/Services mein koi tabdeeli turant bot ke
jawabon mein bhi nazar aati hai.

**Note:** pehle wale version mein "hi" jaisa lafz kisi bhi lambe lafz ke
andar (jaise Urdu ka "**bhi**") match ho kar ghalat greeting trigger kar
deta tha. Ab matching sirf poore, alag lafz par hoti hai — "bhi", "yahi",
"sahi" waghera par bot ghalati se greeting nahi bolega.

Settings → *WhatsApp chat widget* se: widget on/off, chat mein naam, uske
neeche ka text, jawab ka waqt, aur pehla message badal sakte hain.

---

## 6. Services manage karna

Admin panel → **Services**

- Do categories pehle se maujood hain: *Deep Cleaning Services* aur
  *Pest Control Services*. Naya category "Category" button se bana sakte
  hain.
- Har service mein: naam, qeemat, purani qeemat (discount dikhane ke
  liye), tasveer, "kya shamil hai" ki list, aur poori tafseel add kar
  sakte hain.
- **Live** checkbox off karne se service website se hat jati hai (delete
  nahi hoti — data mehfooz rehta hai).
- **Featured** checkbox on karne se woh service home page par nazar aati
  hai.
- Har service ka apna page khud ban jata hai:
  `yourwebsite.com/house-cleaning`, `yourwebsite.com/general-fumigation`
  waghera.

**Nayi service tezi se banane ke liye:**

- Upar **search box** hai — naam ya slug likhein, list foran filter ho jati
  hai. Keyboard par `/` dabane se search par cursor aa jata hai.
- Har service ke aage **copy button** hai. Copy banti hai purani service ki
  saari tafseel ke sath, lekin *off* rehti hai — aap naam aur qeemat badal
  kar Live kar dein. "Water Tank Cleaning" se "Underground Tank Cleaning"
  banane mein 30 second lagte hain.

---

## 7. Bookings (customer requests)

Jab koi customer website ke kisi bhi form se booking bhejta hai:

1. Request database mein save ho jati hai
2. Customer ka WhatsApp khud khul jata hai, poora message pehle se likha
   hua (reference number, service, naam, phone, pata)
3. Admin panel → **Bookings** mein woh request turant nazar aati hai

Bookings page se aap:
- Status badal sakte hain (Nayi → Contacted → Scheduled → Completed)
- Quote price aur internal note likh sakte hain
- Customer ko seedha WhatsApp bhej sakte hain (green button)
- Poori request apni team ko forward kar sakte hain

---

## 8. Clients

Jo customers website par khud account banate hain (`/register` se), unki
list **Admin → Clients** mein nazar aati hai. Unhe band/chaalu kar sakte
hain.

---

## 9. Reviews

**Admin → Reviews** se customer reviews add/edit karein. "Website par
dikhayein" checkbox se control hota hai ke review home page par live hai
ya nahi.

---

## 10. Project files (agar developer se kaam karwana ho)

```
sparkle/
├── app.py              → Main application (yahan se run hota hai)
├── config.py            → Settings (database path, upload size limit)
├── models.py             → Database tables (Service, Booking, User, ...)
├── extensions.py          → Database aur login setup
├── security.py            → CSRF protection, file upload safety
├── messaging.py            → WhatsApp link banane ka logic
├── theming.py               → 12 themes aur 138 fonts ka catalogue
├── auth.py                 → Login/register/logout
├── client.py                → Client dashboard
├── admin.py                  → Admin panel pages
├── api.py                     → Admin ke liye JSON API (AJAX calls)
├── public_site.py              → Public website ke saare pages
├── seed.py                      → Demo data banane wali script
├── requirements.txt              → Python packages ki list
├── templates/                     → HTML files (Jinja2)
│   ├── public/                     → Home, About, Services, Contact
│   ├── auth/                        → Login/register pages
│   ├── client/                       → Client dashboard
│   └── admin/                         → Admin panel pages
└── static/
    ├── css/                           → Stylesheets
    ├── js/                             → JavaScript
    └── uploads/                         → Logo, favicon, service images
```

---

## 11. Live server par daalne ke liye (deployment)

Yeh development server hai (`python app.py`), jo sirf testing ke liye
theek hai. Asal website ke liye:

1. Kisi hosting par (jaise a2 hosting, DigitalOcean, PythonAnywhere)
   Python 3.11+ chahiye
2. `SECRET_KEY` environment variable set karein (random, lambi string)
3. Production server jaise **gunicorn** istemal karein:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
4. Iske aage Nginx laga kar HTTPS (SSL) lagayein
5. `config.py` mein `SESSION_COOKIE_SECURE=1` environment variable set
   karein jab HTTPS chal raha ho

Is qadam ke liye kisi developer ki madad lena behtar rahega.

---

## 12. Is dafa kya check hua, aur kya khud dekhna hai

Is sandbox mein internet band hai, is liye yahan `pip install` nahi ho saka
aur app ko asal browser mein chala kar nahi dekha gaya. Iske bajaye:

- Har `.py` file compile ki gayi (syntax errors ke liye) — sab pass.
- Har `.js` file `node --check` se guzari — sab pass.
- Har `.html` template Jinja2 se parse ki gayi (24 templates) — sab pass,
  aur home/about ke naye number-formatting wale hisse asli data ke sath
  render kar ke bhi dekhe gaye.
- Har jagah jahan icon (`ui.icon(...)`) istemal hota hai (~100 jagah) us
  ke parent CSS class ko dhoond kar confirm kiya ke icon ka size CSS mein
  set hai — 3 jagah (utility bar ka ghari wala icon, admin sidebar ka
  logout button, Settings ke Logo/Favicon labels) size missing thi, theek
  kar di gayi hai, aur ek global safety-net rule bhi daal di hai taake
  aage koi naya icon spot bhool jaye to woh sirf "thora ghalat size" ho.
- Home page ke stat numbers (rating/jobs/staff) pehle sirf JavaScript se
  bharte thay — agar JS slow ya fail ho jata to visitor ko hamesha "0"
  dikhta. Ab asal value seedhi HTML mein aati hai, JS sirf usse animate
  karta hai.
- About page ke stats pehle hardcoded thay (4.8/5, 8,800+, 120+) — ab
  Site settings ki wahi values istemal karte hain jo home page karta hai,
  taake dono pages hamesha match karein.

**Aap khud jo check karein** (kyunke asal browser is sandbox mein nahi
hai): koi bhi service ka page (jaise `/house-cleaning`) khol kar dekh
lein ke price/booking card sidebar mein sahi jagah scroll ke sath chipak
raha hai (`position: sticky` — modern browsers mein kaam karta hai, lekin
yahan test nahi ho saka). Mobile width par bhi ek nazar daal lein.

