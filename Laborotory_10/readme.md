# Отчет по лабораторной работе № 10

#### Был создан главный файл app.py

```from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('makeimage.html')

@app.route('/login')
def login():
    return jsonify({"author": "1147335"})

@app.route('/makeimage', methods=['POST'])
def make_image():
    width = request.form.get('width')
    height = request.form.get('height')
    text = request.form.get('text')

    # Проверяем корректность параметров изображения
    if not width.isdigit() or not height.isdigit() or int(width) <= 0 or int(height) <= 0:
        return render_template('makeimage.html', message="Invalid image size")

    width, height = int(width), int(height)

    image = Image.new('RGB', (width, height), color=(0, 0, 255, 255))
    draw = ImageDraw.Draw(image)

    # Используем стандартный шрифт
    font = ImageFont.load_default()
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    encoded_img = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    # Возвращаем HTML
    return render_template('display_image.html', image_data=encoded_img)

if __name__ == '__main__':
    app.run(debug=True)
```

#### Был создан файл makeimage.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Make Image</title>
    <script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
</head>
<body>
    <div id="app">
        <h1>Create Image</h1>
        <p v-if="message" style="color: red;">{{ message }}</p>
        <form @submit.prevent="generateImage">
            <label for="width">Width:</label>
            <input type="text" v-model="width" id="width" required>
            <br>
            <label for="height">Height:</label>
            <input type="text" v-model="height" id="height" required>
            <br>
            <label for="text">Text:</label>
            <input type="text" v-model="text" id="text" required>
            <br>
            <input type="submit" value="Generate Image">
        </form>
        <div v-if="imageData">
            <h2>Generated Image</h2>
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
                message: null
            },
            methods: {
                async generateImage() {
                    this.message = null; // Сброс сообщения об ошибке
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

                    const data = await response.text();
                    const parser = new DOMParser();
                    const htmlDoc = parser.parseFromString(data, 'text/html');

                    const imgElement = htmlDoc.querySelector('img');

                    if (imgElement) {
                        this.imageData = imgElement.src; // Устанавливаем источник изображения
                    } else {
                        // Обрабатываем сообщение об ошибке
                        this.message = htmlDoc.querySelector('p').textContent;
                        this.imageData = null; // Сбрасываем изображение
                    }
                }
            }
        });
    </script>
</body>
</html>
```

#### И файл display_image.html

```
<!-- templates/display_image.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Display</title>
</head>
<body>
    <h1>Generated Image</h1>
    <img src="data:image/jpeg;base64,{{ image_data }}" alt="Generated Image">
    <br>
    <a href="/">Back</a>
</body>
</html>
```
