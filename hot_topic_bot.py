import requests
import os
import json
from datetime import datetime

# 配置信息
FEISHU_WEBHOOK = os.environ['FEISHU_WEBHOOK_URL']
DEEPSEEK_API_KEY = os.environ['DEEPSEEK_API_KEY']

def fetch_pet_topics():
    """获取宠物相关热点"""
    try:
        # 方法1: 从今日热榜API获取（免费）
        url = "https://api.tophub.today/v2/GetAllTypeGlobalData"
        response = requests.get(url)
        data = response.json()
        
        # 查找宠物相关分类（ID可能需要调整）
        pet_data = None
        for category in data['Data']:
            if '宠物' in category['name']:
                pet_data = category['data']
                break
                
        return pet_data[:10] if pet_data else []  # 返回前10条
        
    except Exception as e:
        print(f"获取热点失败: {e}")
        return []

def ai_analyze_topics(topics):
    """使用AI分析热点并生成创意"""
    if not topics:
        return "今日暂无宠物相关热点"
    
    # 构建话题列表
    topics_text = "\n".join([f"{i+1}. {item['Title']}" for i, item in enumerate(topics)])
    
    # 调用DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    作为宠物自媒体博主，请分析以下今日宠物热点，为我的账号（专注猫咪医疗科普、人宠生活、AI与宠物）生成3个小红书创作灵感：
    
    {topics_text}
    
    要求：
    1. 每个灵感包含标题和简要内容方向
    2. 结合我的账号定位
    3. 语言活泼，有网感
    4. 输出格式为Markdown
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    
    response = requests.post("https://api.deepseek.com/v1/chat/completions", 
                           headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"AI分析失败: {response.text}"

def send_to_feishu(content):
    """发送消息到飞书"""
    payload = {
        "msg_type": "interactive",
        "card": {
            "elements": [{
                "tag": "div",
                "text": {
                    "content": content,
                    "tag": "lark_md"
                }
            }],
            "header": {
                "title": {
                    "content": f"🐱 每日宠物灵感推送 - {datetime.now().strftime('%m/%d')}",
                    "tag": "plain_text"
                }
            }
        }
    }
    
    response = requests.post(FEISHU_WEBHOOK, json=payload)
    return response.status_code == 200

def main():
    print("开始获取今日热点...")
    topics = fetch_pet_topics()
    print(f"获取到 {len(topics)} 条热点")
    
    print("AI分析中...")
    analysis = ai_analyze_topics(topics)
    
    print("发送到飞书...")
    success = send_to_feishu(analysis)
    
    if success:
        print("推送成功!")
    else:
        print("推送失败!")

if __name__ == "__main__":
    main()
