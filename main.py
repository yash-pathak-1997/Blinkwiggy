from flask import Flask, session, request
import redis

from services.analytics import analytics_bp
from services.upload_images import image_upload_bp

app = Flask(__name__)
app.secret_key = 'Blinkwiggy'

app.register_blueprint(image_upload_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix="/analytics")

r = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)


@app.route('/')
def home():
    count = r.incr('visit_count')
    user = session.get('username')
    if user:
        return f"Welcome back, {user}! Visit count: {count}"
    return f"Welcome to Blinkwiggy! Visit count: {count}"


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username and password:
        session['username'] = username
        return f"Logged in as {username}"
    return "Missing username or password", 400


@app.route('/logout')
def logout():
    user = session.pop('username', None)
    return f"Logged out {user}" if user else "You were not logged in"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
