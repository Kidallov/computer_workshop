# Отчет по лабораторной работе № 10


## Структура проекта:
```
Лабораторная_работа_10/
├── app.py
├── static/
│   ├── styles/
│       └── makeimage.css
│       └── result.css
├── templates/
│   └── makeimage.html
│   └── result.html
│   └── hello_user.html
```

## Главные файлы проекта

#### Главный файл `app.py`

```
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('hello_user.html')

@app.route('/login')
def login():
    return jsonify({"author": "1147335"})

@app.route('/makeimage', methods=['POST', 'GET'])
def make_image():
    if request.method == "GET":
        return render_template('makeimage.html')

    width = request.form.get('width')
    height = request.form.get('height')
    text = request.form.get('text')

    if not width.isdigit() or not height.isdigit() or int(width) <= 0 or int(height) <= 0:
        return jsonify({'error': 'Invalid image size'}), 400

    width, height = int(width), int(height)

    image = Image.new('RGB', (width, height), color=(0, 0, 255))
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    encoded_img = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    return jsonify({'image': encoded_img})

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### Комментарии к файлу `app.py`:

```
@app.route('/')                               |
def home():                                   | корневой маршрут, в котором возвращается страница для приветстования пользователя
    return render_template('hello_user.html') |
```

```
@app.route('/login')                      |
def login():                              | маршрут, по которому отображается мой логин в системе Moodle
    return jsonify({"author": "1147335"}) |
```

```
    width = request.form.get('width')    |
    height = request.form.get('height')  | поля, которые работают с нашими значениями
    text = request.form.get('text')      |
```

```
    if not width.isdigit() or not height.isdigit() or int(width) <= 0 or int(height) <= 0: | проверяем на корректность данных и в
        return jsonify({'error': 'Invalid image size'}), 400                               | случае ошибки возвращаем об этом сообщение
```

```
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG') | перевод изображения в байты и сохранение в формате JPEG, а также перевод указателя в начале для последуещего чтения
    img_bytes.seek(0)
```

```
    encoded_img = base64.b64encode(img_bytes.getvalue()).decode('utf-8') | кодирует байтовые данные и и записывается результат в эту переменную
```

```
@app.route('/result')                       |
def result():                               |  по этому пути мы получаем изображение (на новой странице, как сказано в задании)
    return render_template('result.html')   |
```

```
if __name__ == '__main__':   | запускаем наш проект и 
    app.run(debug=True)      | смотрим с помощью отладки где ошибки, если они появляются
```

#### Файл `makeimage.html`

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Создание изображения</title>
    <script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles/makeimage.css') }}">
</head>
<body>
    <div id="app">
        <h1>Создание изображения</h1>
        <form @submit.prevent="generateImage">
            <label for="width">Ширина изображения:</label>
            <input type="text" v-model="width" id="width" required>
            <br>
            <label for="height">Высота изображения:</label>
            <input type="text" v-model="height" id="height" required>
            <br>
            <label for="text">Текст на изображении:</label>
            <input type="text" v-model="text" id="text" required>
            <br>
            <input type="submit" value="Generate Image">
        </form>
        <p v-if="message" style="color: red;">Invalid image size</p>
        <div v-if="imageData">
            <h2>Создать</h2>
            <img :src="imageData" alt="Generated Image">
        </div>
    </div>

    <script>
    new Vue({
        el: '#app',
        data: {
            width: '',
            height: '',
            text: '',
            imageData: null,
            message: false
        },
        methods: {
            async generateImage() {
                const response = await fetch('/makeimage', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        width: this.width,
                        height: this.height,
                        text: this.text
                    })
                });

                if (!response.ok) {
                    this.message = true;
                    return;
                }

                const data = await response.json();
                this.message = false;
                sessionStorage.setItem('imageData', data.image);
                window.location.href = '/result';
            }
        }
    });
</script>
</body>
</html>
```

### Комментарии по файлу `makeimage.html`

```
<script src="https://cdn.jsdelivr.net/npm/vue@2"></script> | испорт фреймоврка Vue
```

