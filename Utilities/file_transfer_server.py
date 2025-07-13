import random
import string
import logging
import threading
import time
import typing
import base64
import json


from pathlib import Path
from flask import Flask, request, send_file, abort, render_template_string
from werkzeug.serving import make_server
from datetime import datetime, timezone


"""
file_transfer_server.py

Author: Roger Dooley
Created for: Offensive Security OSWE (WEB-300) coursework and PoC development

This module defines the `FileTransferServer` class, a lightweight and configurable
Flask-based HTTP server for file upload/download and base64-encoded data transfer.

Key Features:
- Handles GET and POST requests with configurable transfer limits
- Supports raw file uploads or base64-encoded payloads (JSON or query parameter)
- Optional HTML landing page for downloads
- Graceful shutdown via internal thread watcher or authenticated route
- Console and file logging with configurable verbosity
- Dynamic route generation to support unique URLs in PoCs

Usage:
    from file_transfer_server import FileTransferServer

    fts = FileTransferServer(
        file_path="loot.zip",
        save_dir="/tmp",
        direction="upload",
        limit=1,
        encoded=True,
        enable_html_page=True,
        html_page_route='/transfer'
    )
    fts.start()

Intended for integration into proof-of-concept scripts, red team operations,
CTFs, and automated offensive workflows.

Note:
This module is not intended for long-term production use. Use responsibly and only
in environments where you have explicit permission to perform testing.
"""



html_template = """
<html>
<head>
<title>File Transfer Page</title>
</head>
<body>
    <h2>Download Available</h2>
    <a href="{{ route }}">Download {{ filename }}</a>
</body>
</html>
"""


