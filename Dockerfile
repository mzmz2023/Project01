# 使用官方 Python 镜像作为基础
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir fastapi uvicorn

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]