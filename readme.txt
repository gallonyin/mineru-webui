
# 环境
conda activate MinerU

# 切换cpu 32G RAM、 cuda 8G VRAM
vim /export/llmuser/magic-pdf.json

# 测试
magic-pdf -p small_ocr.pdf -o ./output

# 启动服务
python mineru_api.py
or
./start.sh
