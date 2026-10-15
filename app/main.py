import os

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8010")

app = FastAPI(title="demo-frontend")

PAGE = """
<html>
  <body style="font-family: sans-serif; text-align: center; padding-top: 60px;">
    <h1>Demo Frontend</h1>
    <p>在下面输入名字，点击按钮，浏览器会请求前端服务，前端服务再调用后端：</p>
    <input id="name" placeholder="你的名字" style="padding: 8px; font-size: 16px;">
    <button onclick="ask()" style="padding: 8px 16px; font-size: 16px;">调用后端</button>
    <h2 id="result" style="color: #007a3d;"></h2>
    <script>
      async function ask() {
        const name = document.getElementById('name').value || 'world';
        const result = document.getElementById('result');
        result.textContent = '请求中...';
        const resp = await fetch('/ask?name=' + encodeURIComponent(name));
        const data = await resp.json();
        result.textContent = data.message + '  [来源: ' + (data.from || 'unknown') + ']';
        result.style.color = data.from === 'backend' ? '#007a3d' : 'red';
      }
    </script>
  </body>
</html>
"""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    return PAGE


@app.get("/ask")
def ask(name: str = "world", times: int = 1):
    try:
        resp = httpx.post(
            f"{BACKEND_URL}/api/greet",
            json={"name": name, "times": times},
            timeout=3,
        )
        return resp.json()
    except Exception:
        return {"message": "backend service unavailable", "from": "frontend"}
