import os
from app import create_app
from app.extensions import db

app = create_app()

@app.cli.command("create-demo-data")
def create_demo_data():
    """Create demo users and listings (placeholder)."""
    pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 Lucky Kangaroo Backend démarré!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=app.config.get('DEBUG', True))
