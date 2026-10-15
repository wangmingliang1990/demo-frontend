import os

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# 后端服务地址：本地调试默认 8010；CI 集成测试时会用环境变量指向容器化的后端
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8010")

app = FastAPI(title="demo-frontend")

# 前端页面：输入框 + 按钮。点按钮触发浏览器 fetch('/ask?name=...')，
# 结果不刷新页面、直接显示在 #result 里
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


# 转发接口：前端的"客户端时刻"——收到浏览器请求后，用 httpx 去调后端 /api/greet
# 调通了：原样返回后端 JSON（含 from=backend）
# 调不通：返回 from=frontend 的降级提示，页面会显示红色
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
