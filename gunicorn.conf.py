#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 01:23
@Author : YangFei
@File   : gunicorn.conf.py
@Desc   : 
"""
import multiprocessing

# 服务器绑定地址
bind = "0.0.0.0:7001"

# Chinese-CLIP 内存占用大，建议减少工作进程数
# 默认使用 1-2 个工作进程，避免内存不足
workers = min(multiprocessing.cpu_count(), 2)  # 限制为2个进程

# 工作进程类
worker_class = "uvicorn.workers.UvicornWorker"

# 增加超时时间，因为模型推理可能较慢
timeout = 300
graceful_timeout = 60

# 减少最大请求数，避免内存泄漏
max_requests = 500
max_requests_jitter = 50

# 预加载应用，避免每个进程都加载模型
preload_app = True

# 保持连接时间（秒）
keepalive = 5

# 日志配置
loglevel = "info"
accesslog = "-"  # 标准输出
errorlog = "-"   # 标准输出

# 内存相关配置
worker_tmp_dir = "/dev/shm"  # 使用内存文件系统

# 进程名
proc_name = "neon_chinese_clip"

# 环境变量
raw_env = [
    "OMP_NUM_THREADS=1",  # 限制 OpenMP 线程数
    "MKL_NUM_THREADS=1",  # 限制 MKL 线程数
]