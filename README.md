
Then activate venv:
--venv\Scripts\activate

pip list
pip install psycopg2-binary

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:your_password@localhost:5432/mosque_db"

 SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin123@localhost:5432/DN_mosque_db"


-----------verion 2.0------
MosqueManagement/
│
├── app/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── member.py
│   │   ├── imam.py
│   │   ├── friday_donation.py
│   │   ├── general_contribution.py
│   │   ├── imam_salary_contribution.py
│   │   └── imam_salary_payment.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── members.py
│   │   ├── imam.py
│   │   ├── friday.py
│   │   ├── general_contribution.py
│   │   ├── salary.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── pdf_service.py
│   │   ├── email_service.py
│   │   ├── whatsapp_service.py
│   │   └── report_service.py
│   │
│   ├── utils/
│   │   ├── helper.py
│   │   └── constants.py
│   │
│   ├── templates/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── members/
│   │   ├── imam/
│   │   ├── donation/
│   │   ├── reports/
│   │   └── salary/
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── uploads/
│   │
│   └── forms/
│       ├── login_form.py
│       ├── member_form.py
│       └── imam_form.py
│
├── instance/
├── migrations/
├── tests/
├── docs/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md




select * from prayer_time

insert into prayer_time (prayer_name,prayer_time) VALUES()
INSERT INTO prayer_time (prayer_name, prayer_time,display_order) VALUES
('Fajr', '05:10',1),
('Dhuhr', '12:30',2),
('Asr', '16:00',3),
('Maghrib', '18:45',4),
('Isha', '20:00',5),
('Jumma', '13:10',6);