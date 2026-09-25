# WasteWise AI

WasteWise AI is a smart waste-monitoring dashboard built to track bin fill levels, surface potential overflow risks, and support more efficient waste collection planning. The project combines backend analytics, a small data pipeline, and a machine-learning-inspired classification workflow to simulate a real operational monitoring system.

## Product goal

The application is designed to help a city or facility team monitor waste bins and understand whether maintenance should be triggered. It includes:

- live and historical waste statistics
- alert generation for threshold breaches
- settings for notification and capacity thresholds
- dashboard analytics for operational decisions
- prototype computer-vision support for deposit detection and classification

## Technical architecture

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- SQLite database for local persistence
- REST API endpoints for stats, alerts, and settings

The backend is implemented in `backend/app.py` and contains:

- `WasteMeasurement` model for recorded fill-level samples
- `Alert` model for threshold or overflow events
- `Settings` model for operational thresholds
- `HistoricalStats` model to archive summary metrics over time

### Frontend
- React
- Create React App
- Browser-based dashboard with route-based views

The frontend under `src/` consumes the Flask API and displays:

- dashboard summaries
- analytics pages
- alerts feed
- settings configuration

### Sensor and ML pipeline
The project includes more than just a dashboard. It also contains a prototyping pipeline for waste detection:

- `serial_forwarder.py` reads serial data from a sensor device and forwards fill-level telemetry to the backend
- `model/end2endInference.py` performs optical flow and background subtraction to detect deposits or objects in a camera frame
- a pretrained EfficientNet-based model is used for classification of detected waste regions

This creates a full prototype loop: sensor input -> analytics -> alerting -> visual monitoring.

## Core implementation details

### API layer
The backend exposes REST routes such as:

- `GET /api/current-stats`
- `POST /api/current-stats`
- `GET /api/alerts`
- `POST /api/alerts`
- `POST /api/alerts/<id>/dismiss`
- `GET /api/settings`
- `POST /api/settings`
- `GET /api/historical-stats`
- `POST /api/reset-bin`

These endpoints power the dashboard and are designed to model a real operational control interface.

### Analytics logic
The project calculates:

- current fill level and historical averages
- efficiency scores
- percentage distribution across recycling categories
- maximum temperature and fill-duration metrics

When the bin is reset, the backend archives the current cycle into `HistoricalStats` and clears active measurements.

### Alerting system
The API can create, list, and dismiss alerts. This allows the system to model overflow or threshold conditions in a lightweight, real-world SaaS-like pattern.

## Repository structure

```text
backend/
  app.py
  requirements.txt
  seed_data.py
  test_alerts.py
  test_data.py
model/
  end2endInference.py
  best_model_efficientnet_v2_s.pth
sensor/
  mcpwm_capture_hc_sr04/
serial_forwarder.py
src/
  App.js
  components/
  utils/
public/
```

## Local setup

### Backend

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

### Frontend

```bash
npm install
npm start
```

The app is served at:

```text
http://localhost:3000
```

## Machine-learning / vision prototype

The model script uses:

- OpenCV for frame capture and motion tracking
- background subtraction and contour analysis to detect deposits
- EfficientNet V2 for classifying waste regions based on extracted ROI images

This makes the project more than a simple data dashboard: it acts as a prototype for AI-enabled environmental monitoring and predictive maintenance.

## Why this project is technically interesting

WasteWise AI demonstrates how to combine multiple layers of a real system:

- sensor or telemetry ingestion
- backend data persistence and analytics
- real-time dashboard visualization
- alerting and operational decision support
- computer-vision-based classification prototype

It is a strong example of an applied ML + software engineering hackathon project.

## Notes

This project is structured as a prototype and proof-of-concept rather than a production-grade municipal platform. It demonstrates the feasibility of combining waste telemetry, analytics, and AI-driven monitoring in a compact, end-to-end application.
