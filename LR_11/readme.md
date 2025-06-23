# Отчет по лабораторной работе № 11


## Структура проекта:
```
Лабораторная_работа_11/
├── app.py
├── templates/
│   └── decypher.html
│   └── encrypt.html
```

#### Главный файл `app.py`

```
from flask import Flask, jsonify, request, render_template, send_file
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from io import BytesIO

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

@app.route('/decypher')
def decypher_page():
    return render_template('decypher.html')

@app.route('/encrypt')
def encrypt_page():
    return render_template('encrypt.html')

@app.route('/login')
def login():
    return jsonify({"author": "1147335"})

@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return jsonify({
        "private_key": private_pem.decode('utf-8'),
        "public_key": public_pem.decode('utf-8')
    })

@app.route('/encrypt_message', methods=['POST'])
def encrypt_message():
    data = request.get_json()
    public_key_str = data.get('public_key')
    message = data.get('message')

    if not public_key_str or not message:
        return jsonify({"error": "Both public key and message are required"}), 400

    try:
        public_key = serialization.load_pem_public_key(public_key_str.encode('utf-8'))

        encrypted = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        return send_file(BytesIO(encrypted), mimetype='application/octet-stream', as_attachment=True, download_name='secret.bin')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/decypher', methods=['POST'])
def decypher():
    if 'key' not in request.files or 'secret' not in request.files:
        return jsonify({"error": "Both key and secret fields are required"}), 400

    key_file = request.files['key']
    secret_file = request.files['secret']

    try:
        private_key_data = key_file.read()
        private_key = serialization.load_pem_private_key(private_key_data, password=None)

        encrypted_data = secret_file.read()

        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        return decrypted.decode('utf-8'), 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```
#### Комментарии к `app.py`

Этот файл отвечает за серверную логику приложения.

``` /decypher (GET) — загрузка HTML-страницы для расшифровки. ```

``` /encrypt (GET) — загрузка HTML-страницы для шифрования и генерации ключей. ```

``` /login (GET) — возвращает JSON с автором работы ({"author": "1147335"}). ```

``` /generate_keys (POST) — генерирует новую пару RSA-ключей (2048 бит) и возвращает их в формате PEM. ```

``` /encrypt_message (POST) — шифрует сообщение с использованием переданного открытого ключа и возвращает зашифрованный бинарный файл. ```

``` /decypher (POST) — принимает приватный ключ и зашифрованный файл в формате multipart/form-data, расшифровывает содержимое и возвращает текст. ```

#### Файл `decypher.html`

```
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Расшифровка</title>
</head>
<body>
  <h1>Расшифровка с помощью приватного ключа</h1>

  <form id="decypher-form">
    <label>Приватный ключ (key):</label><br>
    <input type="file" name="key" required><br><br>

    <label>Зашифрованный файл (secret):</label><br>
    <input type="file" name="secret" required><br><br>

    <button type="submit">Расшифровать</button>
  </form>

  <div class="result" id="result"></div>

  <script>
    const form = document.getElementById('decypher-form');
    const resultDiv = document.getElementById('result');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(form);
      resultDiv.textContent = 'Расшифровка...';

      try {
        const response = await fetch('/decypher', {
          method: 'POST',
          body: formData
        });

        const text = await response.text();
        resultDiv.textContent = text;
      } catch (err) {
        resultDiv.textContent = 'Ошибка: ' + err.message;
      }
    });
  </script>
</body>
</html>

```
#### Комментарии к `decypher.html`

Фронтенд-страница для расшифровки:

    Позволяет загрузить приватный ключ и зашифрованный файл через форму.

    Отправка формы происходит асинхронно с помощью fetch API без перезагрузки страницы.

    После расшифровки текст отображается сразу в <div> на той же странице.


#### Файл `encrypt.html`

```
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Генерация и шифрование</title>
</head>
<body>
  <h1>Генерация ключей</h1>
  <button onclick="generateKeys()">Сгенерировать</button>

  <h3>Приватный ключ</h3>
  <textarea id="private"></textarea>
  <h3>Публичный ключ</h3>
  <textarea id="public"></textarea>

  <h1>Шифрование сообщения</h1>
  <textarea id="message" placeholder="Введите сообщение..."></textarea><br>
  <button onclick="encrypt()">Зашифровать и скачать</button>

  <div class="result" id="result"></div>

  <script>
    async function generateKeys() {
      const response = await fetch('/generate_keys', { method: 'POST' });
      const data = await response.json();
      document.getElementById('private').value = data.private_key;
      document.getElementById('public').value = data.public_key;
    }

    async function encrypt() {
      const message = document.getElementById('message').value;
      const publicKey = document.getElementById('public').value;

      const response = await fetch('/encrypt_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ public_key: publicKey, message: message })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'secret.bin';
        a.click();
      } else {
        const error = await response.json();
        document.getElementById('result').textContent = error.error || 'Ошибка шифрования';
      }
    }
  </script>
</body>
</html>

```

#### Комментарии к `encrypt.html`

Фронтенд-страница для:

    Генерации пары ключей RSA.

    Отправки открытого ключа и текста для шифрования.

    Загрузки зашифрованного файла на клиент.

Реализовано:

    Генерация и шифрование происходят через кнопки и текстовые поля.

    После успешного шифрования происходит автоматическая загрузка зашифрованного файла.
    

## Комментарии по всей лабораторной работе

Все обязательные требования из задания выполнены:

    1. Реализация на Flask

    2. Маршрут /login возвращает JSON с автором

    3. Маршрут /decypher принимает данные в формате multipart/form-data и корректно обрабатывает

    4. Асинхронная отправка формы без перезагрузки страницы

    5. Отображение результата расшифровки на странице