class FileTransferServer:
    def __init__(self, file_path, save_dir, direction='download', limit=1, encoded=False,
                route=None, port=8888, log_to_console=True, log_to_file=False,
                log_file_path='transfer.log', log_level='INFO', enable_html_page=False,
                html_page_route='/transfer'):
        self.file_path = file_path
        self.save_dir = save_dir
        self.direction = direction
        self.limit = limit
        self.encoded = encoded
        self.port = port
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.log_file_path = Path(log_file_path)
        self.log_level = log_level.upper()
        self._setup_logging()
        self.verbose_repr = self.logger.level
        self.enable_html_page = enable_html_page
        self.html_page_route = html_page_route

        self.transfer_count = 0
        self.route = route or self._generate_route()

        self.app = Flask(__name__)
        self._configure_routes()
        if self.enable_html_page:
            self._configure_html_page()

        self.on_transfer = on_transfer


    def _generate_route(self, length=8) -> str:
        return '/' + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


    def _setup_logging(self):
        self.logger = logging.getLogger(f'FileTransferServer:{id(self)}')

        level = getattr(logging, self.log_level, logging.INFO)
        self.logger.setLevel(level)

        log_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handlers = []

        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            handlers.append(console_handler)

        if self.log_to_file:
            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setFormatter(log_format)
            handlers.append(file_handler)
        
        # Clear previous handlers if any (for interactive environments)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        for handler in handlers:
            self.logger.addHandler(handler)
            

    def _configure_routes(self):

        @self.app.route('/__shutdown', methods=['POST'])
        def shutdown():
            if request.remote_addr != '127.0.0.1':
                self.logger.warning("Unauthorized shutdown attempt from %s", request.remote_addr)
                abort(403)
            
            self.logger.warning("Manual shutdown initiated via /__shutdown")
            shutdown_thread = threading.Thread(target=self.server_thread.shutdown)
            shutdown_thread.start()
            return {"status": "shutting down"}, 200


        if self.direction in [ 'download', 'both']:
            @self.app.route(self.route, methods=['GET'])
            def handle_download():
                self.logger.info("Incoming GET request to %s", self.route)
                if self.transfer_count >= self.limit:
                    self.logger.warning("Transfer limit reached. Aborting.")
                    abort(410)
                if not Path(self.file_path).exists():
                    self.logger.error("File not found %s", self.file_path)
                    abort(404)

                self.transfer_count += 1
                self.logger.info("Transferred %s (count: %d/%d)", self.file_path, self.transfer_count, self.limit)

                if self.on_transfer:                           
                    try:
                        self.on_transfer(Path(self.file_path), self.transfer_count)
                    except Exception as e:
                        self.logger.warning("on_transfer callback raised: %s", e)
                return send_file(self.file_path, as_attachment=True)

            @self.app.route('/exfil', methods=['GET'])
            def exfil():
                self.logger.info("Incoming GET request to /exfil")
                b64_data = request.args.get('q')
                filename = request.args.get('filename')
                if b64_data:

                    if not filename:
                        # if behind a proxy ip_address.remote_addr will return proxy ip
                        # need to get X-Forwarded-For header and parse for remote pi address
                        ip_address = request.remote_addr
                        ts_str = datetime.now(timezone.utc).isoformat()
                        filename = f"{ip_address}_{ts_str}"

                    save_path = self._decode_and_save(b64_data, filename)
                else:
                    self.logger.warning('Data missing from query parameter q or did not use the correct query parameter')
                    abort(410)


        if self.direction in ['upload', 'both']:
            @self.app.route(self.route, methods=['POST'])
            def handle_upload():
                self.logger.info("Incoming POST request to %s", self.route)
                if self.transfer_count >= self.limit:
                    self.logger.warning("Upload limit reached. Aborting.")
                    abort(410)


                if self.encoded:
                    json_response = request.get_json()
                    if json_response:
                        json_filename = None
                        json_encoded_data = None
                        json_filename = json_response.get('filename')
                        json_encoded_data = json_response.get('data')
                        if json_filename and json_encoded_data:
                            save_path = self._decode_and_save(json_encoded_data, json_filename)
                    else:
                        raw_data = request.get_data(as_text=True)
                        fallback_filename = 'uploaded.bin'
                        save_path = self._decode_and_save(raw_data, fallback_filename)
                        self.logger.info("Could not process upload")
                        self.logger.info(f"Content: {request.get_data(as_text=True)}")
                elif request.files:
                    file = request.files['file']
                    filename = file.filename
                    save_path = Path(self.save_dir) / filename
                    file.save(save_path)
                else:
                    self.logger.warning("No valid upload method detected (encoded or file)")
                    abort(400)

                self.transfer_count += 1
                self.logger.info("Saved upload %s (count: %d/%d)", save_path, self.transfer_count, self.limit)

                if self.on_transfer:                           
                    try:
                        self.on_transfer(Path(self.file_path), self.transfer_count)
                    except Exception as e:
                        self.logger.warning("on_transfer callback raised: %s", e)

                return {"status" : 'uploaded', 'path': str(save_path)}, 200


    def _configure_html_page(self) -> None:
        if not self.html_page_route.startswith("/"):
            route = "/" + self.html_page_route
        else:
            route = self.html_page_route
        @self.app.route(f"{route}", methods=['GET'])
        def render_transfer_page():
            self.logger.debug("HTML page requested from %s", request.remote_addr)
            return render_template_string(html_template, route=self.route, filename=Path(self.file_path).name)


    def _decode_and_save(self, data: str, filename: str) -> Path:
        decoded_data = base64.b64decode(data.encode('utf-8'))
        save_to = self.save_dir / filename
        with open(save_to, 'wb') as f:
            f.write(decoded_data)
        return save_to


    def start(self):
        self.logger.info("Starting server on port %d with route %s", self.port, self.route)

        class ServerThread(threading.Thread):
            def __init__(inner_self):
                inner_self.srv = make_server('0.0.0.0', self.port, self.app)
                inner_self.ctx = self.app.app_context()
                inner_self.ctx.push()
                super().__init__()

            def run(inner_self):
                inner_self.srv.serve_forever()

            def shutdown(inner_self):
                inner_self.srv.shutdown()

        self.server_thread = ServerThread()
        self.server_thread.start()

        #Watcher thread to shutdown when transfers are done
        def shutdown_watcher():
            while self.transfer_count < self.limit:
                time.sleep(1)
            self.logger.info("Transfer limit reached. Shutting down server.")
            self.server_thread.shutdown()

        threading.Thread(target=shutdown_watcher, daemon=True).start()
    
    def stop(self):
        if hasattr(self, 'server_thread'):
            self.server_thread.shutdown()

    def __str__(self) -> str:
        if self.verbose_repr:
            return (f"FileTransferServer:\n"
                    f"  direction: {self.direction}\n"
                    f"  route: {self.route}\n"
                    f"  port: {self.port}\n"
                    f"  limit: {self.limit}\n"
                    f"  encoded: {self.encoded}")
        else:
            return f"<FileTransferServer {self.direction.upper()} route={self.route} port={self.port}>"

    def __repr__(self) -> str:
     return (f"<FileTransferServer(direction={self.direction}, "
            f"route='{self.route}', port={self.port}, "
            f"limit={self.limit}, encoded={self.encoded})>")


