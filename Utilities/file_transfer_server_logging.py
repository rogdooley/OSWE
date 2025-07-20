import random
import string
import threading
import time
import base64
import typing

from pathlib import Path
from flask import Flask, request, send_file, abort, render_template_string
from werkzeug.serving import make_server
from datetime import datetime, timezone

from offsec_logger import OffsecLogger

"""
file_transfer_server.py

Author: Roger Dooley
Created for: Offensive Security OSWE (WEB-300) coursework and PoC development

This module defines the `FileTransferServer` class, a flexible Flask-based HTTP server 
used for file uploads, downloads, and base64-encoded data exchange during offensive operations. 
This version integrates the `OffsecLogger` utility for colorized console output, structured 
status indicators, and optional dual logging to disk.

Key Features:
- Handles GET/POST requests for raw or base64-encoded data
- Enforces configurable one-time or limited-use transfers
- Gracefully shuts down after completing transfers or on local request
- Provides optional HTML landing page for download links
- Dynamically generates random routes for PoC delivery stealth
- Supports custom callbacks (e.g., to trigger next stage of exploit)
- Uses OffsecLogger for structured output: [+], [*], [!], etc.
- Logs to both file and stdout with stage timing support

Example:
    from file_transfer_server import FileTransferServer

    fts = FileTransferServer(
        file_path="loot.bin",
        save_dir=Path("/tmp"),
        direction="upload",
        limit=1,
        encoded=True,
        log_to_console=True,
        log_to_file=True,
        log_file_path="upload.log",
        html_page_route='/drop',
        on_transfer=lambda p, c: print(f"Received {p}")
    )
    fts.start()

Use Cases:
- Exploit file hosting or exfiltration drop points
- Offline file transfers during blind SSRF or LFI chains
- Temporary file staging within red team infrastructure
- Automated testing in OSWE/WEB-300-style PoC chains

Note:
Not designed for long-term hosting. For offensive testing use only.
"""

html_template = """
<html>
<head><title>File Transfer Page</title></head>
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
                html_page_route='/transfer', on_transfer: typing.Callable[[Path, int], None] | None = None,
                logger: OffsecLogger | None = None):

        self.file_path = Path(file_path)
        self.save_dir = Path(save_dir)
        self.direction = direction
        self.limit = limit
        self.encoded = encoded
        self.port = port
        self.enable_html_page = enable_html_page
        self.html_page_route = html_page_route
        self.route = route or self._generate_route()
        self.transfer_count = 0
        self.on_transfer = on_transfer

        self.logger = logger or OffsecLogger()

        self.app = Flask(__name__)
        self._configure_routes()
        if self.enable_html_page:
            self._configure_html_page()

    def _generate_route(self, length=8) -> str:
        return '/' + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _configure_routes(self):

        @self.app.route('/__shutdown', methods=['POST'])
        def shutdown():
            if request.remote_addr != '127.0.0.1':
                self.logger.warn("Unauthorized shutdown attempt from {}", request.remote_addr)
                abort(403)

            self.logger.warn("Manual shutdown initiated via /__shutdown")
            shutdown_thread = threading.Thread(target=self.server_thread.shutdown)
            shutdown_thread.start()
            return {"status": "shutting down"}, 200

        if self.direction in ['download', 'both']:
            @self.app.route(self.route, methods=['GET'])
            def handle_download():
                self.logger.info("GET request received on {}", self.route)
                if self.transfer_count >= self.limit:
                    self.logger.warn("Transfer limit reached")
                    abort(410)
                if not self.file_path.exists():
                    self.logger.error("File not found: {}", self.file_path)
                    abort(404)

                self.transfer_count += 1
                self.logger.success("Delivered {} ({} / {})", self.file_path.name, self.transfer_count, self.limit)

                if self.on_transfer:
                    try:
                        self.on_transfer(self.file_path, self.transfer_count)
                    except Exception as e:
                        self.logger.warn("on_transfer raised exception: {}", str(e))
                return send_file(self.file_path, as_attachment=True)

            @self.app.route('/exfil', methods=['GET'])
            def exfil():
                self.logger.info("Exfil request to /exfil")
                b64_data = request.args.get('q')
                filename = request.args.get('filename')
                if b64_data:
                    if not filename:
                        ip = request.remote_addr
                        ts = datetime.now(timezone.utc).isoformat()
                        filename = f"{ip}_{ts}"
                    save_path = self._decode_and_save(b64_data, filename)
                    self.logger.success("Exfil saved: {}", save_path)
                else:
                    self.logger.warn("Missing b64 data")
                    abort(410)

            @self.app.route('/collect', methods=['GET'])
            def collect():
                self.logger.info("Exfil GET to /collect with args: {}", request.query_string.decode())
                path = self.save_dir / f"{request.remote_addr}_{int(time.time())}.log"
                with open(path, "w") as f:
                    f.write(request.query_string.decode())
                return "", 204

        if self.direction in ['upload', 'both']:
            @self.app.route(self.route, methods=['POST'])
            def handle_upload():
                self.logger.info("POST upload received on {}", self.route)
                if self.transfer_count >= self.limit:
                    self.logger.warn("Upload limit exceeded")
                    abort(410)

                if self.encoded:
                    payload = request.get_json()
                    if payload:
                        filename = payload.get("filename", "uploaded.bin")
                        data = payload.get("data")
                        save_path = self._decode_and_save(data, filename)
                    else:
                        data = request.get_data(as_text=True)
                        save_path = self._decode_and_save(data, "fallback.bin")
                        self.logger.info("Received fallback upload")
                elif request.files:
                    file = request.files['file']
                    save_path = self.save_dir / file.filename
                    file.save(save_path)
                else:
                    self.logger.error("Invalid upload request")
                    abort(400)

                self.transfer_count += 1
                self.logger.success("Uploaded {} ({} / {})", save_path.name, self.transfer_count, self.limit)

                if self.on_transfer:
                    try:
                        self.on_transfer(save_path, self.transfer_count)
                    except Exception as e:
                        self.logger.warn("on_transfer raised: {}", str(e))
                return {"status": "uploaded", "path": str(save_path)}, 200

    def _configure_html_page(self):
        route = self.html_page_route
        if not route.startswith("/"):
            route = "/" + route

        @self.app.route(route, methods=['GET'])
        def html_page():
            self.logger.info("HTML download page served")
            return render_template_string(html_template, route=self.route, filename=self.file_path.name)

    def _decode_and_save(self, b64: str, filename: str) -> Path:
        raw = base64.b64decode(b64.encode())
        path = self.save_dir / filename
        with open(path, 'wb') as f:
            f.write(raw)
        return path

    def start(self):
        self.logger.status("Starting server on port {} at {}", self.port, self.route)

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

        def shutdown_watcher():
            while self.transfer_count < self.limit:
                time.sleep(1)
            self.logger.status("Limit reached. Shutting down...")
            self.server_thread.shutdown()

        threading.Thread(target=shutdown_watcher, daemon=True).start()

    def stop(self):
        if hasattr(self, 'server_thread'):
            self.server_thread.shutdown()

    def __repr__(self):
        return f"<FTS route={self.route} port={self.port} direction={self.direction}>"