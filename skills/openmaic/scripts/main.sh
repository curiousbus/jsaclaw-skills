#!/bin/bash
# OpenMAIC 课程生成脚本
# 用法: ./generate-course.sh "学习主题" [语言]

OPENMAIC_URL="${OPENMAIC_URL:-https://edu.openpm.im}"
TOPIC="$1"
LANGUAGE="${2:-zh}"

if [ -z "$TOPIC" ]; then
    echo "用法: $0 \"学习主题\" [语言]"
    echo "示例: $0 \"Python 基础入门\" zh"
    exit 1
fi

echo "📚 正在生成课程: $TOPIC"
echo "🌐 服务地址: $OPENMAIC_URL"
echo ""

# 提交生成任务
RESPONSE=$(curl -s -X POST "$OPENMAIC_URL/api/generate-classroom" \
    -H "Content-Type: application/json" \
    -d "{\"requirement\": \"$TOPIC\", \"language\": \"$LANGUAGE\"}")

JOB_ID=$(echo "$RESPONSE" | jq -r '.data.jobId // empty')
POLL_URL=$(echo "$RESPONSE" | jq -r '.data.pollUrl // empty')

if [ -z "$JOB_ID" ]; then
    echo "❌ 提交失败"
    echo "$RESPONSE" | jq .
    exit 1
fi

echo "✅ 任务已提交，Job ID: $JOB_ID"
echo "⏳ 正在生成课程，请稍候..."
echo ""

# 轮询等待完成
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))
    
    STATUS=$(curl -s "$POLL_URL")
    JOB_STATUS=$(echo "$STATUS" | jq -r '.data.status')
    STEP=$(echo "$STATUS" | jq -r '.data.step // "处理中"')
    PROGRESS=$(echo "$STATUS" | jq -r '.data.progress // 0')
    MESSAGE=$(echo "$STATUS" | jq -r '.data.message // ""')
    
    echo "[$ATTEMPT/$MAX_ATTEMPTS] $STEP - $MESSAGE ($PROGRESS%)"
    
    if [ "$JOB_STATUS" = "succeeded" ]; then
        CLASSROOM_ID=$(echo "$STATUS" | jq -r '.data.result.classroomId // empty')
        echo ""
        echo "🎉 课程生成完成！"
        echo ""
        if [ -n "$CLASSROOM_ID" ]; then
            echo "📖 课程链接: $OPENMAIC_URL/classroom/$CLASSROOM_ID"
        else
            echo "📖 请访问: $OPENMAIC_URL"
        fi
        exit 0
    elif [ "$JOB_STATUS" = "failed" ]; then
        echo ""
        echo "❌ 课程生成失败"
        echo "$STATUS" | jq .
        exit 1
    fi
done

echo ""
echo "⏰ 超时，请稍后访问: $OPENMAIC_URL"
