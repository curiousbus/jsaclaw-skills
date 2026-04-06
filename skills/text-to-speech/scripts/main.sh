#!/bin/bash
set -euo pipefail

# 1. 解析输入参数
TEXT=$(echo "$SKILL_INPUT" | jq -r '.text')
VOICE=$(echo "$SKILL_INPUT" | jq -r '.voice // "nova"')

# 2. 调用 OpenAI TTS API
OUTPUT_FILE="/tmp/speech.mp3"

curl -s -X POST "https://api.openai.com/v1/audio/speech" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg model "tts-1" \
    --arg input "$TEXT" \
    --arg voice "$VOICE" \
    '{model: $model, input: $input, voice: $voice}')" \
  -o "$OUTPUT_FILE"

echo "Audio generated: $(stat -c%s "$OUTPUT_FILE" 2>/dev/null || stat -f%z "$OUTPUT_FILE") bytes"

# 3. 上传结果
bash "${GITHUB_WORKSPACE}/lib/common/upload-result.sh" "$OUTPUT_FILE"
