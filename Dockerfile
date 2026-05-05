# 使用官方 Python 镜像作为基础
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存 layer
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码（排除由 .dockerignore 控制的文件）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]