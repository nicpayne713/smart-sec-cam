import json
import time

import eventlet
from flask import Flask, send_from_directory, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room

from smart_sec_cam.redis import RedisImageReceiver
from smart_sec_cam.video.manager import VideoManager

eventlet.monkey_patch()
app = Flask(__name__, static_url_path='', static_folder='/backend/build', template_folder='/backend/build')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

VIDEO_DIR = "data/videos"

rooms = {}


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)


@app.route('/videos', defaults={'path': 'videos'})
@app.route('/', defaults={'path': ''})
def serve_react_ui(path):
    return render_template("index.html")


@app.route("/rooms", methods=["GET"])
def get_rooms():
    global rooms
    return json.dumps({'rooms': rooms}), 200, {'ContentType': 'application/json'}


@app.route("/video-list", methods=["GET"])
def get_video_list():
    video_type = request.args.get("video-format")  # "webm" or "mp4"
    global VIDEO_DIR
    video_manager = VideoManager(video_dir=VIDEO_DIR)
    return json.dumps({'videos': video_manager.get_video_filenames(video_type)}), 200, {
        'ContentType': 'application/json'}


@app.route("/video/<file_name>", methods=["GET"])
def get_video(file_name: str):
    global VIDEO_DIR
    if "webm" in file_name:
        mime_type = 'video/webm'
    elif "mp4" in file_name:
        mime_type = 'video/mp4'
    else:
        return json.dumps({'status': "ERROR"}), 404, {'ContentType': 'application/json'}
    return send_from_directory(VIDEO_DIR, file_name, as_attachment=True, mimetype=mime_type)


def listen_for_images(redis_url: str, redis_port: int):
    global rooms
    started_listener_thread = False
    image_receiver = RedisImageReceiver(redis_url, redis_port)
    while True:
        # Check for new channels
        # TODO: This should only be done every N seconds
        channel_list = image_receiver.get_all_channels()
        if channel_list != image_receiver.subscribed_channels:
            image_receiver.set_channels(channel_list)
            if not started_listener_thread:
                image_receiver.start_listener_thread()
        # Check for new messages
        if image_receiver.has_message() and image_receiver.subscribed_channels:
            message = image_receiver.get_message()
            image = message.get("data")
            room = str(message.get("channel"))
            rooms[room] = time.time()
            socketio.emit('image', {'room': room, 'data': image}, room=room)
        time.sleep(0.01)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--redis-url', help='Server address to stream images to', default='localhost')
    parser.add_argument('--redis-port', help='Server port to stream images to', default=6379)
    parser.add_argument('--video-dir', help='Directory in which video files are stored', default="data/videos")
    args = parser.parse_args()

    VIDEO_DIR = args.video_dir

    socketio.start_background_task(listen_for_images, args.redis_url, args.redis_port)
    socketio.run(app, host='0.0.0.0', port="8443", debug=True, certfile='certs/sec-cam-server.cert',
                 keyfile='certs/sec-cam-server.key')
