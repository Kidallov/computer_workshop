import http.server
import urllib.parse
import json

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Отправляем HTML-форму, если это GET-запрос
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("form.html", "r", encoding="utf-8") as file:
                self.wfile.write(file.read().encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/submit":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            post_data = urllib.parse.parse_qs(post_data.decode())

            name = post_data.get('name', [''])[0]
            email = post_data.get('email', [''])[0]

            with open("data.txt", "a", encoding="utf-8") as file:
                file.write(f"Имя: {name}, Электронная почта: {email}\n")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>All Good!</h1></body></html>".encode('utf-8'))


if __name__ == "__main__":
    server_address = ('localhost', 8080)
    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Запуск сервера на порту 8080...")
    httpd.serve_forever()
