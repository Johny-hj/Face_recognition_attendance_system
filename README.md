# Face Recognition Attendance System

> **AI-powered attendance tracking** using real-time face recognition, built with Flask, OpenCV, and the `face_recognition` library.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey?logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-green?logo=opencv)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

| Feature | Description |
|---------|-------------|
| 🎯 **Face Recognition Attendance** | Mark attendance automatically via webcam with confidence scoring |
| 📊 **Admin Dashboard** | Visual summary with Chart.js — weekly trends, department breakdown |
| 👨‍🎓 **Student Management** | Full CRUD with photo upload and automatic face encoding |
| 📝 **Manual Attendance** | Fallback manual entry with date/time/status selection |
| 📈 **Reports & Analytics** | Filter by date range, department, student with summary stats |
| 📥 **Excel Export** | Download attendance reports as `.xlsx` files via pandas + openpyxl |
| 🎨 **Dark / Light Theme** | Configurable UI theme stored in application settings |
| 🚀 **Render Deployment Ready** | Pre-configured `render.yaml`, `Procfile`, and `gunicorn.conf.py` |

---

## Tech Stack

- **Backend:** Flask 3.1, SQLAlchemy 2.0, Flask-Login, Flask-WTF
- **Face Recognition:** `face_recognition` (dlib), OpenCV, NumPy, Pillow
- **Database:** SQLite (development) / PostgreSQL (production)
- **Reports:** pandas, openpyxl
- **Frontend:** Bootstrap 5, Chart.js
- **Deployment:** Gunicorn, Render

---

## Prerequisites

- **Python 3.12+**
- **CMake** — required to build dlib (the engine behind `face_recognition`)
- **Visual Studio Build Tools** (Windows) or `build-essential` (Linux/macOS)

### Installing CMake

```bash
# Windows (via Chocolatey)
choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System'

# macOS
brew install cmake

# Ubuntu / Debian
sudo apt-get install -y cmake build-essential libopenblas-dev liblapack-dev
```

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd face-attendance-system

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key-…` | Flask session secret — **change in production** |
| `DATABASE_URL` | `sqlite:///attendance.db` | Database connection string |
| `FLASK_ENV` | `development` | `development` or `production` |
| `PORT` | `5000` | Server port |

---

## Database Setup

```bash
# Create all tables and seed default settings
flask init-db

# Create the default admin account
flask seed-admin
```

**Default admin credentials:**

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

> ⚠️ **Change the default password immediately after first login.**

---

## Running Locally

```bash
python app.py
```

Visit **[http://localhost:5000](http://localhost:5000)**

---

## Render Deployment

1. Push the repository to **GitHub**
2. Create a **New Web Service** on [Render](https://render.com)
3. Connect your repository
4. Render will detect and use `render.yaml` automatically
5. After deployment, open the **Render Shell** and run:
Note: 
Deployment Status: The application was deployed to Render; however, the deployment was unsuccessful due to the large size and resource requirements of dependencies such as dlib, OpenCV, and other face-recognition-related libraries. These dependencies significantly increase build size and memory consumption, exceeding the platform's deployment constraints. Further optimization and dependency management are required before the application can be successfully deployed.   
```bash
flask init-db
flask seed-admin
```

The `render.yaml` blueprint provisions:
- A **Web Service** with CMake/dlib build dependencies
- A **Free PostgreSQL** database (`face_attendance`)
- Auto-generated `SECRET_KEY`

---

## Project Structure

```
face-attendance-system/
├── app.py                  # Application factory & entry point
├── config.py               # Configuration classes
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment blueprint
├── Procfile                # Gunicorn process file
├── gunicorn.conf.py        # Gunicorn server configuration
├── .env.example            # Environment variable template
│
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py         # db instance & model imports
│   ├── student.py          # Student model
│   ├── attendance.py       # Attendance model
│   ├── admin.py            # Admin model (Flask-Login)
│   └── settings.py         # Key-value settings model
│
├── routes/                 # Flask blueprints
│   ├── __init__.py         # Blueprint imports
│   ├── main.py             # Login / logout / index
│   ├── dashboard.py        # Dashboard & chart APIs
│   ├── students.py         # Student CRUD
│   ├── attendance.py       # Attendance (camera + manual)
│   ├── reports.py          # Reports & Excel export
│   └── settings.py         # App settings & account mgmt
│
├── utils/                  # Shared utilities
│   ├── __init__.py
│   ├── helpers.py          # File upload, validation, pagination
│   └── decorators.py       # Route decorators
│
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── uploads/            # Student photos (auto-created)
│
└── templates/              # Jinja2 templates
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── errors/
    ├── students/
    ├── attendance/
    ├── reports/
    └── settings/
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/attendance/api/recognize` | Face recognition (JSON, base64 image) |
| `GET` | `/dashboard/api/weekly-stats` | Weekly attendance chart data |
| `GET` | `/dashboard/api/department-stats` | Department distribution data |
| `GET` | `/reports/export` | Download Excel report |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `dlib` won't install | Install **CMake** first, ensure C++ compiler is available |
| Camera not working | Browser requires **HTTPS** for `getUserMedia` (use localhost for dev) |
| PostgreSQL connection error | Verify `DATABASE_URL` is set and the database exists |
| `face_recognition` import error | Ensure `dlib` compiled successfully with face recognition models |
| Large photo uploads failing | Increase `MAX_CONTENT_LENGTH` in config (default: 16 MB) |

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
