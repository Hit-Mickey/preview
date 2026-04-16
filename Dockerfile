# 1. 使用极致精简的 Python Alpine 镜像
FROM python:3.11-alpine

# 2. 设置容器内的工作目录
WORKDIR /app

# 3. 将本地的脚本复制到容器中
COPY preview.py .

# 4. 暴露预览服务端口
EXPOSE 6033

# 5. 启动命令
CMD ["python", "preview.py"]