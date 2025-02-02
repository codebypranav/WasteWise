from app import db, WasteMeasurement, Alert
from datetime import datetime, timezone, timedelta

def seed_database():
    # Clear existing data
    db.session.query(WasteMeasurement).delete()
    db.session.query(Alert).delete()

    # Add sample measurements
    measurements = [
        # WasteMeasurement(
        #     timestamp=datetime.now(),
        #     fill_level=30.0,
        #     waste_type='recyclable',
        #     temperature=25.0
        # ),
        # WasteMeasurement(
        #     timestamp=datetime.now(),
        #     fill_level=20.0,
        #     waste_type='organic',
        #     temperature=25.0
        # ),
        # WasteMeasurement(
        #     timestamp=datetime.now(),
        #     fill_level=15.0,
        #     waste_type='non-recyclable',
        #     temperature=25.0
        # )
    ]

    # Add sample alerts
    alerts = [
        # Alert(
        #     message='Bin #103 is at 90% capacity',
        #     location='Building A, Floor 2',
        #     timestamp=datetime.now(timezone.utc) - timedelta(minutes=10)
        # ),
        # Alert(
        #     message='Improper waste sorting detected',
        #     location='Building B, Floor 1',
        #     timestamp=datetime.now(timezone.utc) - timedelta(hours=1)
        # ),
        # Alert(
        #     message='Scheduled maintenance tomorrow',
        #     location='All Buildings',
        #     timestamp=datetime.now(timezone.utc) - timedelta(hours=2)
        # )
    ]

    db.session.bulk_save_objects(measurements)
    db.session.bulk_save_objects(alerts)
    db.session.commit()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_database() 