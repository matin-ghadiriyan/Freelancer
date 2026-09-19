# 💼 فریلنسرینو (Freelancino)

پلتفرم حرفه‌ای فریلنسری برای اتصال کارفرمایان و فریلنسرهای متخصص. ساخته‌شده با **Flask** و معماری **Application Factory** و **Blueprint**.

---

## ✨ ویژگی‌ها

- **احراز هویت مبتنی بر Session** — ثبت‌نام، ورود، خروج و مدیریت پروفایل
- **مدیریت پروژه‌ها** — ثبت، فیلتر، جستجو و مشاهده جزئیات
- **سیستم پیشنهاد (Proposal)** — ارسال، پذیرش و رد پیشنهادها
- **دایرکتوری فریلنسرها** — جستجو بر اساس مهارت و وضعیت
- **نظرات و امتیازدهی** — ثبت نظر ۱ تا ۵ ستاره
- **پنل مدیریت** — مدیریت کاربران، پروژه‌ها، دسته‌بندی‌ها، مهارت‌ها و نظرات
- **REST API** — اندپوینت‌های JSON برای پروژه‌ها، فریلنسرها، آمار و ...
- **محدودیت نرخ درخواست (Rate Limiting)** — جلوگیری از سوءاستفاده
- **CSRF Protection** — محافظت از فرم‌ها با Flask-WTF
- **رابط کاربری حرفه‌ای و راست‌چین (RTL)** — طراحی مدرن و واکنش‌گرا
- **صفحات خطای سفارشی** — ۴۰۰، ۴۰۳، ۴۰۴، ۴۲۹ و ۵۰۰

---

## 🧱 معماری پروژه

```
Freelancer/
├── config.py                 # تنظیمات (Development / Production)
├── run.py                    # نقطه ورود برنامه
├── README.md
├── .env                      # متغیرهای محیطی (SECRET_KEY, DATABASE)
└── app/
    ├── __init__.py           # Application Factory: create_app()
    ├── extensions.py         # نمونه‌های db و csrf
    ├── models.py             # مدل‌های دیتابیس (SQLAlchemy)
    ├── rate_limit_function.py# محدودیت نرخ درخواست
    ├── routes/               # همه‌ی بلوپرینت‌ها
    │   ├── __init__.py       # all_blueprints (تجمیع)
    │   ├── auth.py           # احراز هویت + current_user + login_required
    │   ├── main.py           # صفحات اصلی، داشبورد، درباره، تماس، جستجو
    │   ├── projects.py       # پروژه‌ها و پیشنهادها
    │   ├── freelancers.py    # دایرکتوری، پروفایل و نظرات فریلنسرها
    │   ├── admin.py          # پنل مدیریت
    │   └── api.py            # REST API
    ├── templates/            # قالب‌های Jinja2 (RTL فارسی)
    │   ├── base.html         # چیدمان پایه
    │   ├── main/             # index, about, contact, dashboard, search
    │   ├── auth/             # login, register, profile
    │   ├── projects/         # list, detail, create, _card
    │   ├── freelancers/      # list, detail, edit, _card
    │   ├── admin/            # dashboard, users, projects, categories, skills, reviews
    │   └── errors/           # 400, 403, 404, 429, 500
    └── static/
        ├── css/style.css     # استایل حرفه‌ای و واکنش‌گرا
        └── js/main.js        # اسکریپت‌های تعاملی
```

---

## 🛠 پیش‌نیازها

- Python 3.10 یا بالاتر
- pip

---

## ⚙️ نصب و راه‌اندازی

### ۱. کلون کردن پروژه

```bash
git clone <repository-url>
cd Freelancer
```

### ۲. ساخت محیط مجازی

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### ۳. نصب وابستگی‌ها

```bash
pip install flask flask-sqlalchemy flask-wtf python-dotenv
```

### ۴. تنظیم متغیرهای محیطی

یک فایل `.env` در ریشه پروژه بسازید:

```env
SECRET_KEY=your-secret-key-here
DATABASE=sqlite:///Freelancer.db
FLASK_ENV=development
```

### ۵. اجرای برنامه

```bash
python run.py
```

برنامه در آدرس `http://127.0.0.1:5000` در دسترس خواهد بود.

> **نکته:** جداول دیتابیس به‌صورت خودکار در اولین اجرا ساخته می‌شوند.

---

## 🌐 مسیرها (Routes)

### صفحات اصلی (`main_bp`)

