# WasteWise AI

WasteWise AI is a smart waste management dashboard designed to monitor bin fill levels, detect overflow risk, and help optimize waste collection schedules using sensor-like data and AI-informed monitoring.

## Overview

The project includes:
- a Flask backend with SQLite persistence
- a React frontend dashboard
- real-time/near-real-time waste statistics
- alert management for overflow conditions
- historical analytics and threshold settings

## Tech stack

- Frontend: React, Create React App
- Backend: Python, Flask, SQLAlchemy
- Database: SQLite
- API layer: RESTful endpoints for stats, alerts, settings, and historical analysis

## Project structure

```text
backend/
  app.py
  requirements.txt
  seed_data.py
  test_alerts.py
  test_data.py
src/
  App.js
  components/
  utils/
public/
```

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend runs on:

```text
http://localhost:5000
```

## Frontend setup

From the project root:

```bash
npm install
npm start
```

The app will be available at:

```text
http://localhost:3000
```

## Features

- current bin fill level monitoring
- alert generation and dismissal
- storage threshold configuration
- historical analytics with averages and trends
- reset workflow to archive the current collection cycle

## API highlights

Common endpoints include:

- `GET /api/current-stats`
- `POST /api/current-stats`
- `GET /api/alerts`
- `POST /api/alerts`
- `GET /api/settings`
- `POST /api/settings`
- `GET /api/historical-stats`
- `POST /api/reset-bin`

## Notes

This project is intended as a prototype for waste monitoring and optimization, demonstrating how sensor data and analytics can support smarter collection planning.
