# Family Credit Card Spend Tracker

This project is a mobile-first application to track and analyze monthly credit card spending for family members. It uses a Flask backend with an Angular frontend. Transactions are parsed from uploaded PDF statements and organized with tags for flexible reporting.

## Development Setup

1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Upgrade the database:
   ```bash
   flask --app backend/app/main.py db upgrade
   ```
3. Run the application:

   ```bash
   python backend/run.py
   ```


Basic API endpoints are available once the server is running:

- `POST /auth/login` – obtain a JWT token
- `GET /transactions` – list transactions
- `POST /transactions` – create a transaction
- `GET /tags` and `POST /tags`
- `GET /cardholders` and `POST /cardholders`

