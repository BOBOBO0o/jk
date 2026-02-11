# 使用Python 3.10作为基础镜像
# Build version: 2024-02-11-v3 - Fixed dockerignore
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask flask-cors gunicorn

# 复制项目文件
COPY . .

# 验证文件是否存在
RUN ls -la /app/ && \
    echo "Checking critical files:" && \
    ls -la /app/*.py && \
    test -f /app/cloud_api_server.py || (echo "ERROR: cloud_api_server.py missing!" && exit 1)

# 创建数据目录
RUN mkdir -p /app/data

# 暴露API端口
EXPOSE 5001

# 设置PYTHONPATH
ENV PYTHONPATH=/app
ENV FLASK_APP=cloud_api_server.py

# 启动命令（使用Flask内置服务器）
CMD ["python", "-c", "from cloud_api_server import app; app.run(host='0.0.0.0', port=5001, debug=False)"]
