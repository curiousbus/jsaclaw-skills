# 图片生成

根据用户的文字描述生成高质量图片。

## 使用场景

当用户要求生成、创作、画一张图片时，使用此 Skill。

## 参数

调用 execute_skill 时传递以下参数：

- **prompt** (必填): 图片的英文描述。如果用户用中文描述，请翻译成英文后传入。
- **style** (可选): 风格，可选值: realistic, anime, sketch, oil-painting。不传则使用默认风格。
- **size** (可选): 图片尺寸，格式 "宽x高"，默认 "1024x1024"。可选: "1024x1024", "1792x1024", "1024x1792"。

## 调用示例

用户说"帮我画一只赛博朋克风格的猫"，你应该：

1. 调用 load_skill("image-generator") 读取本说明
2. 调用 execute_skill("image-generator", { "prompt": "a cyberpunk cat with neon lights", "style": "realistic" })
3. 将生成的图片发送给用户
