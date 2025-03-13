from flask import Flask, request, render_template, send_from_directory
import json
import os

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/submit', methods=['POST'])
def submit():
    moodle_login = request.form.get('moodle_login')
    current_time = request.form.get('current_time')

    if not moodle_login or not current_time:
        return '<h3>Ошибка: данные не могут быть пустыми!</h3>'

    data = {
        'moodle_login': moodle_login,
        'current_time': current_time
    }

    existing_data = []

    if os.path.exists('data.json'):
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            return '<h3>Ошибка, файл данных поврежден. Создан новый файл.</h3>'

    existing_data.append(data)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

    return '<h3>Данные успешно сохранены!</h3>'


if __name__ == '__main__':
    app.run(debug=True)