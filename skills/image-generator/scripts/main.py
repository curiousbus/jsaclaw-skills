import json
import os
import subprocess
import sys
import urllib.request

# 1. 读取输入参数
skill_input = json.loads(os.environ["SKILL_INPUT"])
prompt = skill_input["prompt"]
style = skill_input.get("style", "vivid")
size = skill_input.get("size", "1024x1024")

# 2. 调用外部 API 生成图片
api_key = os.environ["OPENAI_API_KEY"]

request_body = json.dumps({
    "model": "dall-e-3",
    "prompt": prompt,
    "size": size,
    "style": style,
    "n": 1,
}).encode()

req = urllib.request.Request(
    "https://api.openai.com/v1/images/generations",
    data=request_body,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read())

image_url = result["data"][0]["url"]

# 3. 下载生成的图片
output_path = "/tmp/generated-image.png"
urllib.request.urlretrieve(image_url, output_path)

# 4. 上传结果到 R2
subprocess.run(
    ["bash", f"{os.environ['GITHUB_WORKSPACE']}/lib/common/upload-result.sh", output_path],
    check=True,
)

print(f"Image generated and uploaded: {prompt}")
