from flask import Blueprint, send_from_directory

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def serve_index():
    return send_from_directory('../client', 'index.html')

@static_bp.route('/<path:filename>')
def serve_client_files(filename):
    return send_from_directory('../client', filename)

@static_bp.route('/admin/')
def serve_admin():
    return send_from_directory('../client/admin', 'admin.html')

@static_bp.route('/admin/<path:filename>')
def serve_admin_files(filename):
    return send_from_directory('../client/admin', filename)