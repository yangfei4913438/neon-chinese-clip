## 说明

一个基于本地部署实现的多模态向量生成服务。

注意：本项目仅用于安全环境下的多模态(图像+文本)向量生成，如果要部署在开放的公网环境，请务必增加安全校验代码，防止被恶意调用。

## 模型依赖

需要到 下载模型的 pt 文件到项目的目录(`models/pretrained_weights`)下：

- https://huggingface.co/OFA-Sys/chinese-clip-rn50
- https://huggingface.co/OFA-Sys/chinese-clip-vit-base-patch16
- https://huggingface.co/OFA-Sys/chinese-clip-vit-large-patch14
- https://huggingface.co/OFA-Sys/chinese-clip-vit-large-patch14-336px
- https://huggingface.co/OFA-Sys/chinese-clip-vit-huge-patch14

或者下面的地址

- https://www.modelscope.cn/models/AI-ModelScope/chinese-clip-rn50
- https://www.modelscope.cn/models/AI-ModelScope/chinese-clip-vit-base-patch16
- https://www.modelscope.cn/models/AI-ModelScope/chinese-clip-vit-large-patch14
- https://www.modelscope.cn/models/AI-ModelScope/chinese-clip-vit-large-patch14-336px
- https://www.modelscope.cn/models/AI-ModelScope/chinese-clip-vit-huge-patch14

没有这几个模型 pt 文件，切换对应模型的时候，会导致项目运行异常。

> 注意：下载的文件，不要修改文件名。否则可能会导致文件无法被识别！！！

目前对应的名称分别是：
- clip_cn_rn50.pt
- clip_cn_vit-b-16.pt
- clip_cn_vit-l-14.pt
- clip_cn_vit-l-14-336.pt
- clip_cn_vit-h-14.pt

## 开发环境的项目启动

执行 ./dev.sh 即可

## 构建

> 构建之前确定已经下载好上面提及的模型文件，并放置到对应目录下。打包之后，模型文件会被包含进去。

```shell
docker build -t clip-service:latest .
```

## 启动容器

> 启动容器，映射 7001 端口

```shell
docker run -d -p 7001:7001 --name clip-service clip-service:latest
```

## 访问接口文档

http://localhost:7001/redoc

或者

http://localhost:7001/docs

## 导出镜像

> 导出为 tar.gz 文件, 方便传输部署

```shell
docker save clip-service:latest | gzip > clip-service.tar.gz
```

- 发送到远程服务器(rsync大文件更稳定)

```shell
rsync -avzP clip-service.tar.gz user@deploy-server:/tmp/
```

## 导入镜像

> 导入 tar.gz 文件

```shell
gunzip -c clip-service.tar.gz | docker load
```

其他就是正常的 docker 操作了。