| متد | مسیر | توضیح |
|-----|------|-------|
| GET | `/` | صفحه اصلی |
| GET | `/about` | درباره ما |
| GET/POST | `/contact` | تماس با ما |
| GET | `/dashboard` | داشبورد کاربر (نیاز به ورود) |
| GET | `/search` | جستجوی پروژه/فریلنسر |

### احراز هویت (`auth_bp` — پیشوند `/auth`)

| متد | مسیر | توضیح |
|-----|------|-------|
| GET/POST | `/auth/register` | ثبت‌نام |
| GET/POST | `/auth/login` | ورود |
| GET | `/auth/logout` | خروج |
| GET/POST | `/auth/profile` | ویرایش پروفایل |

### پروژه‌ها (`projects_bp` — پیشوند `/projects`)

| متد | مسیر | توضیح |
|-----|------|-------|
| GET | `/projects/` | لیست پروژه‌ها |
| GET | `/projects/<slug>` | جزئیات پروژه |
| GET/POST | `/projects/new` | ثبت پروژه جدید |
| POST | `/projects/<slug>/proposal` | ارسال پیشنهاد |
| POST | `/projects/proposals/<id>/<action>` | پذیرش/رد پیشنهاد |

### فریلنسرها (`freelancers_bp` — پیشوند `/freelancers`)

| متد | مسیر | توضیح |
|-----|------|-------|
| GET | `/freelancers/` | دایرکتوری فریلنسرها |
| GET | `/freelancers/<id>` | پروفایل فریلنسر |
| GET/POST | `/freelancers/me` | ویرایش پروفایل فریلنسری |
| POST | `/freelancers/<id>/review` | ثبت نظر |

### مدیریت (`admin_bp` — پیشوند `/admin`)

| متد | مسیر | توضیح |
|-----|------|-------|
| GET | `/admin/` | داشبورد مدیریت |
| GET | `/admin/users` | مدیریت کاربران |
| POST | `/admin/users/<id>/toggle` | فعال/غیرفعال کردن کاربر |
| GET | `/admin/projects` | مدیریت پروژه‌ها |
| POST | `/admin/projects/<id>/feature` | ویژه کردن پروژه |
| GET/POST | `/admin/categories` | مدیریت دسته‌بندی‌ها |
| GET/POST | `/admin/skills` | مدیریت مهارت‌ها |
| GET | `/admin/reviews` | مدیریت نظرات |

### API (`api_bp` — پیشوند `/api`)

| متد | مسیر | توضیح |
|-----|------|-------|
| GET | `/api/health` | بررسی سلامت |
| GET | `/api/projects` | لیست پروژه‌ها |
| GET | `/api/projects/<slug>` | جزئیات پروژه |
| GET | `/api/freelancers` | لیست فریلنسرها |
| GET | `/api/categories` | لیست دسته‌بندی‌ها |
| GET | `/api/skills` | لیست مهارت‌ها |
| GET | `/api/stats` | آمار کلی |
| GET | `/api/me` | اطلاعات کاربر (نیاز به ورود) |
| GET | `/api/my/proposals` | پیشنهادهای من |
| GET | `/api/projects/<slug>/proposals` | پیشنهادهای یک پروژه |

---

## 🗄 مدل‌های دیتابیس

- **User** — حساب کاربری (کارفرما/فریلنسر/مدیر) با رمزنگاری رمز عبور
- **FreelancerProfile** — اطلاعات تخصصی فریلنسر (نرخ ساعتی، مهارت‌ها، امتیاز)
- **Skill** — مهارت‌ها
- **Category** — دسته‌بندی پروژه‌ها
- **Project** — پروژه‌ها با بودجه، مهلت و وضعیت
- **Proposal** — پیشنهادهای فریلنسرها (یکتا برای هر پروژه/فریلنسر)
- **Review** — نظرات و امتیازها

---

## 🔒 امنیت

- رمزهای عبور با `werkzeug.security` هش می‌شوند
- محافظت CSRF روی تمام فرم‌های POST
- محدودیت نرخ درخواست در `before_request`
- کنترل دسترسی با `login_required` و `admin_required`
- کوئری‌های پارامتری SQLAlchemy (جلوگیری از SQL Injection)

---

## 🧑‍💻 توسعه

- **زبان:** Python 3
- **فریم‌ورک:** Flask
- **ORM:** Flask-SQLAlchemy
- **فرم‌ها:** Flask-WTF (CSRF)
- **دیتابیس:** SQLite (قابل تغییر به PostgreSQL/MySQL)
- **فرانت‌اند:** HTML5 + CSS3 + JavaScript (Vanilla)

---

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.