```
<link rel="stylesheet" href="{{ url_for('static', filename='styles/makeimage.css') }}"> | подключаем css стили
```

```
el: '#app', | работает с элементом `app`
        data: | в этом месте отображаются данные, которые мы заносим
methods: | вызываем метод

if (!response.ok) {
    this.message = true;
    return;
} | если ошибка, то переводим флаг переменной message в true и отображаем сообщение
```


#### Файл `result.html`

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Созданное изображение</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles/result.css') }}">
</head>
<body>
    <h1>Созданное изображение</h1>
    <img id="result-image" alt="Generated Image">
    <br>
    <a href="/">Вернуться на главный экран</a>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const data = sessionStorage.getItem('imageData');
            if (data) {
                document.getElementById('result-image').src = 'data:image/jpeg;base64,' + data;
            } else {
                document.body.innerHTML = '<p style="color: red;">Данные изображения не найдены. Пожалуйста, сначала создайте изображение.</p><a href="/">Вернуться на главный экран</a>';
            }
        });
    </script>
</body>
</html>
```

### Комментарии к `result.html`

```
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const data = sessionStorage.getItem('imageData'); | считывает сохраненное изображение, которое мы сохранили в файле `makeimage.html`
            if (data) {
                document.getElementById('result-image').src = 'data:image/jpeg;base64,' + data; | загружаем данные
            } else {
                document.body.innerHTML = '<p style="color: red;">Данные изображения не найдены. Пожалуйста, сначала создайте изображение.</p><a href="/">Вернуться на главный экран</a>'; | если данных нет, выводим сообщение
            }
        });
    </script>
```

## CSS стили для каждого файла

### `makeimage.css`

```
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    padding-top: 40px;
}

#app {
    background-color: #ffffff;
    padding: 30px 40px;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    max-width: 480px;
    width: 100%;
}

h1 {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 25px;
    font-size: 28px;
}

form {
    display: flex;
    flex-direction: column;
}

label {
    margin-bottom: 6px;
    color: #2c3e50;
    font-weight: 600;
}

input[type="text"] {
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
}

input[type="submit"] {
    background-color: #2c3e50;
    color: white;
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

input[type="submit"]:hover {
    background-color: #1a252f;
}

p {
    margin-bottom: 15px;
    text-align: center;
}

img {
    margin-top: 20px;
    max-width: 100%;
    border-radius: 10px;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

h2 {
    text-align: center;
    color: #34495e;
}
```

### `result.css`

```
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f9f9f9;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    justify-content: center;
}

h1 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 32px;
    text-align: center;
}

#result-image {
    max-width: 90%;
    max-height: 70vh;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

a {
    display: inline-block;
    padding: 10px 20px;
    background-color: #2c3e50;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
    transition: background-color 0.3s ease;
}

a:hover {
    background-color: #1a252f;
}

p {
    color: red;
    font-size: 18px;
    margin-bottom: 20px;
    text-align: center;
}
```


## Комментарии по всей лабораторной работе

1. Я не стал создавать отдельные `JS` файлы для каждого `.html` файла, хотя было бы правильным сделать именно так, но тут код на пару строк, поэтому можно обойтись таким способом.
2. Для файла `hello_user.html` я не создал отдельный `.css` файл, потому что там код маленьким и не требует отдельного файла, как другие `.html` файлы.
3. Была реализована задача вывода логина ` Формат ответа по маршруту /login {"author": "__ваш логин__"} `
4. Была реализована задача ` Если переданы неверные параметры размеров изображения, возвращать сообщение в переменной message "Invalid image size" на ту же самую страницу makeimage.html снова с формой для генерации картинки. ` с переводом флагов true и false.
5. Была реализована задача `Вывод и отображение самого изображения на страницу с формой (без перезагрузки страницы, асинхронно) или другую страницу как thumbnail.`
6. Была реализована задача `Реализация фронтэнда и отправка данных на сервер с использованием какого-либо фронтэнд-фреймворка.` с помощью Vue.


