def fetch_pet_topics():
    """获取宠物相关热点 - 修复版本"""
    pet_topics = []
    keywords = ['猫', '狗', '宠物', '萌宠', '喵', '汪', '猫咪', '狗狗', '铲屎官', '毛孩子', '主子']
    
    print("开始从多个数据源获取热点...")
    
    # 数据源1: 微博热搜（相对稳定）
    try:
        print("尝试从微博热搜获取...")
        weibo_url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(weibo_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            hot_list = data.get('data', {}).get('realtime', [])
            
            for item in hot_list:
                title = item.get('note', '')
                if title and any(keyword in title for keyword in keywords):
                    pet_topics.append({
                        'Title': title,
                        'Url': f"https://s.weibo.com/weibo?q={title}",
                        'Source': '微博'
                    })
                    print(f"✓ 从微博找到: {title}")
            
            print(f"从微博热搜找到 {len([t for t in pet_topics if t['Source'] == '微博'])} 条宠物相关热点")
        else:
            print(f"微博热搜请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"微博热搜获取失败: {str(e)}")
    
    # 数据源2: 知乎热榜
    try:
        print("尝试从知乎热榜获取...")
        zhihu_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.zhihu.com/hot'
        }
        response = requests.get(zhihu_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', []):
                title = item.get('target', {}).get('title', '')
                if title and any(keyword in title for keyword in keywords):
                    # 检查是否已存在类似标题，避免重复
                    if not any(t['Title'] == title for t in pet_topics):
                        pet_topics.append({
                            'Title': title,
                            'Url': f"https://www.zhihu.com/question/{item.get('target', {}).get('id', '')}",
                            'Source': '知乎'
                        })
                        print(f"✓ 从知乎找到: {title}")
            
            print(f"从知乎热榜找到 {len([t for t in pet_topics if t['Source'] == '知乎'])} 条宠物相关热点")
        else:
            print(f"知乎热榜请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"知乎热榜获取失败: {str(e)}")
    
    print(f"总共找到 {len(pet_topics)} 条宠物相关热点")
    return pet_topics[:10]  # 返回前10条

def ai_analyze_topics(topics):
    """使用AI分析热点并生成创意"""
    if not topics:
        return "今日暂无宠物相关热点"
    
    # 构建话题列表，包含来源信息
    topics_text = "\n".join([f"{i+1}. [{item['Source']}] {item['Title']}" for i, item in enumerate(topics)])
    
    # 调用DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    作为宠物自媒体博主，请分析以下今日宠物热点，为我的账号（专注猫咪医疗科普、人宠生活、AI与宠物）生成3个小红书创作灵感：
    
    {topics_text}
    
    要求：
    1. 每个灵感包含【标题】和【内容方向】
    2. 结合我的账号定位，可以侧重医疗科普、温馨生活或科技应用
    3. 语言活泼，有网感，使用小红书风格
    4. 输出格式为Markdown，清晰易读
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    
    try:
        response = requests.post("https://api.deepseek.com/v1/chat/completions", 
                               headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"AI分析失败: {response.status_code} - {response.text}"
    except Exception as e:
        return f"AI分析请求异常: {str(e)}"
