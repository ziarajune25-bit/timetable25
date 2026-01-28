#!/usr/bin/env python
"""
Gunicorn configuration file for production deployment
"""

import os
import multiprocessing

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')
backlog = 2048

# Worker processes
workers = os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'timetable-management-system'

# Server mechanics
daemon = False
pidfile = None
umask = 0
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# keyfile = '/path/to/keyfile.pem'
# certfile = '/path/to/certfile.pem'
# ca_certs = '/path/to/ca-certs.pem'
# ssl_version = 'TLSv1_2'

# Application
raw_env = ['FLASK_ENV=production']
