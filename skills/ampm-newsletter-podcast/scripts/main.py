#!/usr/bin/env python3
"""
双人播客 TTS 生成器 v5
主持人有个性，专家幽默风趣用类比
"""

import json
import uuid
import base64
import requests
import os
import tempfile
import re
import random

TTS_CONFIG = {
    "appid": "7897143711",
    "cluster": "volcano_tts", 
    "token": os.environ['DOUBAO_API_KEY'],
    "female_voice": "zh_female_xiaohe_uranus_bigtts",
    "male_voice": "zh_male_m191_uranus_bigtts",
}

TTS_API_URL = "https://openspeech.bytedance.com/api/v1/tts"


def generate_tts(text: str, voice_type: str, output_path: str) -> bool:
    payload = {
        "app": {
            "appid": TTS_CONFIG["appid"],
            "token": TTS_CONFIG["token"],
            "cluster": TTS_CONFIG["cluster"],
        },
        "user": {"uid": "xiaoxia_podcast"},
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "rate": 24000,
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{TTS_CONFIG['token']}"
    }
    
    try:
        response = requests.post(TTS_API_URL, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get("code") == 3000:
            audio_data = base64.b64decode(result["data"])
            with open(output_path, "wb") as f:
                f.write(audio_data)
            return True
        else:
            print(f"TTS error: {result.get('message')}")
            return False
    except Exception as e:
        print(f"TTS request failed: {e}")
        return False


def parse_news_to_sections(news_text: str) -> dict:
    sections = {
        "headlines": [],
        "hn": [],
        "reddit": [],
        "other": []
    }
    
    current_section = "headlines"
    current_item = None
    
    lines = news_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if '早安' in line or '晚间' in line or '新闻简报' in line or '时效' in line:
            continue
        
        if '头条' in line:
            current_section = "headlines"
            continue
        elif 'Hacker News' in line or line == '💻 Hacker News 热门':
            current_section = "hn"
            continue
        elif 'Reddit' in line and '热议' in line:
            current_section = "reddit"
            continue
        elif '值得关注' in line or '值得' in line:
            current_section = "other"
            continue
        
        if line.startswith('🔹') or line.startswith('•'):
            if current_item:
                sections[current_section].append(current_item)
            
            title = line.replace('🔹', '').replace('•', '').strip()
            title = re.sub(r'\|.*$', '', title).strip()
            
            current_item = {
                "title": title,
                "detail": ""
            }
        elif current_item and not line.startswith('|') and not line.startswith('📊') and not line.startswith('🔗'):
            clean = re.sub(r'[📊🔗📅]', '', line).strip()
            if clean and len(clean) > 5:
                if current_item["detail"]:
                    current_item["detail"] += " " + clean
                else:
                    current_item["detail"] = clean
    
    if current_item:
        sections[current_section].append(current_item)
    
    return sections


def create_dialogue_from_sections(sections: dict) -> list:
    """生成对话脚本 - 主持人有个性，专家幽默用类比"""
    
    dialogue = []
    
    # ===== 开场 =====
    dialogue.append(("female", "今天 AI 圈子有什么大动作？"))
    
    # ===== 头条新闻 =====
    if sections["headlines"]:
        dialogue.append(("male", "最重磅的肯定是 Nvidia GTC 大会，黄仁勋又放大招了。"))
        
        for i, item in enumerate(sections["headlines"]):
            # 专家用类比解释
            if i == 0:  # Vera CPU
                dialogue.append(("male", "Nvidia 发布了自研的 CPU，叫 Vera。"))
                dialogue.append(("male", "你可以把它理解成，Nvidia 以前只卖显卡这种\"肌肉\"，现在连\"大脑\"也自己造了。一台机器，CPU、GPU 全是自家的。"))
                dialogue.append(("female", "等等，Nvidia 自己做 CPU 了？这不是跟 Intel、AMD 抢饭碗吗？"))
                dialogue.append(("male", "对，而且是专门为 AI agent 设计的，就像给赛车专门定制发动机，比通用 CPU 效率高得多。"))
            elif i == 1:  # DGX Station
                dialogue.append(("male", "还有一个叫 DGX Station，相当于把数据中心的主机塞到桌面上。"))
                dialogue.append(("female", "桌面超算听起来很酷，但普通人买得起吗？"))
                dialogue.append(("male", "哈哈，这个不是给普通人用的。就像你不会在家里放个工业级 3D 打印机一样，这是给企业和专业开发者的。价格嘛，六位数起步吧。"))
            elif i == 2:  # Agent 平台
                dialogue.append(("male", "还有个大动作，Nvidia 拉来了 17 家企业巨头，一起做 AI agent 平台。"))
                dialogue.append(("female", "17 家巨头一起站台，Nvidia 这是想成为 AI agent 的基础设施啊。"))
                dialogue.append(("male", "没错，就像当年的 Windows 之于 PC，Nvidia 想成为 AI agent 时代的操作系统。"))
            
        dialogue.append(("female", "Nvidia 这波攻势很猛啊。"))
    
    # ===== Hacker News =====
    if sections["hn"]:
        dialogue.append(("male", "再来看看 Hacker News 上大家在聊什么。"))
        
        for item in sections["hn"]:
            if "Godot" in item["title"]:
                dialogue.append(("male", "有个项目挺火的，用 Claude Code 自动生成 Godot 游戏。"))
                dialogue.append(("male", "就像你跟设计师说\"我要个马里奥风格的游戏\"，它就给你生成出来了。代码、美术、场景，一条龙。"))
                dialogue.append(("female", "用 AI 生成完整游戏？这听起来有点太科幻了吧。"))
                dialogue.append(("male", "已经有 demo 了，效果还行。当然离真正上市的游戏还有距离，但这个方向挺有意思的。"))
            elif "MCP" in item["title"] or "Context" in item["title"]:
                dialogue.append(("male", "还有个讨论热度很高，关于 MCP 吃掉 Context Window 的问题。"))
                dialogue.append(("male", "简单说就是，MCP 这种工具协议太\"胖\"了，光描述工具有哪些功能就要占掉一大半的内存。"))
                dialogue.append(("female", "MCP 消耗那么多 token？这个问题挺严重的啊。"))
                dialogue.append(("male", "对，就像你请个助手，结果他光介绍自己会什么就说了半小时，真正干活的时间反而少了。所以现在有人推 CLI 替代方案。"))
            elif "LLM" in item["title"] or "分布式" in item["title"]:
                dialogue.append(("male", "还有篇论文，把 LLM 团队当成分布式系统来研究。"))
                dialogue.append(("male", "就像管理一个团队，你不能只看个人能力，还要看他们怎么协作、怎么分工。这篇论文就是这个思路。"))
                dialogue.append(("female", "把 LLM 当分布式系统来研究？这个角度挺新颖的。"))
    
    # ===== Reddit =====
    if sections["reddit"]:
        dialogue.append(("male", "Reddit 上今天有个帖子炸了。"))
        
        for item in sections["reddit"]:
            if "吊唁" in item["title"]:
                dialogue.append(("male", "有人用 AI 写吊唁回复，结果被网友狂喷。"))
                dialogue.append(("female", "用 AI 写吊唁？这... 也太没人情味了吧。"))
                dialogue.append(("male", "是啊，就像你朋友失恋了，你发个机器生成的安慰短信，谁看了不生气？有些事情，AI 真的不该插手。"))
    
    # ===== 其他值得关注 =====
    if sections["other"]:
        dialogue.append(("male", "最后还有几个有意思的项目。"))
        items_text = "、".join([item["title"] for item in sections["other"][:3]])
        dialogue.append(("male", f"{items_text}，感兴趣的可以看看。"))
    
    # ===== 结尾 =====
    dialogue.append(("female", "好，今天的 AI 新闻就到这儿。有什么总结？"))
    dialogue.append(("male", "Nvidia 这次是真想在 AI 时代当老大了，从硬件到软件到生态，全面铺开。其他厂商估计压力不小。"))
    dialogue.append(("female", "嗯，AI 行业竞争越来越激烈了。我们明天见！"))
    dialogue.append(("male", "明天见！"))
    
    return dialogue


def generate_podcast(news_text: str, output_path: str) -> bool:
    sections = parse_news_to_sections(news_text)
    
    total_items = sum(len(v) for v in sections.values())
    if total_items == 0:
        print("没有解析到新闻内容")
        return False
    
    print(f"解析到 {total_items} 条新闻")
    for section, items in sections.items():
        if items:
            print(f"  {section}: {len(items)} 条")
    
    dialogue = create_dialogue_from_sections(sections)
    print(f"生成了 {len(dialogue)} 段对话")
    
    audio_files = []
    temp_dir = tempfile.mkdtemp()
    
    for i, (speaker, text) in enumerate(dialogue):
        voice = TTS_CONFIG["female_voice"] if speaker == "female" else TTS_CONFIG["male_voice"]
        audio_path = os.path.join(temp_dir, f"segment_{i:03d}.mp3")
        
        clean_text = re.sub(r'[📊🔗📅🔥🔹•|]', '', text).strip()
        if not clean_text:
            continue
        
        print(f"  [{i+1}/{len(dialogue)}] {speaker}: {clean_text[:40]}...")
        
        if generate_tts(clean_text, voice, audio_path):
            audio_files.append(audio_path)
    
    if not audio_files:
        print("没有成功生成任何音频")
        return False
    
    if len(audio_files) == 1:
        import shutil
        shutil.copy(audio_files[0], output_path)
    else:
        import subprocess
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for af in audio_files:
                f.write(f"file '{af}'\n")
        
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output_path]
        subprocess.run(cmd, capture_output=True)
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return os.path.exists(output_path)
