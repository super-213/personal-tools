#!/bin/bash

# check_hires.sh
# Usage: ./check_hires.sh /path/to/audio.flac

FILE="$1"

if [[ -z "$FILE" ]]; then
    echo "用法: $0 <音频文件路径>"
    echo "支持格式: flac, mp3, m4a 等"
    exit 1
fi

if [[ ! -f "$FILE" ]]; then
    echo "错误: 文件不存在 — $FILE"
    exit 2
fi

# 使用 ffprobe 获取采样率（单位：Hz），仅取第一个音频流
SAMPLE_RATE=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 "$FILE" 2>/dev/null)

if [[ -z "$SAMPLE_RATE" ]] || [[ "$SAMPLE_RATE" =~ error ]]; then
    echo "错误: 无法解析音频采样率，请确认是有效音频文件。"
    exit 3
fi

# 判断是否为 HI-RES（> 44100 Hz）
if (( SAMPLE_RATE > 44100 )); then
    CATEGORY="HI-RES"
else
    CATEGORY="Standard"
fi

echo "文件: $(basename "$FILE")"
echo "路径: $FILE"
echo "采样率: ${SAMPLE_RATE} Hz ($((SAMPLE_RATE / 1000)) kHz)"
echo "类别: $CATEGORY"