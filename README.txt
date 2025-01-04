

# ⚠️注意
1. 使用本项目前，请确保你已经按照官方文档安装了 MinerU 和 CUDA 加速，并可以通过命令行运行 mineru 命令（如 “magic-pdf -p small_ocr.pdf -o ./output”）
2. 本项目完全依赖官方项目，为社区提供封装简化的API和可视化操作，方便部署在Linux环境持续提供服务。

# MinerU 官方文档
https://github.com/opendatalab/MinerU/blob/master/docs/README_Ubuntu_CUDA_Acceleration_en_US.md

请确保可以在自己的服务器上正常运行 mineru 命令，并能得到正确的文件输出。

# 官方提供了 pdf转md 的使用方法 （Local File Example）
[https://mineru.readthedocs.io/en/latest/user_guide/quick_start/to_markdown.html](https://mineru.readthedocs.io/en/latest/user_guide/quick_start/to_markdown.html)，我们在此基础上，添加了 异步任务， 并使用 fastapi 提供了相关 api 接口。


# 使用方法

1. 安装依赖(不含MinerU主项目依赖，可直接在自己的MinerU虚拟环境上继续安装)
pip install -r requirements.txt

2. 运行 mineru_api.py
python mineru_api.py
    -  指定端口
    python mineru_api.py --port 8001

3. 访问 http://0.0.0.0:8001/upload 上传 pdf 文件

4. 访问 http://0.0.0.0:8001/task/task_id 查看任务状态

5. 访问 http://0.0.0.0:8001/docs 查看 api 文档


QA
1. 根据官方描述 cpu运行推荐32G RAM，cuda运行推荐8G VRAM

