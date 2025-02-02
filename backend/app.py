from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import func

app = Flask(__name__)
CORS(app)

# SQLite Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wastewise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class WasteMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    fill_level = db.Column(db.Float, nullable=False)  # percentage
    waste_type = db.Column(db.String(20), nullable=False)  # 'recyclable', 'organic', 'non-recyclable'
    temperature = db.Column(db.Float)  # in Fahrenheit

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    message = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notifications_email = db.Column(db.Boolean, default=False)
    notifications_push = db.Column(db.Boolean, default=False)
    notifications_sms = db.Column(db.Boolean, default=False)
    threshold_capacity = db.Column(db.Integer, default=80)
    threshold_temperature = db.Column(db.Float, default=85.0)

class HistoricalStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    recyclable_percentage = db.Column(db.Float, nullable=False)
    organic_percentage = db.Column(db.Float, nullable=False)
    non_recyclable_percentage = db.Column(db.Float, nullable=False)
    efficiency_score = db.Column(db.Float, nullable=False)
    max_temperature = db.Column(db.Float)
    fill_duration_hours = db.Column(db.Float)  # Time taken to fill the bin

# Routes
# Add this near the top of the file, after the db initialization
current_stats = {'fill_level': 0}  # Global variable to store current fill level

@app.route('/api/current-stats', methods=['GET', 'POST'])
def handle_stats():
    if request.method == 'POST':
        data = request.get_json()
        fill_level = data.get('fill_level', 0)
        current_stats['fill_level'] = fill_level
        
        # Store in database
        measurement = WasteMeasurement(
            fill_level=fill_level,
            waste_type='non-recyclable'  # Since we're only tracking fill level now
        )
        db.session.add(measurement)
        db.session.commit()
        
        return jsonify({"status": "success", "fill_level": fill_level})
    else:  # GET request
        return jsonify({"fill_level": current_stats.get('fill_level', 0)})

@app.route('/api/alerts', methods=['GET', 'POST'])
def handle_alerts():
    """Get or create alerts"""
    if request.method == 'POST':
        try:
            data = request.json
            alert = Alert(
                message=data['message'],
                location=data['location'],
                is_read=data.get('is_read', False)
            )
            db.session.add(alert)
            db.session.commit()
            return jsonify({
                'message': 'Alert created successfully',
                'alert': {
                    'id': alert.id,
                    'message': alert.message,
                    'location': alert.location,
                    'timestamp': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'isRead': alert.is_read
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(10).all()
            return jsonify([{
                'id': alert.id,
                'message': alert.message,
                'location': alert.location,
                'timestamp': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'isRead': alert.is_read
            } for alert in alerts])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<int:alert_id>/dismiss', methods=['POST'])
def dismiss_alert(alert_id):
    """Delete an alert"""
    try:
        alert = Alert.query.get(alert_id)
        if alert:
            db.session.delete(alert)  # Delete instead of marking as read
            db.session.commit()
            return jsonify({'message': 'Alert deleted successfully'})
        return jsonify({'error': 'Alert not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update system settings"""
    if request.method == 'POST':
        try:
            data = request.json
            settings = Settings.query.first()
            if not settings:
                settings = Settings()
                db.session.add(settings)
            
            settings.notifications_email = data['notifications']['email']
            settings.notifications_push = data['notifications']['push']
            settings.notifications_sms = data['notifications']['sms']
            settings.threshold_capacity = data['thresholds']['capacity']
            settings.threshold_temperature = data['thresholds']['temperature']
            
            db.session.commit()
            return jsonify({'message': 'Settings saved successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'notifications': {
                'email': settings.notifications_email,
                'push': settings.notifications_push,
                'sms': settings.notifications_sms
            },
            'thresholds': {
                'capacity': settings.threshold_capacity,
                'temperature': settings.threshold_temperature
            }
        })

@app.route('/api/reset-bin', methods=['POST'])
def reset_bin():
    """Reset the bin and archive current stats"""
    try:
        # Get current measurements
        latest_measurements = {}
        start_time = None
        max_temp = 0
        
        for waste_type in ['recyclable', 'organic', 'non-recyclable']:
            measurements = WasteMeasurement.query\
                .filter_by(waste_type=waste_type)\
                .order_by(WasteMeasurement.timestamp.desc())\
                .all()
            
            if measurements:
                latest_measurements[waste_type] = measurements[0].fill_level
                # Track earliest measurement time and max temperature
                for m in measurements:
                    # Ensure timestamp has timezone info
                    measurement_time = m.timestamp.replace(tzinfo=timezone.utc) if m.timestamp.tzinfo is None else m.timestamp
                    if start_time is None or measurement_time < start_time:
                        start_time = measurement_time
                    if m.temperature and m.temperature > max_temp:
                        max_temp = m.temperature

        if latest_measurements:
            total = sum(latest_measurements.values())
            if total > 0:
                # Calculate percentages
                recyclable_pct = (latest_measurements.get('recyclable', 0) / total * 100)
                organic_pct = (latest_measurements.get('organic', 0) / total * 100)
                non_recyclable_pct = (latest_measurements.get('non-recyclable', 0) / total * 100)
                
                # Calculate efficiency score
                efficiency = (recyclable_pct + organic_pct) / 2
                
                # Calculate fill duration in hours
                end_time = datetime.now(timezone.utc)
                # Ensure start_time has timezone info
                if start_time and start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                duration = (end_time - start_time).total_seconds() / 3600 if start_time else 0

                # Save historical stats
                hist_stats = HistoricalStats(
                    recyclable_percentage=recyclable_pct,
                    organic_percentage=organic_pct,
                    non_recyclable_percentage=non_recyclable_pct,
                    efficiency_score=efficiency,
                    max_temperature=max_temp,
                    fill_duration_hours=duration
                )
                db.session.add(hist_stats)

        # Clear current measurements
        WasteMeasurement.query.delete()
        
        # Clear alerts
        Alert.query.delete()
        
        db.session.commit()
        return jsonify({'message': 'Bin reset successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical-stats', methods=['GET'])
def get_historical_stats():
    """Get historical statistics"""
    try:
        # Get all historical records
        records = HistoricalStats.query.order_by(HistoricalStats.timestamp.desc()).all()
        
        # Calculate averages
        averages = db.session.query(
            func.avg(HistoricalStats.recyclable_percentage).label('avg_recyclable'),
            func.avg(HistoricalStats.organic_percentage).label('avg_organic'),
            func.avg(HistoricalStats.non_recyclable_percentage).label('avg_non_recyclable'),
            func.avg(HistoricalStats.efficiency_score).label('avg_efficiency'),
            func.avg(HistoricalStats.max_temperature).label('avg_max_temp'),
            func.avg(HistoricalStats.fill_duration_hours).label('avg_duration')
        ).first()

        return jsonify({
            'history': [{
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'recyclable': round(record.recyclable_percentage, 1),
                'organic': round(record.organic_percentage, 1),
                'nonRecyclable': round(record.non_recyclable_percentage, 1),
                'efficiency': round(record.efficiency_score, 1),
                'maxTemperature': round(record.max_temperature, 1),
                'fillDuration': round(record.fill_duration_hours, 1)
            } for record in records],
            'averages': {
                'recyclable': round(averages.avg_recyclable or 0, 1),
                'organic': round(averages.avg_organic or 0, 1),
                'nonRecyclable': round(averages.avg_non_recyclable or 0, 1),
                'efficiency': round(averages.avg_efficiency or 0, 1),
                'maxTemperature': round(averages.avg_max_temp or 0, 1),
                'fillDuration': round(averages.avg_duration or 0, 1)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)