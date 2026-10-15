"""端到端集成测试：真实调用运行中的前端服务（前端背后是容器化的后端）。

由 integration.yml 工作流启动服务后执行，不在普通 push CI 中运行。
"""
import os

import httpx

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:8011")


def test_health():
    resp = httpx.get(f"{FRONTEND_URL}/health", timeout=5)
    assert resp.status_code == 200


def test_e2e_ask_hits_real_backend():
    resp = httpx.get(f"{FRONTEND_URL}/ask", params={"name": "ci"}, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    # from == backend 说明请求真正穿透到了后端服务（而不是降级提示）
    assert data["from"] == "backend"
    assert "Hello, ci!" in data["message"]
