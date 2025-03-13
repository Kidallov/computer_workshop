from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/')
def do_get():
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz).strftime('%d.%m.%y %H:%M:%S')

    user_login = "1147335"

    return f'{user_login}, {current_time}'

if __name__ == '__main__':
    app.run('localhost', 8080)
