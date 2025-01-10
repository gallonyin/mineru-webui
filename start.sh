#!/bin/bash

# 定义变量
SCRIPT_NAME="mineru_api.py"
CONDA_ENV="MinerU"  # conda 环境名称

# 记录时间
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始重启服务..."

# 初始化 conda
source /export/llmuser/anaconda3/etc/profile.d/conda.sh  # 替换为你的 conda.sh 路径

# 激活 conda 环境
echo "正在激活 conda 环境: $CONDA_ENV"
conda activate $CONDA_ENV

# 检查 conda 环境是否成功激活
if [ $? -ne 0 ]; then
    echo "conda 环境激活失败！"
    echo "重启失败：conda 环境激活错误"
    exit 1
fi

# 查找并终止旧进程
OLD_PID=$(ps -ef | grep "$SCRIPT_NAME" | grep -v grep | awk '{print $2}')
if [ ! -z "$OLD_PID" ]; then
    echo "正在终止旧进程 PID: $OLD_PID"
    kill -9 $OLD_PID
    sleep 2
fi

# 启动新进程
echo "正在启动新进程..."
nohup python $SCRIPT_NAME &
NEW_PID=$!

# 检查是否成功启动
sleep 2
if ps -p $NEW_PID > /dev/null; then
    echo "服务成功重启，新 PID: $NEW_PID"
    echo "重启成功！"
else
    echo "服务启动失败！"
    echo "重启失败！"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - 重启完成"

# 退出 conda 环境（可选）
conda deactivate
