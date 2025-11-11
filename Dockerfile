# 使用python3.12.6-slim镜像
FROM python:3.12.6-slim AS builder

# 配置系统加速
RUN rm -rf /etc/apt/sources.list.d/* && \
    # 创建主源文件
    cat > /etc/apt/sources.list <<EOFA
deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free
deb http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free
deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free
EOFA

# 创建备用源文件
RUN cat > /etc/apt/sources.list.d/backup.list <<EOFB
deb https://repo.huaweicloud.com/debian/ bookworm main contrib non-free
deb https://repo.huaweicloud.com/debian/ bookworm-updates main contrib non-free
deb https://repo.huaweicloud.com/debian-security bookworm-security main contrib non-free
EOFB

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git curl wget \
    # 编译相关工具
    build-essential gcc g++ make

# pip 配置系统加速
RUN mkdir -p /root/.pip && \
    cat > /root/.pip/pip.conf <<EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
EOF

# 安装 uv（使用 pip 安装）
RUN pip install --no-cache-dir uv

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV UV_NO_VENV=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
ENV UV_PYTHON="/usr/local/bin/python"

# 先复制依赖配置文件，利用 Docker 缓存
COPY pyproject.toml uv.lock .

# 创建一个空的 README.md 文件以满足构建要求
RUN touch README.md

# 安装生产依赖（非开发依赖，根据锁文件安装）
RUN uv sync --no-dev --frozen

# 再复制项目代码
COPY . .

# 确保模型目录存在
RUN mkdir -p models/pretrained_weights

# 清理缓存
RUN uv cache clean

# 运行时阶段
FROM python:3.12.6-slim AS runtime

# 配置系统加速
RUN rm -rf /etc/apt/sources.list.d/* && \
    # 创建主源文件
    cat > /etc/apt/sources.list <<EOFA
deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free
deb http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free
deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free
EOFA

# 创建备用源文件
RUN cat > /etc/apt/sources.list.d/backup.list <<EOFB
deb https://repo.huaweicloud.com/debian/ bookworm main contrib non-free
deb https://repo.huaweicloud.com/debian/ bookworm-updates main contrib non-free
deb https://repo.huaweicloud.com/debian-security bookworm-security main contrib non-free
EOFB

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    # JPEG图像支持
    libjpeg62-turbo \
    # PNG图像支持
    libpng16-16 \
    # 支持 WebP 图像格式
    libwebp7 \
    # PyTorch 多线程计算依赖
    libgomp1 \
    # 清理缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

WORKDIR /app

# 设置环境变量
ENV UV_NO_VENV=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
ENV UV_PYTHON="/usr/local/bin/python"

# 添加常用别名
RUN echo 'alias ll="ls -la"' >> /root/.bashrc

# 暴露应用端口
EXPOSE 7001

# 设置默认命令，使用 uv 运行 gunicorn 启动应用
CMD ["uv", "run", "gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
