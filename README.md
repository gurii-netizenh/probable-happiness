# HappiTrack

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)

**HappiTrack** is a full-stack web application built with Flask for tracking and predicting daily happiness levels. Inspired by positive psychology research (e.g., Harvard's Grant Study), users answer quick quizzes on habits like sleep, exercise, and social connections to get a "probable happiness" score (0-100), personalized tips, and trend visualizations. It's guest-friendly (no login for basic quizzes) but encourages authentication for saving data, charts, and exports.


- **Tech Stack**: Flask, SQLAlchemy (SQLite), Flask-Login, WTForms, Bootstrap 5, Chart.js, Jinja2.
- **Status**: Production-ready MVP (tested on Python 3.12, Windows/Linux).

## Features

- **Daily Happiness Quiz**: 5 weighted questions (sleep 20%, exercise 25%, connections 30%, gratitude 15%, overall 10%) with normalized scoring (max 100).
- **Guest Mode**: Try quizzes without signup—scores flash with login nudge.
- **User Auth**: Secure registration/login/logout with role-based access (user/admin).
- **Dashboard**: Personalized overview with recent scores and average.
- **History & Trends**: Interactive line charts (Chart.js) of scores over time + CSV export.
- **Profile & Admin**: View/edit user details; admin sees all users/logs.
- **Tips & Emails**: Randomized advice based on score; optional email summaries (SMTP via Flask-Mail).
- **UI/UX**: Responsive Bootstrap design with dark mode toggle, animations, and mood-themed cards.
- **Security**: CSRF protection, hashed passwords (Werkzeug), open redirect guards.

## Installation & Setup

### Prerequisites

- Python 3.12+
- Git

### Quick Start (Local Dev)

1. **Clone Repo**:

   ```
   git clone https://github.com/Gurry-12/probable-happiness.git  # Or your repo
   cd probable-happiness
   ```

2. **Virtual Environment**:

   ```
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```
   pip install -r requirements.txt
   ```

   `requirements.txt` contents:

   ```
   flask==3.0.0
   flask-login==0.6.3
   flask-wtf==1.2.1
   flask-sqlalchemy==3.1.1
   flask-mail==0.10.0
   python-dotenv==1.0.0
   werkzeug==3.0.1
   wtforms==3.1.1
   ```

4. **Environment Variables** (.env file—create in root, gitignore it):

   ```
   SECRET_KEY=your_super_secret_key_here  # Generate: python -c 'import secrets; print(secrets.token_hex(16))'
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password  # Gmail app password
   ```

   - Emails optional (skips if no MAIL_USERNAME).

5. **Database Setup**:

   ```
   python setup_db.py  # Creates instance/happitrack.db + seeds admin user
   ```

   - Admin: Username `admin`, Email `admin@example.com`, Password `adminpass`.

6. **Run App**:

   ```
   set FLASK_APP=app.py  # Windows; export on Mac/Linux
   flask run --debug
   ```

   - Visit `http://127.0.0.1:5000/` (landing page).
   - Init DB if needed: `/init-db`.

### Deployment (Heroku Example)

1. Install Heroku CLI, `heroku create happitrack-app`.
2. Add `Procfile`: `web: gunicorn app:app` (`pip install gunicorn`).
3. Set env vars: `heroku config:set SECRET_KEY=...` (all from .env).
4. For Postgres: `heroku addons:create heroku-postgresql:hobby-dev` → Update `config.py` URI.
5. `git push heroku main && heroku open`.

## Usage

1. **As Guest**: Land on `/` → "Try Quiz as Guest" → Submit form → See score/tip → "Login to Save".
2. **Signup/Login**: `/register` or `/login` → Redirects to dashboard.
3. **Quiz Flow**: `/quiz` → Answer (e.g., sleep=8, exercise=4) → `/result` (score ~75, tip) → Check "Log" for save.
4. **Dashboard**: `/dashboard` → Recent averages + quick quiz link.
5. **History**: `/history` → Line chart of trends + export CSV.
6. **Admin**: Login as admin → `/admin` for user/logs overview.

### Example Quiz Score Calc

- Inputs: Sleep=10/10 (20%), Exercise=5/5 (25%), Connections=4/5 (30%), Gratitude=3/5 (15%), Overall=8/10 (10%).
- Normalized: Sum weights → 85/100 ("Room to grow! Try a 10-min walk.").

## Project Structure

```
probable-happiness/
├── app.py              # Main Flask app + routes
├── config.py           # App config (SECRET_KEY, DB URI)
├── models.py           # SQLAlchemy models (User, Log)
├── utils.py            # Helpers (scoring, logging, export, email)
├── setup_db.py         # One-time DB init script
├── requirements.txt    # Dependencies
├── .env                # Env vars (gitignore)
├── templates/          # Jinja2 HTML (base.html, index.html, quiz.html, etc.)
├── static/             # CSS/JS (custom.css, charts.js)
└── instance/           # SQLite DB (happitrack.db)
```

## Contributing

1. Fork & clone.
2. Create branch: `git checkout -b feature/new-tip`.
3. Commit: `git commit -m "Add ML predictions"`.
4. Push/PR to main.

Issues? Open a ticket. Pull requests welcome—focus on UX, security, or ML enhancements (e.g., scikit-learn for score predictions).

## License

MIT License—see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com).
- Icons: [Font Awesome](https://fontawesome.com).
- Research: Harvard Grant Study on happiness factors.

Questions? [Open an issue](https://github.com/Gurry-12/probable-happiness/issues). Happy tracking! 🌟

