#!/usr/bin/python3

import io
import logging
import socketserver
from http import server
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from gpiozero import LED

PAGE = open("index.html").read()

led = LED(17)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

import os

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
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        elif self.path == '/MCXN_logo.png':  # Serve the logo image
            try:
                with open("MCXN_logo.png", "rb") as f:
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404)
        elif self.path == '/autofocus':
            success = picam2.autofocus_cycle()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Autofocus triggered' if success else b'Autofocus failed')
        elif self.path == '/toggle_ir':
            led.toggle()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'IR LED toggled')
        elif self.path == '/temperature':
            try:
                with open("/sys/bus/w1/devices/28-00000d85698f/w1_slave") as f:
                    lines = f.readlines()
                    if lines[0].strip()[-3:] == 'YES':
                        equals_pos = lines[1].find('t=')
                        if equals_pos != -1:
                            temp_string = lines[1][equals_pos+2:]
                            temperature_c = float(temp_string) / 1000.0
                            temperature_f = temperature_c * 9.0 / 5.0 + 32.0
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(bytes(
                                f'{{"temp_c": {temperature_c:.2f}, "temp_f": {temperature_f:.2f}}}',
                                'utf-8'
                            ))
                        else:
                            raise ValueError("Temperature reading not found")
                    else:
                        raise ValueError("CRC check failed")
            except Exception as e:
                logging.warning("Failed to read temperature: %s", str(e))
                self.send_error(500, message=str(e))
        elif self.path == '/focus_near':
            global current_focus
            current_focus = min(1.0, current_focus + 0.05)  # step closer
            picam2.set_controls({"AfMode": 0, "LensPosition": current_focus})
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Focus set closer: {current_focus:.2f}".encode())

        elif self.path == '/focus_far':
            global current_focus
            current_focus = max(0.0, current_focus - 0.05)  # step further
            picam2.set_controls({"AfMode": 0, "LensPosition": current_focus})
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Focus set farther: {current_focus:.2f}".encode())
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
    GPIO.cleanup()
