import os

from app import create_app

# Set environment variables if not already set
os.environ.setdefault('FLASK_CONFIG', 'development')

app = create_app()

if __name__ == '__main__':
    print(f"Starting Flask application in {app.config.get('ENV', 'default')} mode")
    app.run(
        host='127.0.0.1',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
