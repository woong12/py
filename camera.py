#!/usr/bin/python3

# This is the same as mjpeg_server.py, but uses the h/w MJPEG encoder.

import io
import logging
import socketserver
from http import server
from threading import Condition
from datetime import datetime

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head>
<meta name="viewport" content="width=device-width. initial-scale=1.0"/>
<title>picamera2 MJPEG streaming demo</title>
<style>
    * {
        box-sizing: border-box;
        margin: 0;
    }
        
    body {
        width: 100vw;
        height: 100vh;
        display: flex;
        justify-content: top;
        align-items: center;
        flex-direction: column;
        position: absolute;
        object-fit: cover;
        background-color: #ffffff;
    }
    
    .box {
        width: 400px;
        height: 280px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 25px;
        position: relative;
        margin-top: 10px;
        overflow: hidden;
        box-shadow: rgba(0, 0, 0, 0.5) 0px 10px 20px;
    }
    
    
</style>
</head>
<body>

<div class="box">
    <img src="stream.mjpg" width="400" height="280" />
</div>
<!--
<form action="/capture">
    <button type="submit">Capture</button>
    -->
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client  %s: %s',
                    self.client_address, str(e))
        # elif self.path == '/capture':
            # self.send_response(200)
            # self.send_header('Content-type', 'text/plain')
            # self.end_headers()
            # try:
                # capture_frsame()
                # self.wfile.write(b'Capture successful')
            # except Exception as e:
                # logging.warning('Error capturing frame: %s', str(e))
                # self.wfile.write(b'Error capturing frame')
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    
    
# def capture_frame():
    # if output.frame is None:
        # raise Exception('No frame aval')
    # capture_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # with open(f'capture_{capture_time}.jpg', 'wb') as file:
        # file.write(output.frame)


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (400, 280)}))
# picam2.framerate = 30
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
