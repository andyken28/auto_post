from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

INDEX_HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Ứng dụng Python đơn giản</title></head>
<body>
<h1>Ứng dụng Python đơn giản</h1>
<p>Chạy trên cổng 8080</p>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
