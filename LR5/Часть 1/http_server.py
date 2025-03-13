from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import pytz

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        moscow_tz = pytz.timezone('Europe/Moscow')
        current_time = datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M:%S')

        user_login = "1147335"

        result = f'{user_login}, {current_time}'

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(result, "utf-8"))

httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
print('Server is running')
httpd.serve_forever()
