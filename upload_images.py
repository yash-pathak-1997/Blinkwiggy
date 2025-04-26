import os
from flask import Blueprint, request, jsonify, session
from db.postgres import PostgresConnection
from redis import Redis
from rq import Queue
from tasks.image_tasks import upload_to_minio_task
from tasks.ocr import process_order_images

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

image_upload_bp = Blueprint('image_upload', __name__)
redis_conn = Redis(host='redis', port=6379)
task_queue = Queue(connection=redis_conn)


@image_upload_bp.route('/upload', methods=['POST'])
def upload_image_paths():
    username = session.get('username')
    paths = request.form.getlist('paths')

    if not username:
        return jsonify({"error": "User not logged in"}), 401
    if not paths:
        return jsonify({"error": "No paths provided"}), 400

    db = PostgresConnection(
        dbname='image_db',
        user='postgres',
        password='postgres',
        host='host.docker.internal',
        port='33333'
    )

    for path in paths:
        db.insert_image_path(username, path)
        task_queue.enqueue(upload_to_minio_task, path, username)

    valid_paths = [p for p in paths if os.path.exists(p)]

    task_queue.enqueue(process_order_images, username, valid_paths)

    db.close()
    return jsonify({"message": "Paths recorded", "username": username, "paths": paths})
