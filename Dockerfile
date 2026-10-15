# 前端服务的容器镜像定义（和后端 Dockerfile 同构，便于对照理解）
# 前端虽然是"服务端渲染"角色，部署形态和后端完全一样：一个 Web 服务镜像

FROM python:3.11-slim

WORKDIR /app

# 先装依赖再拷代码，利用镜像层缓存（同后端 Dockerfile 的技巧）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8010

# 注意：容器内统一监听 8010，对外映射成什么端口由 docker-compose 决定。
# 前端启动后调哪个后端，由环境变量 BACKEND_URL 决定（compose 里注入 http://backend:8010）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
