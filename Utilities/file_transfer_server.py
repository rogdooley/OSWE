import random
import string
import logging
import threading
import time

from pathlib import Path
from flask import Flask, request, send_file, abort
from werkzeug.serving import make_server

class FileTransferServer:
    def __init__(self, file_path, save_dir, direction='download', limit=1, encoded=False,
                route=None, port=8888, log_to_console=True, log_    to_file=False,
                log_file_path='transfer.log', log_level='INFO'):
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

        self.transfer_count = 0
        self.route = route or self._generate_route()

        self.app = Flask(__name__)
        self._configure_routes()


    def _generate_route(self, length=8):
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
            self.logger.warning("Manual shutdown initiated via /__shutdown")
            shutdown_thread = threading.Thread(target=self.server_thread.shutdown)
            shutdown_thread.start()
            return {"status": "shutting down"}, 200

        if self.direction in [ 'download', 'both']:
            @self.app.route(self.route, methods=['GET'])
            def handle_download():
                self.logger.info("Incoming GET request to %s", self.route)
                if self.transfer_count >= self.limit:
                    self.logger.warning("Transfer limite reached. Aborting.")
                    abort(410)
                if not Path(self.file_path).exists():
                    self.logger.error("File not found %s", self.file_path)
                    abort(404)

                self.transfer_count += 1
                self.logger.info("Transferred %s (count: %d/%d)", self.file_path, self.transfer_count, self.limit)
                return send_file(self.file_path, as_attachment=True)

        if self.direction in ['upload', 'both']:
            @self.app.route(self.route, methods=['POST'])
            def handle_upload():
                self.logger.info("Incoming POST request to %s", self.route)
                if self.transfer_count >= self.limit:
                    self.logger.warning("Upload limit reached. Aborting.")
                    abort(410)

                if 'file' not in request.files:
                    self.logger.error("No file part in request.")
                    abort(400)

                file = request.files['file']
                filename = file.filename
                save_path = Path(self.save_dir) / filename
                file.save(save_path)

                self.transfer_count += 1
                self.logger.info("Saved upload %s (count: %d/%d)", save_path, self.transfer_count, self.limit)
                return {"status" : 'uploaded', 'path': str(save_path)}, 200


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
        self.logger.warning("Manual stop() called")
        if hasattr(self, 'server_thread'):
            self.server_thread.shutdown()

    def __str__(self):
        if self.verbose_repr:
            return (f"FileTransferServer:\n"
                    f"  direction: {self.direction}\n"
                    f"  route: {self.route}\n"
                    f"  port: {self.port}\n"
                    f"  limit: {self.limit}\n"
                    f"  encoded: {self.encoded}")
        else:
            return f"<FileTransferServer {self.direction.upper()} route={self.route} port={self.port}>"

    def __repr__(self):
     return (f"<FileTransferServer(direction={self.direction}, "
            f"route='{self.route}', port={self.port}, "
            f"limit={self.limit}, encoded={self.encoded})>")

