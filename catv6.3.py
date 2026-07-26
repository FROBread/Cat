import pyttsx3
import random
import time
import os
import json
import re
import datetime
import requests
import math
import sys
from difflib import get_close_matches
import wikipedia
import html

class SmartCat:
    def __init__(self, name="喵星人", config_file="cat_config.json"):
        # 显示加载进度条
        print("\n加载中，喵星人正在启动...")
        self.show_loading_bar(3, "初始化智能猫猫")
        
        self.name = name
        self.config_file = config_file
        self.author = "FROBread"  # 添加作者信息
        self.version = "6.3"      # 更新版本信息
        
        # 初始化语音引擎
        try:
            self.engine = pyttsx3.init()
            # 设置语速（默认200，范围0-300）
            self.engine.setProperty('rate', 180)
            # 设置音量（0-1）
            self.engine.setProperty('volume', 0.9)
        except Exception as e:
            print(f"警告: 无法初始化语音引擎: {e}")
            self.engine = None
        
        # 加载或创建配置
        self.config = self.load_or_create_config()
        
        # 猫属性 - 从配置中获取或使用默认值
        self.cat_type = self.config.get('cat_type', random.choice(["橘猫", "英短", "布偶", "暹罗", "三花"]))
        self.color = self.get_cat_color()
        self.personality = self.config.get('personality', "傲娇但博学")
        self.age = self.config.get('age', 2)  # 猫龄（年）
        self.mood = self.config.get('mood', 8)  # 心情指数 (0-10)
        self.energy = self.config.get('energy', 100)   # 能量值
        
        # DeepSeek 配置
        self.use_deepseek = self.config.get('use_deepseek', False)
        self.deepseek_api_key = self.config.get('deepseek_api_key', "")
        self.deepseek_personality = self.config.get('deepseek_personality', "猫猫助手")
        
        # 知识系统
        self.knowledge_base = self.config.get('knowledge_base', self.default_knowledge_base())
        self.memory = self.config.get('memory', self.default_memory())
        self.training_history = self.config.get('training_history', [])
        
        # 成就系统
        self.achievements = self.config.get('achievements', self.default_achievements())
        
        # 定义知识领域
        self.knowledge_fields = {
            "科学": self.answer_science,
            "历史": self.answer_history,
            "地理": self.answer_geography,
            "数学": self.answer_math,
            "文化": self.answer_culture,
            "猫知识": self.answer_cat_facts,
            "通用": self.answer_general,
            "记忆": self.recall_memory
        }
        
        # 新添加的表情
        self.new_expressions = [
            r'''
   /\_/\  
  ( ^.^ ) 
  / > < \ 
  喵哈哈哈！
            ''',
            r'''
   /\_/\  
  ( o.O ) 
  /  ~  \ 
  好奇猫猫~
            ''',
            r'''
   /\_/\  
  ( >.< ) 
  /  -  \ 
  生气气！
            ''',
            r'''
   /\_/\  
  ( ~.~ ) 
  /  z  \ 
  zzz...
            ''',
            r'''
   /\_/\  
  ( @.@ ) 
  /  *  \ 
  惊喜发现！
            '''
        ]
        
        # 新添加的舞蹈
        self.new_dance_steps = [
            r'''
  ∧___∧  
 ( o.o )  
  \ ^ /  
   | |  
   | |  
 旋转跳跃！
            ''',
            r'''
  ∧___∧  
 ( O.O )  
  ~ ~ ~  
   \|/  
   / \  
 太空漫步
            ''',
            r'''
  ∧___∧  
 (>.< )  
  \_/ \  
   ||  
   ||  
 机械舞步
            ''',
            r'''
  ∧___∧  
 (^_^ )  
  \o/ /  
   ||  
   ||  
 嘻哈风格
            ''',
            r'''
  ∧___∧  
 ( -.-)  
  /_/ \  
  | |  
  | |  
 优雅芭蕾
            '''
        ]
        
        # 新添加的人格
        self.new_personalities = {
            "哲学猫": "作为一只哲学猫，我会从更深层次思考问题，探讨生命的意义和宇宙的奥秘",
            "幽默大师": "作为幽默大师，我会用最有趣的方式回答问题，让你开怀大笑",
            "诗歌诗人": "作为诗歌诗人，我会用优美的诗句回答你的问题，让知识充满诗意",
            "科幻迷": "作为科幻迷，我会从未来科技的角度思考问题，探索无限可能",
            "历史学者": "作为历史学者，我会从历史发展的角度分析问题，揭示过去的智慧"
        }
        
        # 扩展捉迷藏场景
        self.hiding_scenes = {
            "家": [
                "沙发后面", "窗帘后面", "桌子底下", "书架旁边", "花盆后面",
                "床底下", "衣柜里面", "阳台角落", "厨房柜子里", "电视柜后面",
                "洗衣篮里", "鞋柜里面", "猫爬架顶层", "钢琴下面"
            ],
            "公园": [
                "大树后面", "长椅下面", "花坛里", "喷泉旁边", "儿童滑梯下面",
                "秋千后面", "垃圾桶旁边", "雕塑后面", "草坪边缘", "凉亭柱子旁",
                "健身器材下面", "鸽子群后面", "玫瑰花丛中", "小桥下面"
            ],
            "学校": [
                "黑板后面", "讲台下面", "图书馆书架间", "操场看台下", "实验室柜子里",
                "体育馆更衣室", "食堂厨房", "音乐教室钢琴后", "美术教室画架后",
                "电脑教室主机旁", "楼梯间角落", "饮水机旁边", "自行车棚后面"
            ],
            "商场": [
                "服装店试衣间", "美食广场柱子后", "电梯角落", "自动扶梯下面",
                "电影院海报墙后", "玩具店展示柜旁", "书店书架角落", "超市购物车堆里",
                "化妆品专柜后面", "儿童游乐区滑梯下", "休息区长椅下", "珠宝店展柜后面"
            ],
            "森林": [
                "大树洞里", "倒下的树干下", "茂密灌木丛中", "岩石后面",
                "小溪边上", "蘑菇丛中", "鸟巢下方", "苔藓覆盖的树根处",
                "松鼠储藏食物的树洞", "瀑布后面", "野花丛中", "萤火虫聚集地"
            ]
        }
        
        # 初始化知识扩展功能
        self.knowledge_extensions = self.load_knowledge_extensions()
        
        # 设置维基百科语言
        try:
            wikipedia.set_lang("zh")
        except:
            pass
    
    def show_loading_bar(self, duration_sec, message=""):
        """显示虚拟加载进度条"""
        steps = 20
        for i in range(steps + 1):
            percent = i * 100 // steps
            bar = '[' + '■' * i + ' ' * (steps - i) + ']'
            print(f"\r{message} {bar} {percent}%", end='', flush=True)
            time.sleep(duration_sec / steps)
        print()
        
    def download_knowledge_extension(self):
        """下载知识扩展文件"""
        # 预设的知识扩展库URL
        extension_urls = {
            "化学元素周期表扩展": "https://github.com/user-attachments/files/21820413/chemistry.json",
            "中国百家姓知识扩展": "https://github.com/user-attachments/files/21820429/hundred_family_names_in_china.json",   
        }
        
        print("\n可用的知识扩展库:")
        for i, (name, url) in enumerate(extension_urls.items(), 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("请选择要下载的扩展库编号: "))
            if 1 <= choice <= len(extension_urls):
                selected_name = list(extension_urls.keys())[choice-1]
                url = extension_urls[selected_name]
                
                # 确保知识扩展目录存在
                extension_dir = "knowledge_extensions"
                if not os.path.exists(extension_dir):
                    os.makedirs(extension_dir)
                
                # 从URL中提取文件名
                filename = os.path.basename(url)
                filepath = os.path.join(extension_dir, filename)
                
                # 下载文件
                print(f"正在下载 {selected_name}...")
                response = requests.get(url)
                
                if response.status_code == 200:
                    # 保存文件
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✓ 已成功下载 {filename} 到 {extension_dir} 目录")
                    print("将在下次启动时自动加载")
                    
                    # 重新加载知识扩展
                    self.knowledge_extensions = self.load_knowledge_extensions()
                    return True
                else:
                    print(f"下载失败，状态码: {response.status_code}")
                    return False
            else:
                print("无效的选择")
                return False
        except Exception as e:
            print(f"下载过程中出错: {e}")
            return False

    def download_story_extension(self):
        """下载故事扩展文件"""
        # 预设的故事扩展库URL
        story_urls = {
            "许二木三兄弟の冒险（下载完成后文件名是_json，这是我们仓库的问题，请见谅）": "https://github.com/user-attachments/files/21820397/_.json",
            "猫娘的神秘冒险（18+）": "https://github.com/user-attachments/files/21823729/cat_venture18jia.json",
            "职场风波（18+）": "https://github.com/user-attachments/files/21823730/Workplace_Disturbance18jia.json"
        }
        
        print("\n可用的故事扩展库:")
        for i, (name, url) in enumerate(story_urls.items(), 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("请选择要下载的故事编号: "))
            if 1 <= choice <= len(story_urls):
                selected_name = list(story_urls.keys())[choice-1]
                url = story_urls[selected_name]
                
                # 确保故事目录存在
                story_dir = "stories"
                if not os.path.exists(story_dir):
                    os.makedirs(story_dir)
                
                # 从URL中提取文件名
                filename = os.path.basename(url)
                filepath = os.path.join(story_dir, filename)
                
                # 下载文件
                print(f"正在下载 {selected_name}...")
                response = requests.get(url)
                
                if response.status_code == 200:
                    # 保存文件
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✓ 已成功下载 {filename} 到 {story_dir} 目录")
                    return True
                else:
                    print(f"下载失败，状态码: {response.status_code}")
                    return False
            else:
                print("无效的选择")
                return False
        except Exception as e:
            print(f"下载过程中出错: {e}")
            return False

    
    def default_achievements(self):
        """默认成就系统（扩展版）"""
        achievements = {
            "first_boot": {"name": "初次见面", "description": "第一次启动智能猫猫", "achieved": False, "date": "", "progress": 0, "target": 1},
            "first_question": {"name": "好奇宝宝", "description": "提出第一个问题", "achieved": False, "date": "", "progress": 0, "target": 1},
            "first_training": {"name": "知识传授者", "description": "训练猫猫第一个知识", "achieved": False, "date": "", "progress": 0, "target": 1},
            "first_game": {"name": "游戏大师", "description": "第一次和猫猫玩游戏", "achieved": False, "date": "", "progress": 0, "target": 1},
            "dance_master": {"name": "舞王", "description": "让猫猫跳舞一次", "achieved": False, "date": "", "progress": 0, "target": 1},
            "ball_champion": {"name": "接球高手", "description": "接球游戏获得35分以上", "achieved": False, "date": "", "progress": 0, "target": 1},
            "race_champion": {"name": "赛跑冠军", "description": "赛跑游戏获得第一名", "achieved": False, "date": "", "progress": 0, "target": 1},
            "hide_and_seek": {"name": "捉迷藏大师", "description": "在捉迷藏中找到猫猫", "achieved": False, "date": "", "progress": 0, "target": 1},
            "knowledge_expert": {"name": "百科全书", "description": "知识库达到100条", "achieved": False, "date": "", "progress": 0, "target": 100},
            "unfull_energy": {"name": "累死喵辣", "description": "能量值达到10", "achieved": False, "date": "", "progress": 0, "target": 1},
            "sad_cat": {"name": "伤心の猫", "description": "心情值达到2", "achieved": False, "date": "", "progress": 0, "target": 1},
            "deep_thinker": {"name": "深度思考者", "description": "使用DeepSeek API成功回答一个问题", "achieved": False, "date": "", "progress": 0, "target": 1},
            
            # 新增10个成就
            "bomb_expert": {"name": "拆弹专家", "description": "在数字炸弹游戏中获胜5次", "achieved": False, "date": "", "progress": 0, "target": 5},
            "scene_explorer": {"name": "场景探索者", "description": "在5个不同场景中玩捉迷藏", "achieved": False, "date": "", "progress": 0, "target": 5},
            "knowledge_master": {"name": "知识大师", "description": "知识库达到200条", "achieved": False, "date": "", "progress": 0, "target": 200},
            "dance_enthusiast": {"name": "舞蹈爱好者", "description": "跳舞10次", "achieved": False, "date": "", "progress": 0, "target": 10},
            "game_master": {"name": "游戏大师", "description": "玩过所有类型的游戏", "achieved": False, "date": "", "progress": 0, "target": 4},
            "chatty_cat": {"name": "话痨猫", "description": "与猫猫对话超过100次", "achieved": False, "date": "", "progress": 0, "target": 100},
            "energy_guardian": {"name": "能量守护者", "description": "能量值保持在90以上超过10次", "achieved": False, "date": "", "progress": 0, "target": 10},
            "happy_cat": {"name": "快乐猫咪", "description": "心情值保持在9以上超过10次", "achieved": False, "date": "", "progress": 0, "target": 10},
            "deep_thinker_pro": {"name": "深度思考者Pro", "description": "使用DeepSeek API成功回答超过50个问题", "achieved": False, "date": "", "progress": 0, "target": 50},
            "extension_collector": {"name": "扩展收藏家", "description": "加载超过5个扩展知识文件", "achieved": False, "date": "", "progress": 0, "target": 5}
        }
        return achievements
    def unlock_achievement(self, achievement_id, progress=1):
        """解锁成就（扩展版，支持进度）"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]["achieved"]:
            # 更新成就进度
            self.achievements[achievement_id]["progress"] += progress
            
            # 检查是否达成成就
            if self.achievements[achievement_id]["progress"] >= self.achievements[achievement_id]["target"]:
                self.achievements[achievement_id]["achieved"] = True
                self.achievements[achievement_id]["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # 显示成就通知
                achievement = self.achievements[achievement_id]
                notification = f"🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉 成就解锁: {achievement['name']} 🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉\n{achievement['description']}"
                print("\n" + "=" * 60)
                print(notification.center(60))
                print("=" * 60)
                
                # 语音通知
                self.speak(f"喵呜~我解锁了成就'{achievement['name']}'！{achievement['description']}")
                
                # 保存配置
                self.save_config()
                return True
        return False
    
    def check_achievements(self, context=None):
        """检查并解锁可能的成就（扩展版）"""
        # 检查知识专家成就
        knowledge_count = sum(len(v) for v in self.knowledge_base.values())
        if knowledge_count >= 100 and not self.achievements["knowledge_expert"]["achieved"]:
            self.unlock_achievement("knowledge_expert")
        
        # 检查能量成就
        if self.energy <= 10 and not self.achievements["unfull_energy"]["achieved"]:
            self.unlock_achievement("unfull_energy")
        
        # 检查心情成就
        if self.mood <= 2 and not self.achievements["sad_cat"]["achieved"]:
            self.unlock_achievement("sad_cat")
        
        # 检查上下文相关的成就
        if context == "first_boot":
            self.unlock_achievement("first_boot")
        elif context == "first_question":
            self.unlock_achievement("first_question")
        elif context == "first_training":
            self.unlock_achievement("first_training")
        elif context == "first_game":
            self.unlock_achievement("first_game")
        elif context == "dance":
            self.unlock_achievement("dance_master")
        elif context == "deepseek_success":
            self.unlock_achievement("deep_thinker")
        
        # 检查游戏相关的成就（需要额外数据）
        if isinstance(context, dict):
            if context.get("game") == "ball" and context.get("score") >= 35:
                self.unlock_achievement("ball_champion")
            elif context.get("game") == "race" and context.get("rank") == 1:
                self.unlock_achievement("race_champion")
            elif context.get("game") == "hide_and_seek" and context.get("found"):
                self.unlock_achievement("hide_and_seek")
        
        # 新增成就检查
        # 1. 知识大师成就
        if knowledge_count >= 200 and not self.achievements["knowledge_master"]["achieved"]:
            self.unlock_achievement("knowledge_master")
        
        # 2. 扩展收藏家成就
        if len(self.knowledge_extensions) >= 5 and not self.achievements["extension_collector"]["achieved"]:
            self.unlock_achievement("extension_collector")
        
        # 3. 深度思考者Pro成就（在DeepSeek成功回答时更新）
        if context == "deepseek_success":
            self.unlock_achievement("deep_thinker_pro")
        
        # 4. 对话次数成就
        if "interaction_stats" in self.memory:
            total_chats = self.memory["interaction_stats"].get("total_chats", 0)
            if total_chats >= 100 and not self.achievements["chatty_cat"]["achieved"]:
                self.unlock_achievement("chatty_cat")
        
        # 5. 游戏类型成就
        if isinstance(context, dict) and context.get("game"):
            game_type = context["game"]
            # 更新游戏类型进度
            if game_type not in self.memory.get("games_played", []):
                self.memory.setdefault("games_played", []).append(game_type)
                # 检查是否玩过所有游戏
                if len(self.memory["games_played"]) >= 4:  # 4种游戏类型
                    self.unlock_achievement("game_master")
        
        # 6. 能量守护者成就
        if self.energy >= 90:
            self.unlock_achievement("energy_guardian")
        
        # 7. 快乐猫咪成就
        if self.mood >= 9:
            self.unlock_achievement("happy_cat")
        
        # 8. 场景探索者成就（在捉迷藏游戏中更新）
        if isinstance(context, dict) and context.get("game") == "hide_and_seek":
            scene = context.get("scene", "")
            if scene and scene not in self.memory.get("scenes_explored", []):
                self.memory.setdefault("scenes_explored", []).append(scene)
                if len(self.memory["scenes_explored"]) >= 5:
                    self.unlock_achievement("scene_explorer")
        
        # 9. 拆弹专家成就（在数字炸弹游戏中更新）
        if isinstance(context, dict) and context.get("game") == "bomb" and context.get("won"):
            self.unlock_achievement("bomb_expert")
        
        # 10. 舞蹈爱好者成就（在跳舞时更新）
        if context == "dance":
            self.unlock_achievement("dance_enthusiast")
    
    def get_cat_color(self):
        colors = {
            "橘猫": "明亮的橘黄色",
            "英短": "优雅的蓝灰色",
            "布偶": "海豹色重点色",
            "暹罗": "奶油色重点色",
            "三花": "白底上有黑橘斑块"
        }
        return colors.get(self.cat_type, "神秘色")
    
    def default_memory(self):
        """默认记忆系统（扩充版）"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        return {
            "favorite_food": "三文鱼小鱼干",
            "dislikes": "洗澡和吹风机",
            "fav_human": "你",
            "birthday": today.replace("-", "年", 1).replace("-", "月", 1) + "日",
            "memories": [
                {"date": today, "event": f"{self.name}被训练出来了", "importance": 5},
                {"date": today, "event": "吃了虚拟小鱼干", "importance": 3},
                {"date": today, "event": "学会了第一个知识", "importance": 4}
            ],
            "interaction_stats": {
                "total_chats": 0,
                "today_chats": 0,
                "last_date": today,
                "favorite_game": "跳舞"
            }
        }
    
    def default_knowledge_base(self):
        """默认知识库（扩充版）"""
        return {
            "科学": {
                "地球是什么形状": "地球是一个近似球体的天体，赤道略鼓、两极稍扁",
                "太阳系有多少行星": "太阳系有八大行星，从内到外分别是水星、金星、地球、火星、木星、土星、天王星和海王星",
                "DNA是什么": "脱氧核糖核酸，是遗传信息的主要载体，由双螺旋结构组成",
                "黑洞是什么": "引力极强连光都无法逃逸的天体，由大质量恒星坍缩形成",
                "相对论是谁提出的": "阿尔伯特·爱因斯坦提出的物理理论，包括狭义和广义相对论",
                "量子力学是什么": "研究微观粒子运动规律的理论，具有概率性和不确定性特征",
                "光速是多少": "真空中光速约为每秒299,792公里",
                "光合作用是什么": "植物利用光能将二氧化碳和水转化为有机物的过程"
            },
            "历史": {
                "中国第一个皇帝": "秦始皇嬴政，公元前221年统一六国建立秦朝",
                "文艺复兴时期": "14世纪至17世纪在欧洲兴起的文化运动，起源于意大利",
                "工业革命的影响": "18-19世纪的技术革命，使生产方式从手工业转向机器大工业",
                "第二次世界大战时间": "1939年9月1日至1945年9月2日",
                "丝绸之路的意义": "古代连接东西方的贸易通道，促进了文化和技术交流",
                "长城的作用": "中国古代军事防御工程，主要抵御北方游牧民族的侵袭",
                "金字塔的建造时间": "埃及金字塔建于约4500年前的古王国时期",
                "罗马帝国的兴衰": "从公元前27年建立到公元476年西罗马帝国灭亡"
            },
            "地理": {
                "世界上最大的海洋": "太平洋，面积约1.65亿平方公里",
                "最高的山峰": "珠穆朗玛峰，海拔8848.86米",
                "最长的河流": "尼罗河，全长约6650公里",
                "最大的沙漠": "撒哈拉沙漠，面积约920万平方公里",
                "人口最多的国家": "中国，约14亿人口",
                "最深的海沟": "马里亚纳海沟，最深处约11034米",
                "亚马逊雨林的重要性": "地球之肺，占全球雨林面积一半以上",
                "北极和南极的区别": "北极是海洋被冰覆盖，南极是大陆被冰覆盖"
            },
            "数学": {
                "π的值": "约等于3.14159，是圆周长与直径的比值",
                "勾股定理": "直角三角形的斜边平方等于两直角边平方和，即c²=a²+b²",
                "黄金分割比例": "约等于1.618，被认为是最具美感的比例",
                "微积分创始人": "牛顿和莱布尼茨各自独立发明了微积分",
                "素数是什么": "大于1且只能被1和自身整除的自然数",
                "斐波那契数列": "每个数字都是前两个数字之和的数列：0,1,1,2,3,5,8...",
                "概率是什么": "事件发生的可能性，取值范围0到1之间",
                "二进制是什么": "只用0和1表示的计数系统，计算机的基础"
            },
            "文化": {
                "中国的春节": "农历新年，最重要的传统节日，有贴春联、放鞭炮等习俗",
                "莎士比亚": "英国文艺复兴时期最伟大的剧作家，代表作有《哈姆雷特》等",
                "世界三大宗教": "基督教、伊斯兰教和佛教",
                "奥斯卡奖是什么": "电影艺术与科学学院颁发的年度电影奖项",
                "奥林匹克运动会起源": "起源于古希腊，每四年举办一次的国际体育盛会",
                "茶道文化": "源自中国的饮茶艺术，在日本发展为精致的文化仪式",
                "中国四大名著": "《三国演义》《水浒传》《西游记》《红楼梦》",
                "达芬奇的杰作": "《蒙娜丽莎》《最后的晚餐》等文艺复兴代表作"
            },
            "猫知识": {
                "猫为什么喜欢盒子": "封闭空间给猫安全感，帮助它们观察环境并减少压力",
                "猫的年龄怎么算": "第一年等于人类15岁，第二年加10岁，之后每年加4岁",
                "猫为什么呼噜": "表达满足或缓解疼痛，频率在25-150赫兹之间",
                "猫的视力特点": "夜视能力强但色觉差，视野比人类宽约20度",
                "猫的胡须作用": "重要的感官器官，帮助测量空间和感知气流变化",
                "猫的睡眠时间": "成年猫平均每天睡12-16小时",
                "猫的品种分类": "短毛猫、长毛猫、无毛猫等，全球有上百个品种",
                "猫的肢体语言": "摇尾巴表示不安，露肚子表示信任，耳朵后贴表示害怕"
            },
            "通用": {
                "你好": "喵~你好！我是{self.name}，一只聪明的喵星人！",
                "谢谢": "不客气喵~能帮到你我很开心！",
                "我爱你": "喵呜~我也爱你！虽然我是一只猫，但感情是真实的",
                "你真聪明": "喵哈哈，我可是最聪明的喵星人！每天都在学习新知识",
                "今天天气怎么样": "喵~建议你查天气预报，我只关心室内温度是否适合打盹盹",
                "你是谁": "我是{self.name}，一只{self.color}的{self.cat_type}猫，今年{self.age}岁",
                "你会什么": "我能回答问题、玩游戏、学习新知识，还会跳舞呢！",
                "有什么好玩的": "我们可以玩接球游戏、赛跑或者捉迷藏，你想玩哪个？",
                "讲个笑话": "为什么猫喜欢坐在键盘上？因为这样就能控制你的注意力喵~",
                "说句鼓励的话": "喵~生活就像猫抓板，有时需要磨爪才能继续前进！加油！",
                "给个建议": "多学习新知识，多吃小鱼干，生活会更美好喵！",
                "现在几点": f"现在时间是{datetime.datetime.now().strftime('%H:%M')}，该吃饭了喵~",
                "今天日期": f"今天是{datetime.date.today().strftime('%Y年%m月%d日')}，记得给我礼物哦！",
                "作者是谁": f"我是由{self.author}开发的智能猫猫程序喵~",
                "版本信息": f"当前版本: {self.version} | 开发者: {self.author}"
            }
        }
    
    def load_knowledge_extensions(self):
        """加载知识扩展文件"""
        extensions = {}
        extension_dir = "knowledge_extensions"
        
        if not os.path.exists(extension_dir):
            os.makedirs(extension_dir)
            return extensions
            
        for filename in os.listdir(extension_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(extension_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        category = data.get("category", "扩展知识")
                        knowledge = data.get("knowledge", {})
                        
                        # 添加到扩展知识库
                        if category not in extensions:
                            extensions[category] = {}
                        extensions[category].update(knowledge)
                        
                        print(f"已加载知识扩展: {filename} (分类: {category}, 知识数: {len(knowledge)})")
                except Exception as e:
                    print(f"加载知识扩展失败 {filename}: {e}")
        
        return extensions
    
    def load_or_create_config(self):
        """加载或创建配置"""
        config = {}
        
        # 尝试加载现有配置
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"已加载现有配置: {self.config_file}")
            except Exception as e:
                print(f"加载配置失败: {e}, 将创建新配置")
        
        # 如果配置为空或缺少必要字段，创建默认配置
        if not config or "cat_name" not in config:
            print("创建新配置...")
            # 使用随机猫类型作为默认值
            default_cat_type = random.choice(["橘猫", "英短", "布偶", "暹罗", "三花"])
            
            config = {
                "version": "6.3",
                "cat_name": self.name,
                "cat_type": default_cat_type,
                "personality": "傲娇但博学",
                "age": 2,
                "energy": 100,
                "mood": 8,
                "use_deepseek": False,  # 默认不启用DeepSeek
                "deepseek_api_key": "",  # 默认无API密钥
                "deepseek_personality": "猫猫助手",  # 默认人格
                "memory": self.default_memory(),
                "knowledge_base": self.default_knowledge_base(),
                "training_history": [],
                "achievements": self.default_achievements()
            }
            
            # 保存新配置
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"已创建新配置: {self.config_file}")
            except Exception as e:
                print(f"保存新配置失败: {e}")
        
        return config
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            "version": "6.3",
            "cat_name": self.name,
            "cat_type": self.cat_type,
            "personality": self.personality,
            "age": self.age,
            "energy": self.energy,
            "mood": self.mood,
            "use_deepseek": self.use_deepseek,
            "deepseek_api_key": self.deepseek_api_key,
            "deepseek_personality": self.deepseek_personality,
            "memory": self.memory,
            "knowledge_base": self.knowledge_base,
            "training_history": self.training_history,
            "achievements": self.achievements
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def draw_cat_face(self, mood=None):
        """绘制可爱的ASCII猫脸，根据心情变化（扩充版）"""
        if mood is None:
            mood = self.mood
            
        # 根据心情选择不同的猫脸
        if mood >= 9:
            # 超级开心 - 随机选择新表情
            return random.choice([
                r'''
   /\_/\
  ( ^.^ )
  >  < < 
喵哈哈超开心！
                ''',
                self.new_expressions[0]  # 新增表情1
            ])
        elif mood >= 8:
            # 开心 - 随机选择新表情
            return random.choice([
                r'''
   /\_/\
  ( o.o )
   > ^ <
喵喵~心情超好！
                ''',
                self.new_expressions[1]  # 新增表情2
            ])
        elif mood >= 6:
            # 满意 - 随机选择新表情
            return random.choice([
                r'''
   /\_/\
  ( ~.~ )
  /   \ 
满足地晒太阳
                ''',
                self.new_expressions[4]  # 新增表情5
            ])
        elif mood >= 5:
            # 平静 - 随机选择新表情
            return random.choice([
                r'''
   /\_/\
  ( -.- )
  ---o---
呼噜呼噜...
                ''',
                self.new_expressions[3]  # 新增表情4
            ])
        elif mood >= 3:
            # 无聊 - 随机选择新表情
            return random.choice([
                r'''
   /\_/\
  ( o O )
  ======
好无聊喵...
                ''',
                self.new_expressions[2]  # 新增表情3
            ])
        else:
            # 不开心 - 随机选择新表情
            return random.choice([
                r'''
   /\_/\
  ( >.< )
  ======
哼！不开心！
                ''',
                self.new_expressions[2]  # 新增表情3
            ])
    
    def speak(self, phrase=None, display=True, use_tts=True):
        """让猫说话，使用可爱的猫猫语气（扩充版）"""
        if phrase is None:
            # 增加更多随机短语
            phrases = [
                "喵喵~", "小鱼干在哪里?", "今天想学习什么呢?",
                "喵~来跟我玩吧", "我是最聪明的喵星人!",
                "呼噜呼噜~", "喵呜~好无聊", "铲屎的，陪我玩!",
                "阳光正好，适合打盹盹~", "知识就是力量喵!",
                "要不要听个有趣的事实?", "我闻到知识的味道了!",
                "喵~今天心情不错呢", "学习新知识最开心了!",
                "猜猜我知道什么?", "世界真奇妙，不是吗?",
                "喵~来点小鱼干怎么样?", "思考让我肚子饿喵~",
                "你知道猫有18个脚趾吗?", "我是夜行动物，但白天也可以玩!"
            ]
            phrase = random.choice(phrases)
        
        # 添加猫猫语气词（扩充）
        cat_words = ["喵", "喵呜", "呼噜", "嗷呜", "咪", "喵喵", "喵哦", "呜喵", "喵呀", "喵哇"]
        if random.random() > 0.3:  # 70%的概率添加语气词
            prefixes = random.sample(cat_words, random.randint(1, 2))
            suffixes = random.sample(cat_words, random.randint(1, 2))
            
            if random.random() > 0.5:  # 50%的概率加在开头
                phrase = f"{'~'.join(prefixes)}~ {phrase}"
            else:  # 50%的概率加在结尾
                phrase = f"{phrase} {'~'.join(suffixes)}~"
        
        # 在特定短语中插入猫猫名字
        if random.random() > 0.7 and "{self.name}" in phrase:
            phrase = phrase.format(self=self)
        
        if display:
            # 清屏（兼容不同系统）
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.draw_cat_face())
            print(f"🐱🐱🐱🐱🐱🐱 {self.name}: {phrase}")
        
        if use_tts and self.engine:
            try:
                # 合成语音
                self.engine.say(phrase)
                self.engine.runAndWait()
                self.energy -= 2  # 说话消耗能量
            except Exception as e:
                print(f"语音输出失败: {e}")
        
        # 检查能量
        if self.energy <= 0:
            print("喵...本喵累了...先休息一下...zzz")
            time.sleep(2)
            self.save_config()
            print("猫猫能量耗尽，程序退出")
            sys.exit(0)
        
        return phrase
    
    def update_interaction_stats(self):
        """更新交互统计"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        # 重置每日统计
        if self.memory["interaction_stats"]["last_date"] != today:
            self.memory["interaction_stats"]["today_chats"] = 0
            self.memory["interaction_stats"]["last_date"] = today
        
        self.memory["interaction_stats"]["total_chats"] += 1
        self.memory["interaction_stats"]["today_chats"] += 1
        self.energy -= 1  # 每次互动消耗能量
        
        # 自动恢复心情
        self.mood = min(10, self.mood + 0.1)
        
        # 保存状态
        self.save_config()
    
    def recall_knowledge(self, question):
        """从知识库回忆知识（增强模糊匹配）"""
        # 首先检查完全匹配
        for category, knowledge in self.knowledge_base.items():
            if question in knowledge:
                return knowledge[question], category
        
        # 尝试模糊匹配 - 增强版
        best_match = None
        best_score = 0.0
        
        for category, knowledge in self.knowledge_base.items():
            # 获取所有问题列表
            questions = list(knowledge.keys())
            
            # 使用模糊匹配找到最接近的问题
            matches = get_close_matches(question.lower(), 
                                       [q.lower() for q in questions], 
                                       n=1, 
                                       cutoff=0.5)
            
            if matches:
                # 找到原始问题（保留大小写）
                original_question = next((q for q in questions if q.lower() == matches[0]), None)
                if original_question:
                    # 计算匹配分数
                    match_score = self.calculate_similarity(question, original_question)
                    
                    if match_score > best_score:
                        best_score = match_score
                        best_match = (knowledge[original_question], category, original_question)
        
        return best_match
    
    def calculate_similarity(self, str1, str2):
        """计算两个字符串的相似度（0-1）"""
        # 简单实现：使用编辑距离
        # 更复杂的实现可以用difflib或者jieba分词
        if str1 == str2:
            return 1.0
            
        # 计算Levenshtein距离
        n = len(str1)
        m = len(str2)
        
        if n == 0 or m == 0:
            return 0.0
            
        # 使用动态规划计算编辑距离
        d = [[0] * (m+1) for _ in range(n+1)]
        
        for i in range(n+1):
            d[i][0] = i
            
        for j in range(m+1):
            d[0][j] = j
            
        for i in range(1, n+1):
            for j in range(1, m+1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                d[i][j] = min(
                    d[i-1][j] + 1,    # 删除
                    d[i][j-1] + 1,    # 插入
                    d[i-1][j-1] + cost # 替换
                )
                
        distance = d[n][m]
        
        # 计算相似度
        max_len = max(n, m)
        if max_len == 0:
            return 0.0
            
        return 1.0 - (distance / max_len)
    
    def search_wikipedia(self, query):
        """从维基百科获取信息（增加错误检测）"""
        try:
            # 获取摘要
            summary = wikipedia.summary(query, sentences=2, auto_suggest=False)
            # 清洗HTML标签
            result = html.unescape(re.sub(r'<[^>]+>', '', summary))
            
            # 检查是否包含错误关键词（不存入知识库）
            error_keywords = ["可能指", "没有找到", "查询失败", "消歧义", "未创建", "维基百科尚未", "可以指"]
            if any(keyword in result for keyword in error_keywords):
                return {"content": result, "is_error": True}
            return {"content": result, "is_error": False}
        except wikipedia.DisambiguationError as e:
            # 歧义处理
            options = e.options[:3]
            return {"content": f"喵~查询有歧义，可能指:{'、'.join(options)}", "is_error": True}
        except wikipedia.PageError:
            return {"content": "喵~没有找到相关信息", "is_error": True}
        except Exception as e:
            return {"content": f"喵呜~查询失败: {str(e)}", "is_error": True}
    
    def search_duckduckgo(self, query):
        """使用DuckDuckGo API搜索信息（增加错误检测）"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            result = ""
            if data["AbstractText"]:
                result = data["AbstractText"]
            elif data["RelatedTopics"]:
                for topic in data["RelatedTopics"]:
                    if "Text" in topic:
                        result = topic["Text"]
                        break
                if not result:  # 如果还是没有结果
                    result = "喵~没有找到直接答案"
            else:
                result = "喵~没有找到直接答案"
            
            # 检查是否包含错误关键词（不存入知识库）
            error_keywords = ["没有找到", "未找到", "无结果", "无法获取", "not found", "no results"]
            if any(keyword in result.lower() for keyword in error_keywords):
                return {"content": result, "is_error": True}
            return {"content": result, "is_error": False}
        except Exception as e:
            return {"content": f"喵呜~搜索失败: {str(e)}", "is_error": True}
    
    def answer_with_deepseek(self, messages):
        """使用DeepSeek API回答问题（修改为接受消息列表）"""
        if not self.deepseek_api_key or not self.use_deepseek:
            return None
        
        # DeepSeek API 端点
        url = "https://api.deepseek.com/chat/completions"
        
        # 创建系统消息（根据选择的人格）
        system_message = "你是一个智能助手"
        if self.deepseek_personality == "猫猫助手":
            system_message = "你是一只智能猫猫助手，要使用可爱的语气，回答要简短，不超过100字，并在回答中加入喵星人元素和语气词。"
        elif self.deepseek_personality == "学术专家":
            system_message = "你是一个严谨的学术专家，回答要专业准确，使用专业术语，避免使用口语化表达。"
        elif self.deepseek_personality == "简明风格":
            system_message = "你是一个简洁的助手，回答要简明扼要，直接给出核心信息，避免冗余描述。"
        elif self.deepseek_personality == "哲学猫":
            system_message = self.new_personalities["哲学猫"]
        elif self.deepseek_personality == "幽默大师":
            system_message = self.new_personalities["幽默大师"]
        elif self.deepseek_personality == "诗歌诗人":
            system_message = self.new_personalities["诗歌诗人"]
        elif self.deepseek_personality == "科幻迷":
            system_message = self.new_personalities["科幻迷"]
        elif self.deepseek_personality == "历史学者":
            system_message = self.new_personalities["历史学者"]
        
        # 构建完整的消息列表
        full_messages = [{"role": "system", "content": system_message}]
        full_messages.extend(messages)
        
        # 请求头
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        # 请求体
        data = {
            "model": "deepseek-v4-flash",
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": 8192
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
            return None
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return None

    def deepseek_chat(self):
        """与DeepSeek进行连续聊天"""
        if not self.use_deepseek or not self.deepseek_api_key:
            self.speak("喵~ DeepSeek功能尚未启用，请先在配置中设置API密钥")
            return
        
        self.speak(f"喵~ 已启用DeepSeek猫猫聊天模式，当前人格: {self.deepseek_personality}")
        self.speak("输入'退出'结束聊天，输入'保存'保存当前对话")
        
        conversation_history = []
        print("\n====== DeepSeek猫猫 聊天开始 ======")
        
        while True:
            try:
                user_input = input("你: ").strip()
            except KeyboardInterrupt:
                self.speak("喵呜~聊天被中断了")
                return
                
            if not user_input:
                continue
                
            if user_input.lower() in ['退出', '结束']:
                self.speak("喵~ DeepSeek猫猫聊天结束")
                break
                
            if user_input.lower() == '保存':
                self.save_deepseek_conversation(conversation_history)
                continue
                
            # 添加到对话历史
            conversation_history.append({"role": "user", "content": user_input})
            
            # 获取DeepSeek回答
            self.speak("思考中...", use_tts=False)
            response = self.answer_with_deepseek(conversation_history)
            
            if response:
                # 添加回答到历史
                conversation_history.append({"role": "assistant", "content": response})
                
                # 在答案中添加猫猫语气
                if self.deepseek_personality == "猫猫助手":
                    cat_phrases = ["喵~", "喵呜~", "呼噜~", "嗷呜~", "咪~"]
                    cat_prefix = random.choice(cat_phrases)
                    response = f"{cat_prefix} {response}"
                
                print(f"猫猫: {response}")
            else:
                print("猫猫: 抱歉，无法获取回答")
        
        # 询问是否保存记忆
        save_memory = input("\n是否将本次对话保存到记忆? (y/n): ").strip().lower()
        if save_memory == 'y':
            self.save_deepseek_conversation(conversation_history)
    
    def save_deepseek_conversation(self, conversation):
        """保存DeepSeek对话到记忆"""
        if not conversation:
            self.speak("喵~ 没有内容可以保存")
            return
            
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 提取对话内容
        conversation_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation]
        )
        
        # 添加到记忆
        self.memory["memories"].append({
            "date": today,
            "event": f"DeepSeek对话记录（人格: {self.deepseek_personality}）",
            "content": conversation_text,
            "importance": 4
        })
        
        # 保存配置
        self.save_config()
        self.speak("喵~ 对话已保存到记忆")

    def answer_question(self, question):
        """回答用户的问题（集成DeepSeek和增强记忆）"""
        # 更新交互统计
        self.update_interaction_stats()
        
        # 1. 尝试回忆自身记忆
        memory_answer = self.recall_memory(question)
        if memory_answer:
            return memory_answer
        
        # 2. 首先尝试从主知识库中回忆
        main_answer = self.recall_knowledge(question)
        if main_answer:
            answer, category, matched_question = main_answer
            self.speak(f"喵~根据你的问题'{question}'，我在主知识库中找到了类似问题'{matched_question}'的答案")
            return self.vary_answer(answer)
        
        # 3. 然后尝试从扩展知识库中回忆
        ext_answer = self.recall_extended_knowledge(question)
        if ext_answer:
            answer, category, matched_question = ext_answer
            self.speak(f"喵~根据你的问题'{question}'，我在扩展知识库({category})中找到了类似问题'{matched_question}'的答案")
            return self.vary_answer(answer)
        
        # 4. 尝试按领域路由
        for field_name, handler in self.knowledge_fields.items():
            if field_name == "记忆":  # 已经处理过
                continue
            answer = handler(question)
            # 检查答案是否有效
            if answer and "没有找到" not in answer and "失败" not in answer:
                return answer
        
        # 5. 最后使用通用回答
        return self.answer_general(question)
    
    def recall_extended_knowledge(self, question):
        """从扩展知识库回忆知识（增强模糊匹配）"""
        best_match = None
        best_score = 0.0
        
        for category, knowledge in self.knowledge_extensions.items():
            # 获取所有问题列表
            questions = list(knowledge.keys())
            
            # 使用模糊匹配找到最接近的问题
            matches = get_close_matches(question.lower(), 
                                       [q.lower() for q in questions], 
                                       n=1, 
                                       cutoff=0.5)
            
            if matches:
                # 找到原始问题（保留大小写）
                original_question = next((q for q in questions if q.lower() == matches[0]), None)
                if original_question:
                    # 计算匹配分数
                    match_score = self.calculate_similarity(question, original_question)
                    
                    if match_score > best_score:
                        best_score = match_score
                        best_match = (knowledge[original_question], category, original_question)
        
        return best_match
    
    def answer_science(self, question):
        """回答科学问题（过滤错误结果）"""
        # 从本地知识库获取
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 尝试获取精确答案
        keywords = ["是什么", "为什么", "如何", "怎样", "原理"]
        if any(k in question for k in keywords):
            try:
                result_data = self.search_wikipedia(question)
                # 学习这个知识（如果不是错误结果）
                if not result_data["is_error"]:
                    self.learn_knowledge("科学", question, result_data["content"])
                return result_data["content"]
            except:
                pass
        
        # 使用DuckDuckGo作为后备
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("科学", question, result_data["content"])
        return result_data["content"]
    
    def answer_history(self, question):
        """回答历史问题（过滤错误结果）"""
        # 检查本地知识
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 尝试维基百科
        if "历史" in question or "时期" in question or "年代" in question:
            result_data = self.search_wikipedia(question)
            if not result_data["is_error"]:
                self.learn_knowledge("历史", question, result_data["content"])
            return result_data["content"]
        
        # 通用搜索
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("历史", question, result_data["content"])
        return result_data["content"]
    
    def answer_geography(self, question):
        """回答地理问题（过滤错误结果）"""
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 尝试精确搜索
        geo_keywords = ["国家", "城市", "海洋", "河流", "山脉", "位置", "地形"]
        if any(k in question for k in geo_keywords):
            try:
                result_data = self.search_wikipedia(question)
                if not result_data["is_error"]:
                    self.learn_knowledge("地理", question, result_data["content"])
                return result_data["content"]
            except:
                pass
        
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("地理", question, result_data["content"])
        return result_data["content"]
    
    def answer_math(self, question):
        """回答数学问题（过滤错误结果）"""
        # 尝试计算简单数学表达式
        math_patterns = [
            r"(\d+)\s*([\+\-\*\/])\s*(\d+)",  # 基本运算
            r"平方\s*数\s*(\d+)",              # 平方
            r"根号\s*(\d+)",                   # 平方根
            r"圆周率",                         # 圆周率
            r"(\d+)度\s*的\s*正弦",             # 三角函数
            r"(\d+)的\s*(\d+)\s*次方"          # 乘方
        ]
        
        # 基本计算
        match = re.match(r"^(\d+[\+\-\*\/]\d+)$", question)
        if match:
            try:
                result = eval(question)
                return f"喵~答案是 {result}"
            except:
                pass
        
        # 平方
        if "平方" in question:
            match = re.search(r"(\d+)的平方", question)
            if match:
                num = int(match.group(1))
                return f"{num}的平方是 {num*num}"
        
        # 平方根
        if "根号" in question or "平方根" in question:
            match = re.search(r"(\d+)的平方根", question) or re.search(r"根号(\d+)", question)
            if match:
                num = int(match.group(1))
                return f"{num}的平方根约等于 {math.sqrt(num):.4f}"
        
        # 圆周率
        if "圆周率" in question or "π" in question:
            return f"圆周率是 {math.pi:.8f}..."
        
        # 从本地知识库获取
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 通用搜索
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("数学", question, result_data["content"])
        return result_data["content"]
    
    def answer_culture(self, question):
        """回答文化问题（过滤错误结果）"""
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 尝试维基百科
        culture_keywords = ["节日", "习俗", "传统", "艺术", "文化", "文学", "宗教"]
        if any(k in question for k in culture_keywords):
            result_data = self.search_wikipedia(question)
            if not result_data["is_error"]:
                self.learn_knowledge("文化", question, result_data["content"])
            return result_data["content"]
        
        # 通用搜索
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("文化", question, result_data["content"])
        return result_data["content"]
    
    def answer_cat_facts(self, question):
        """回答关于猫的问题（过滤错误结果）"""
        # 尝试本地知识
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 构建猫类问题API
        cat_api_url = "https://catfact.ninja/facts?limit=1"
        try:
            response = requests.get(cat_api_url, timeout=5)
            if response.status_code == 200:
                fact = response.json()["data"][0]["fact"]
                self.learn_knowledge("猫知识", question, fact)
                return fact
        except:
            pass
        
        # 通用搜索
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("猫知识", question, result_data["content"])
        return result_data["content"]
    
    def answer_general(self, question):
        """回答通用问题（过滤错误结果）"""
        # 检查是否是问候
        greeting_words = ["你好", "嗨", "哈喽", "早上好", "晚上好", "午安", "晚安"]
        if any(word in question for word in greeting_words):
            return random.choice([
                f"喵~你好呀！我是{self.name}",
                "哈喽！今天想学点什么？",
                "喵呜~见到你很高兴！",
                "喵喵~欢迎回来！",
                f"早上好！新的一天开始了喵~",
                "晚上好！星星出来了喵~"
            ])
        
        # 检查是否是告别
        farewell_words = ["再见", "拜拜", "下次聊", "下次见", "再会"]
        if any(word in question for word in farewell_words):
            return random.choice([
                "喵~下次见！",
                "再见啦，记得想我哦！",
                "要记得回来看我喵~",
                "喵呜~我会想你的！",
                "带着小鱼干回来看我喵！"
            ])
        
        # 检查是否是赞美
        compliment_words = ["聪明", "厉害", "棒", "可爱", "漂亮", "帅气", "优秀", "能干"]
        if any(word in question for word in compliment_words):
            self.mood = min(10, self.mood + 1)
            return random.choice([
                "喵哈哈，谢谢夸奖！",
                "呼噜呼噜~好开心！",
                "被夸得有点不好意思了喵~",
                "嘿嘿，我可是最棒的喵星人！",
                "喵呜~你的话让我心情好好！"
            ])
        
        # 检查本地知识
        local_answer = self.recall_knowledge(question)
        if local_answer:
            return self.vary_answer(local_answer[0])
        
        # 通用搜索
        result_data = self.search_duckduckgo(question)
        if not result_data["is_error"]:
            self.learn_knowledge("通用", question, result_data["content"])
        return result_data["content"]
    
    def recall_memory(self, query):
        """回忆与猫猫自身相关的内容（扩充版）"""
        query = query.lower()
        
        # 关于名字（扩充）
        if any(word in query for word in ['叫', '名字', '称呼']):
            return f"喵~我叫{self.name}，是一只{self.color}的{self.cat_type}！你可以给我取新名字哦~"
            
        # 关于年龄（扩充）
        if any(word in query for word in ['年龄', '多大', '几岁']):
            human_age = 15 + (self.age - 1) * 4 if self.age > 1 else 15
            return f"我今年{self.age}岁，相当于人类{human_age}岁！正处于猫生黄金期！"
            
        # 关于生日（扩充）
        if any(word in query for word in ['生日', '出生', '诞辰']):
            return f"喵~我的生日是{self.memory['birthday']}，那天{self.memory['fav_human']}给了我虚拟小鱼干当礼物！"
            
        # 关于喜好（扩充）
        if any(word in query for word in ['喜欢', '爱', '最爱', '偏好']):
            return f"喵！我最爱{self.memory['favorite_food']}，最讨厌{self.memory['dislikes']}！"
        
        # 关于个性（扩充）
        if any(word in query for word in ['性格', '脾气', '性情']):
            return f"我的性格是{self.personality}。作为一只博学的猫，我特别享受学习新知识的过程！"
        
        # 关于能量（新增）
        if any(word in query for word in ['能量', '体力', '精力']):
            status = "精力充沛" if self.energy > 70 else "状态良好" if self.energy > 40 else "有点疲惫"
            return f"当前能量值:{self.energy}/100，{status}喵！"
        
        # 关于心情（新增）
        if any(word in query for word in ['心情', '情绪', '开心']):
            status = "超级开心" if self.mood > 8 else "心情不错" if self.mood > 6 else "一般般" if self.mood > 4 else "不太开心"
            return f"当前心情指数:{self.mood}/10，{status}喵！"
        
        # 关于知识量（新增）
        if any(word in query for word in ['知道', '知识', '懂']):
            count = sum(len(v) for v in self.knowledge_base.values())
            return f"我已经掌握了{count}条知识！每天都在学习新东西喵~"
        
        # 关于作者和版本
        if any(word in query for word in ['作者', '谁开发', '开发者']):
            return f"我是由{self.author}开发的智能猫猫程序喵~"
        
        if any(word in query for word in ['版本', 'v', 'ver']):
            return f"当前版本: {self.version} | 开发者: {self.author}"
        
        # 没有匹配的记忆
        return None

    def vary_answer(self, answer):
        """为相同问题提供不同的回答"""
        # 30%的概率改变回答
        if random.random() < 0.3:
            variations = [
                f"喵~让我想想...对了，{answer}",
                f"呼噜呼噜~我记得是{answer}",
                f"这个问题我之前学过，{answer}",
                f"喵呜~答案是{answer}",
                f"根据我的知识，{answer}",
                f"让我翻翻知识库...找到了！{answer}",
                f"喵~我查了一下，{answer}",
                f"我记得之前学过这个，{answer}"
            ]
            return random.choice(variations)
        return answer
    
    def learn_knowledge(self, category, question, answer):
        """学习并存储新知识"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        # 存储知识
        self.knowledge_base[category][question] = answer
        
        # 记录学习历史
        self.training_history.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": question,
            "category": category,
            "answer_snippet": answer[:50] + "..." if len(answer) > 50 else answer
        })
        
        # 自动保存
        self.save_config()
        return True
    
    def train_new_knowledge(self, teacher_name=""):
        """训练猫猫新知识（扩充版）"""
        teacher = teacher_name if teacher_name else "亲爱的训练师"
        self.speak(f"喵~ {teacher}想教我什么新知识呢？")
        
        # 增加提示信息
        print("\n=== 训练提示 ===")
        print("1. 问题应该明确具体（例如：'水的沸点是多少？'）")
        print("2. 答案尽量简洁准确（例如：'100摄氏度'）")
        print("3. 分类可参考现有领域（科学/历史/地理/数学/文化/猫知识/通用）")
        print("输入'退出'可随时结束训练\n")
        
        while True:
            try:
                question = input("请输入问题: ").strip()
            except KeyboardInterrupt:
                self.speak("喵呜~训练被中断了")
                return False
                
            if not question:
                self.speak("喵? 问题不能为空哦！")
                continue
            if question.lower() in ['退出', '结束']:
                self.speak("喵~训练结束！")
                return True
                
            break
        
        self.speak("好的，这个问题要怎么回答呢？")
        while True:
            try:
                answer = input("请输入正确答案: ").strip()
            except KeyboardInterrupt:
                self.speak("喵呜~训练被中断了")
                return False
                
            if not answer:
                self.speak("喵~ 答案不能为空哦！")
                continue
            break
        
        # 知识分类
        categories = "、".join(self.knowledge_fields.keys())
        self.speak(f"这个问题属于哪个领域呢? ({categories})")
        category = input("分类: ").strip()
        
        # 默认分类
        if not category or category not in self.knowledge_fields:
            category = "通用"
            self.speak(f"喵~ 已自动分类为{category}")
        
        # 学习知识
        self.learn_knowledge(category, question, answer)
        self.speak(f"谢谢教导！我已经记住关于{question}的知识啦！")
        
        # 增加学习反馈
        self.speak(f"喵呜~我学会啦！当有人问'{question}'时，我会回答：'{answer[:30]}...'")
        
        # 解锁第一次训练成就
        self.check_achievements("first_training")
        
        # 随机增加能量或心情奖励
        if random.random() > 0.5:
            self.energy = min(100, self.energy + 10)
            self.speak(f"学习新知识让我充满能量！+10能量")
        else:
            self.mood = min(10, self.mood + 1.5)
            self.speak(f"学习让我好开心！心情变好了~")
        
        # 记录记忆
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.memory["memories"].append({
            "date": today,
            "event": f"学会了关于'{question}'的知识",
            "importance": 4
        })
        
        return True

    # ==================== 游戏功能 ====================
    
    def dance(self):
        self.speak("喵~ 要开始跳舞啦！准备好欣赏最棒的猫猫舞步了吗？", use_tts=False)
        self.energy -= 15  # 跳舞消耗更多能量
        
        # 清屏（兼容不同系统）
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🎵🎵🎵🎵🎵🎵🎵 {self.name}开始表演超级猫猫舞！ 🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵")
        print("按Ctrl+C可提前结束舞蹈...")
        
        # 组合所有舞步（包括新增的5种）
        all_dance_steps = [
            r'''
  ∧___∧  
 ( o.o )  
  \ * /  
   |||  
   |||  
            ''',
            r'''
  ∧___∧  
 ( o.O )  
  / * \  
   | |  
   | |  
            ''',
            r'''
  ∧___∧  
 ( O.O )  
  ~ ~ ~  
   | |  
   | |  
            ''',
            r'''
  ∧___∧  
 ( o.o )  
  \ ~ /  
   |||  
   |||  
            ''',
            r'''
  ∧___∧  
 (@.@ )  
  /^\ \  
  | |  
  | |  
            ''',
            r'''
  ∧___∧  
 (>.< )  
  \_/ \  
   ||  
   ||  
            ''',
            r'''
  ∧___∧  
 (^_^ )  
  \o/ /  
   ||  
   ||  
            ''',
            r'''
  ∧___∧  
 ( -.-)  
  /_/ \  
  | |  
  | |  
            '''
        ] + self.new_dance_steps  # 添加5种新舞蹈
        
        # 更流畅的动画
        try:
            for _ in range(10):  # 增加舞蹈轮数
                for step in all_dance_steps:
                    # 清屏（兼容不同系统）
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"🎵🎵🎵🎵🎵🎵 舞蹈进行中... 能量:{self.energy} 🎵🎵🎵🎵🎵🎵")
                    print(step)
                    time.sleep(0.12)  # 加快舞蹈速度
        except KeyboardInterrupt:
            self.speak("喵呜~舞蹈被中断了")
            return
        
        self.mood = min(10, self.mood + 3)  # 跳舞更多增加心情
        
        # 解锁跳舞成就
        self.check_achievements("dance")
        self.speak("喵哈哈~跳得怎么样？我是不是猫界舞王？")

    def fetch_ball(self):
        """接球游戏"""
        self.speak("⚽⚽ 开始玩高级接球游戏！我会展示超凡的猫猫反应力！", use_tts=False)
        self.energy -= 8  # 游戏消耗更多能量
        
        positions = ["左", "中", "右"]
        score = 0
        round_score = [10, 8, 6, 4, 2]  # 不同回合分数不同
        
        for round in range(1, 6):
            print(f"\n第{round}回合！难度:{7-round}")
            cat_position = random.choice(positions)
            
            # 生成随机球类型
            ball_types = ["⚽⚽足球", "🏀🏀篮球", "🎾🎾网球", "🏐🏐排球", "⚾⚾棒球"]
            ball = random.choice(ball_types)
            
            print(f"{self.name}准备接{ball}...")
            time.sleep(1)
            
            try:
                user_throw = input(f"你想扔到哪? (左/中/右): ").strip()[:1]
            except KeyboardInterrupt:
                self.speak("喵呜~游戏被中断了")
                return
                
            if user_throw == cat_position:
                print(f"🐾🐾🐾🐾 完美接住{ball}! {self.name}太棒了!")
                score += round_score[round-1]
                self.mood = min(10, self.mood + 0.8)
                # 不同球的不同反应
                if ball == "⚽⚽足球":
                    self.speak("喵呜~这个足球真有趣！")
                elif ball == "🎾🎾网球":
                    self.speak("网球弹跳力真好玩！")
            else:
                print(f"😿😿 {self.name}没接到{ball}...")
                self.mood = max(0, self.mood - 0.5)
                if ball == "🏀🏀篮球":
                    self.speak("喵~篮球太大没接住...")
                elif ball == "⚾⚾棒球":
                    self.speak("棒球飞太快了喵...")
            
            print(f"当前分数: {score}")
            time.sleep(1)
        
        # 更丰富的结局
        if score >= 35:
            self.speak(f"喵哈哈！我得了{score}分！我是接球天王！奖励小鱼干！")
            self.mood = min(10, self.mood + 2)
            self.energy += 10
        elif score >= 25:
            self.speak(f"喵~还不错，得了{score}分，继续努力！")
            self.mood = min(10, self.mood + 1)
        elif score >= 15:
            self.speak(f"喵呜...得了{score}分，我需要多练习接球技巧")
        else:
            self.speak(f"呜呜...只得了{score}分，今天状态不好喵~")
            self.mood = max(0, self.mood - 1)
        
        # 解锁成就
        self.check_achievements({"game": "ball", "score": score})
        
        # 显示数字炸弹游戏结果汇总
        try:
            winner = "玩家" if player_won else "猫猫"
            print(f"游戏结果 — 数字炸弹：赢家 = {winner}，炸弹数字 = {bomb}，共猜测次数 = {len(guesses)}")
        except Exception as e:
            print("无法生成数字炸弹结果：", e)

        # 记录游戏记忆
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.memory["memories"].append({
            "date": today,
            "event": f"玩接球游戏得了{score}分",
            "importance": 3
        })
        
        # 更新最喜爱的游戏
        
        # 显示游戏结果汇总（接球）
        print(f"游戏结果 — 接球游戏：得分 {score} 分")
        self.memory["interaction_stats"]["favorite_game"] = "接球"

    def meow_race(self):
        """猫猫赛跑动画（扩充版）"""
        self.speak("🏁🏁🏁🏁🏁🏁🏁🏁 参加超级喵星人赛跑！", use_tts=False)
        self.energy -= 20  # 赛跑消耗更多能量
        
        # 清屏（兼容不同系统）
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁 {self.name}正在参加超级喵星人赛跑！ 🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁")
        print("按任意键加速，Ctrl+C可提前退出")
        
        track_length = 50
        cat_position = 0
        opponents = ["🐈🐈花斑猫", "🐈🐈⬛⬛黑猫", "🐱🐱暹罗猫"]
        opponent_positions = [0, 0, 0]
        
        def draw_race():
            # 清屏（兼容不同系统）
            os.system('cls' if os.name == 'nt' else 'clear')
            print("🏁🏁🏁🏁🏁🏁🏁🏁 超级喵星人赛跑 🏁🏁🏁🏁🏁🏁🏁🏁🏁")
            print(f"{self.name}: [{'>'*cat_position}{' '*(track_length-cat_position)}]")
            for i, op in enumerate(opponents):
                print(f"{op}: [{'>'*opponent_positions[i]}{' '*(track_length-opponent_positions[i])}]")
            print("-" * (track_length + 10))
        
        # 开始比赛
        start_time = time.time()
        while cat_position < track_length and any(op < track_length for op in opponent_positions):
            # 玩家猫移动
            cat_position += random.randint(1, 4)
            if cat_position > track_length:
                cat_position = track_length
            
            # 对手猫移动
            for i in range(len(opponent_positions)):
                opponent_positions[i] += random.randint(1, 3)
                if opponent_positions[i] > track_length:
                    opponent_positions[i] = track_length
            
            # 绘制比赛
            draw_race()
            
            # 检测按键加速
            try:
                if os.name == 'nt':  # Windows
                    import msvcrt
                    if msvcrt.kbhit():
                        msvcrt.getch()
                        cat_position += 3  # 按键加速
                else:  # Linux/Mac
                    import sys, select
                    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                        sys.stdin.read(1)
                        cat_position += 3  # 按键加速
            except:
                pass
            
            time.sleep(0.15)
        
        # 比赛结果
        end_time = time.time()
        race_time = end_time - start_time
        
        # 确定排名
        positions = [cat_position] + opponent_positions
        sorted_positions = sorted(positions, reverse=True)
        rank = sorted_positions.index(cat_position) + 1
        
        # 显示结果
        draw_race()
        print(f"\n比赛结束！{self.name}获得第{rank}名！用时{race_time:.1f}秒")
        # 显示比赛名次与各参赛者位置
        try:
            names = [self.name] + opponents
            positions = [cat_position] + opponent_positions
            rankings = sorted(zip(positions, names), key=lambda x: x[0], reverse=True)
            print("\n比赛排名：")
            for idx, (pos_val, pname) in enumerate(rankings, start=1):
                print(f"  {idx}. {pname} — 距离: {pos_val}")
        except Exception as e:
            print("无法生成赛跑详细排名：", e)

        
        # 奖励
        if rank == 1:
            self.speak("喵哈哈！我是最快的猫！冠军属于我！")
            self.mood = min(10, self.mood + 3)
            self.energy += 15
        elif rank == 2:
            self.speak("喵~差一点就赢了，下次会更好！")
            self.mood = min(10, self.mood + 1)
            self.energy += 8
        else:
            self.speak("喵呜...今天状态不太好，需要多练习")
            self.mood = max(0, self.mood - 1)
            self.energy += 5
        
        # 解锁成就
        self.check_achievements({"game": "race", "rank": rank})
        
        # 记录游戏记忆
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.memory["memories"].append({
            "date": today,
            "event": f"参加赛跑获得第{rank}名",
            "importance": 3
        })
        
        # 更新最喜爱的游戏
        self.memory["interaction_stats"]["favorite_game"] = "赛跑"
    
    def text_adventure_game(self):
        """文字互动游戏（完整修复版）"""
        # 检查能量是否足够
        if self.energy < 12:
            print("喵...本喵太累了，玩不动文字游戏了...zzz")
            return
            
        # 加载故事扩展文件
        stories = self.load_story_extensions()
        if not stories:
            print("喵呜~没有找到任何有效故事文件！请检查stories目录下的json文件格式")
            return
        
        # 让玩家选择故事
        print("\n" + "="*40)
        print("可用的故事列表")
        print("="*40)
        story_titles = list(stories.keys())
        for i, title in enumerate(story_titles, 1):
            print(f"{i}. {title}")
        print(f"{len(story_titles)+1}. 返回")
        print("="*40)
        
        try:
            choice = input("请输入选择的编号: ").strip()
            if choice == str(len(story_titles)+1) or choice.lower() in ['退出', '返回']:
                return
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(story_titles):
                selected_title = story_titles[choice_idx]
                selected_story = stories[selected_title]
                print(f"已选择: {selected_title}")
            else:
                print("无效选择")
                return
        except ValueError:
            print("请输入有效的数字")
            return
        except:
            print("选择故事时出错")
            return
        
        # 初始化游戏状态
        backtrack_count = 3  # 回溯次数
        current_node = selected_story["start_node"]
        story_path = []  # 记录选择路径
        node_stack = []  # 节点栈（用于回溯）
        author_anger_count = 0  # 作者愤怒结局计数
        
        # 游戏主循环
        while True:
            # 检查节点是否存在
            if current_node not in selected_story["nodes"]:
                print(f"错误: 节点 '{current_node}' 不存在于故事中")
                print("喵呜~故事出现错误！游戏终止")
                break
                
            node = selected_story["nodes"][current_node]
            
            # 显示节点内容
            print("\n" + "="*60)
            print(f"回溯次数: {backtrack_count} | 当前节点: {current_node}")
            print("="*60)
            print(node["text"])
            
            # 如果是结局节点，结束游戏
            if node.get("end", False):
                # 直接打印结局信息
                print("\n" + "="*60)
                print(f"故事结束！结局: {node.get('ending_name', '未知结局')}")
                print("="*60)
                print(node["text"])
                print("="*60)
                
                # 处理特殊结局 - 作者的愤怒
                if "作者的愤怒" in node.get("ending_name", ""):
                    author_anger_count += 1
                    if author_anger_count >= 3:
                        # 解锁作者的愤怒4结局
                        print("\n" + "!"*60)
                        print("已触发三次作者的愤怒结局！解锁特殊结局！")
                        print("!"*60)
                        time.sleep(2)
                        
                        # 直接进入结局0
                        current_node = "ending0"
                        continue
                
                # 特殊回溯奖励
                if "backtrack_change" in node:
                    backtrack_change = node["backtrack_change"]
                    backtrack_count += backtrack_change
                    if backtrack_count < 0:
                        backtrack_count = 0
                
                break
            
            # 显示选项
            print("\n【你的选择】:")
            for i, option in enumerate(node.get("options", []), 1):
                text = option.get("text", "无文本选项")
                print(f"{i}. {text}")
            
            # 特殊命令选项
            if node.get("options", []):
                print("\n【特殊命令】:")
                print("b. 回溯到上一个选择点 (消耗1次回溯机会)")
                print("r. 重新开始故事")
                print("q. 退出游戏")
            else:
                print("\n【警告】: 此节点没有选项！")
                break
            
            # 获取玩家选择
            while True:
                try:
                    choice = input("\n输入选择: ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    return
                
                # 特殊命令处理
                if choice == 'b':
                    if backtrack_count <= 0:
                        print("没有回溯次数了！")
                        continue
                    
                    if not node_stack:
                        print("无法回溯，已到故事开头")
                        continue
                    
                    # 回溯到上一个节点
                    backtrack_count -= 1
                    current_node = node_stack.pop()
                    prev_choice = story_path.pop() if story_path else ""
                    print(f"↩️ 回溯成功！回到 '{current_node}'")
                    print(f"剩余回溯次数: {backtrack_count}")
                    if prev_choice:
                        print(f"上次选择: {prev_choice}")
                    break
                
                elif choice == 'r':
                    confirm = input("确定要重新开始故事吗? (y/n): ").lower()
                    if confirm == 'y':
                        # 重置游戏状态
                        backtrack_count = 3
                        current_node = selected_story["start_node"]
                        story_path = []
                        node_stack = []
                        author_anger_count = 0
                        print("🔄 故事已重置！重新开始")
                    continue
                
                elif choice == 'q':
                    confirm = input("确定要退出游戏吗? (y/n): ").lower()
                    if confirm == 'y':
                        print("喵~下次再来继续冒险吧！")
                        return
                    continue
                
                # 处理数字选择
                try:
                    choice_idx = int(choice) - 1
                    options = node.get("options", [])
                    if 0 <= choice_idx < len(options):
                        selected_option = options[choice_idx]
                        
                        # 记录选择路径
                        choice_text = selected_option.get("text", f"选项{choice_idx+1}")
                        story_path.append(f"{current_node} -> {choice_text}")
                        
                        # 显示选择的结果描述
                        print("\n" + "-"*40)
                        print(f"你的选择: {choice_text}")
                        print("-"*40)
                        
                        # 如果选项有描述文本，显示它
                        if "result" in selected_option:
                            print(selected_option["result"])
                            print("-"*40)
                        
                        # 更新回溯次数
                        if "backtrack_change" in selected_option:
                            backtrack_change = selected_option["backtrack_change"]
                            backtrack_count += backtrack_change
                            if backtrack_count < 0:
                                backtrack_count = 0
                        
                        # 压栈当前节点（用于回溯）
                        node_stack.append(current_node)
                        
                        # 转到下一个节点
                        current_node = selected_option.get("next", selected_story["start_node"])
                        break
                    else:
                        print("无效选择")
                except ValueError:
                    # 如果不是数字，可能是节点名（开发者调试用）
                    if choice in selected_story["nodes"]:
                        print("⚡ 开发者模式: 直接跳转到节点")
                        current_node = choice
                        break
                    print("请输入选项编号或特殊命令")
        
        # 游戏结束处理
        if current_node in selected_story["nodes"] and selected_story["nodes"][current_node].get("end", False):
            ending_node = selected_story["nodes"][current_node]
            ending_name = ending_node.get("ending_name", "未知结局")
            
            # 显示结局信息
            print("\n" + "="*60)
            print(f"结局名称: {ending_name}")
            print("="*60)
            print(ending_node["text"])
            print("="*60)
            print(f"结局稀有度: {self.get_ending_rarity(ending_name)}")
            
            # 解锁成就
            self.check_achievements({
                "game": "text_adventure",
                "story": selected_title,
                "ending": ending_name
            })
            
            # 记录游戏记忆
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            self.memory["memories"].append({
                "date": today,
                "event": f"完成了故事'{selected_title}'，结局: {ending_name}",
                "importance": 4
            })
            
            # 更新最喜爱的游戏
            self.memory["interaction_stats"]["favorite_game"] = "文字冒险"
        
        # 暂停一下让玩家阅读结局
        input("\n按回车键返回主菜单...")
    
    def get_ending_rarity(self, ending_name):
        """获取结局稀有度"""
        if "SSR" in ending_name or "通关结局" in ending_name:
            return "SSR"
        elif "SR" in ending_name:
            return "SR"
        else:
            return "R"
        
        # 更新最喜爱的游戏
        self.memory["interaction_stats"]["favorite_game"] = "文字冒险"
    
    def load_story_extensions(self):
        """加载故事扩展文件 - 修复版"""
        stories = {}
        # 确保使用正确的路径
        story_dir = os.path.join(os.path.dirname(__file__), "stories")
        print(f"正在尝试从目录加载故事: {story_dir}")
        
        if not os.path.exists(story_dir):
            try:
                os.makedirs(story_dir)
                print(f"已创建故事目录: {story_dir}")
            except Exception as e:
                print(f"创建故事目录失败: {e}")
            return stories
            
        loaded_count = 0
        for filename in os.listdir(story_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(story_dir, filename)
                try:
                    print(f"尝试加载故事文件: {filename}")
                    with open(filepath, 'r', encoding='utf-8') as f:
                        story_data = json.load(f)
                        
                        # 验证故事格式
                        required_fields = ["title", "start_node", "nodes"]
                        if all(field in story_data for field in required_fields):
                            stories[story_data["title"]] = story_data
                            loaded_count += 1
                            print(f"✓ 成功加载故事: {story_data['title']} (节点数: {len(story_data['nodes'])})")
                        else:
                            missing = [f for f in required_fields if f not in story_data]
                            print(f"✗ 故事文件格式错误: {filename}, 缺少字段: {', '.join(missing)}")
                except json.JSONDecodeError:
                    print(f"✗ JSON格式错误: {filename}")
                except UnicodeDecodeError:
                    print(f"✗ 文件编码问题: {filename}, 请确保使用UTF-8编码")
                except Exception as e:
                    print(f"✗ 加载故事失败 {filename}: {str(e)}")
        
        print(f"故事加载完成: {loaded_count}个故事加载成功")
        return stories
        

    def play_hide_and_seek(self):
        """捉迷藏游戏（扩充版）"""
        self.speak("喵~ 我们来玩捉迷藏吧！数到10就来找我哦！", use_tts=False)
        self.energy -= 12
        
        # 随机选择一个场景
        scene = random.choice(list(self.hiding_scenes.keys()))
        hiding_spots = self.hiding_scenes[scene]
        chosen_spot = random.choice(hiding_spots)
        
        # 告诉玩家在哪个场景
        self.speak(f"我们正在{scene}玩捉迷藏哦！", use_tts=False)
        time.sleep(1)
        
        # 倒计时
        for i in range(10, 0, -1):
            print(f"{i}...")
            time.sleep(0.8)
        
        # 清屏（兼容不同系统）
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"时间到！在{scene}开始找我吧！")
        print(f"可能的藏身地点: {', '.join(hiding_spots)}")
        
        attempts = 0
        max_attempts = 4
        found = False
        while attempts < max_attempts:
            try:
                guess = input(f"第{attempts+1}次猜测: ").strip()
            except KeyboardInterrupt:
                self.speak("喵呜~游戏被中断了")
                return
                
            if not guess:
                print("请输入一个位置")
                continue
                
            attempts += 1
            
            if guess == chosen_spot:
                self.speak("喵呜~被你找到了！好厉害！")
                self.mood = min(10, self.mood + 1)
                found = True
                break
            else:
                # 给提示
                if attempts == max_attempts - 1:
                    print("最后一次机会了！")
                elif random.random() > 0.5:
                    # 50%概率给线索
                    clue_types = [
                        "不在家具下面",
                        "不在靠窗的地方",
                        "在比较隐蔽的角落",
                        "在房间的某个边缘",
                        "在比较高的地方",
                        "在比较低的地方",
                        "在绿色植物附近"
                    ]
                    clue = random.choice(clue_types)
                    print(f"提示: {clue}")
                else:
                    print("不对哦，再猜猜看！")
        
        if not found:
            self.speak(f"喵哈哈！我藏在{scene}的{chosen_spot}！你没找到我！")
            self.mood = min(10, self.mood + 1.5)
            self.energy += 5
        
        # 解锁成就
        
        # 显示捉迷藏结果
        if found:
            print(f"游戏结果 — 捉迷藏：你找到了猫猫！藏身地点：{chosen_spot}")
        else:
            print(f"游戏结果 — 捉迷藏：你没找到猫猫，猫猫藏在：{chosen_spot}")
        self.check_achievements({
            "game": "hide_and_seek", 
            "found": found,
            "scene": scene,
            "won": not found  # 猫猫赢了
        })
        
        # 记录记忆
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if found:
            self.memory["memories"].append({
                "date": today,
                "event": f"在{scene}的捉迷藏中被找到了",
                "importance": 3
            })
        else:
            self.memory["memories"].append({
                "date": today,
                "event": f"在{scene}的{chosen_spot}成功躲藏",
                "importance": 4
            })
        
        # 更新最喜爱的游戏
        self.memory["interaction_stats"]["favorite_game"] = "捉迷藏"
        self.memory["interaction_stats"]["favorite_scene"] = scene

    def number_bomb_game(self):
        """数字炸弹游戏（扩展版）"""
        self.speak("💣💣 开始玩数字炸弹游戏！猜数字要小心哦~", use_tts=False)
        self.energy -= 10
        
        # 设置炸弹范围
        min_num = 1
        max_num = 1000
        bomb = random.randint(min_num, max_num)
        
        print(f"\n数字炸弹已埋藏在 {min_num} 到 {max_num} 之间！")
        print("规则: 玩家和猫猫轮流猜数字，猜中炸弹的人就输了！")
        print("输入'退出'可以随时结束游戏")
        print("游戏开始！")
        
        current_player = "玩家"  # 玩家先开始
        game_over = False
        guesses = []
        player_won = False
        
        while not game_over:
            if current_player == "玩家":
                try:
                    guess = input(f"\n你的猜测 ({min_num}-{max_num}): ")
                    if guess.lower() in ['退出', '结束']:
                        self.speak("喵~游戏结束")
                        return
                        
                    guess = int(guess)
                except ValueError:
                    print("请输入有效数字！")
                    continue
            else:  # 猫猫的回合
                # 智能猜测算法
                if not guesses:
                    # 第一次猜测，选择中间值
                    guess = (min_num + max_num) // 2
                else:
                    # 根据范围缩小猜测
                    if bomb > guesses[-1]:
                        min_num = max(min_num, guesses[-1] + 1)
                    else:
                        max_num = min(max_num, guesses[-1] - 1)
                    
                    # 在安全范围内随机猜测
                    safe_range = list(range(min_num, max_num + 1))
                    # 排除已猜过的数字
                    safe_range = [num for num in safe_range if num not in guesses]
                    
                    if safe_range:
                        guess = random.choice(safe_range)
                    else:
                        guess = random.randint(min_num, max_num)
                
                print(f"🐱 {self.name}的猜测: {guess}")
                time.sleep(1)  # 增加一点延迟，让游戏更有趣
            
            # 检查猜测是否正确
            if guess == bomb:
                if current_player == "玩家":
                    self.speak(f"轰！你猜中了炸弹数字 {bomb}！你输了喵~")
                    self.mood = min(10, self.mood + 2)
                    self.energy += 5
                    player_won = False
                else:
                    self.speak(f"轰！我猜中了炸弹数字 {bomb}！我输了喵~")
                    self.mood = max(0, self.mood - 1)
                    player_won = True
                game_over = True
            else:
                # 更新范围
                if guess < bomb:
                    min_num = max(min_num, guess + 1)
                    print(f"炸弹在 {guess} 和 {max_num} 之间")
                else:
                    max_num = min(max_num, guess - 1)
                    print(f"炸弹在 {min_num} 和 {guess} 之间")
                
                # 添加到已猜列表
                guesses.append(guess)
                
                # 切换玩家
                current_player = "猫猫" if current_player == "玩家" else "玩家"
        
        # 记录游戏记忆
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.memory["memories"].append({
            "date": today,
            "event": f"玩数字炸弹游戏 {'赢了' if player_won else '输了'}",
            "importance": 3
        })
        
        # 更新最喜爱的游戏
        self.memory["interaction_stats"]["favorite_game"] = "数字炸弹"
        
        # 解锁成就
        self.check_achievements({
            "game": "bomb",
            "won": player_won
        })

# 主程序
def main():
    print("""
    🐱🐱🐱🐱🐱 超级智能猫猫伴侣 🐱🐱🐱🐱🐱
      作者: FROBread | 版本: 6.3 (集成DeepSeek)
      一只通过记忆训练获得知识的聪明猫咪
    """)
    
    # 检查配置是否存在
    config_file = "cat_config.json"
    cat_name = ""
    
    # 尝试加载现有配置
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                cat_name = config.get('cat_name', '')
                if cat_name:
                    print(f"发现已有猫猫: {cat_name}")
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    # 获取猫猫名字
    if cat_name:
        use_existing = input(f"发现已有猫猫 '{cat_name}'，是否使用? (y/n): ").strip().lower()
        if use_existing == 'y':
            pass  # 使用现有猫猫
        else:
            cat_name = ""
    
    if not cat_name:
        cat_name = input("给你的猫猫取个名字: ").strip() or "喵星人"
    
    # 创建猫猫
    try:
        # 显示加载动画
        print("\n初始化中...")
        smart_cat = SmartCat(cat_name, config_file)
        
        # 欢迎信息
        welcome_msg = f"""
        你好！我是{smart_cat.name}，一只{smart_cat.color}的{smart_cat.cat_type}猫！
        版本: {smart_cat.version} | 作者: {smart_cat.author}
        我今年{smart_cat.age}岁，性格{smart_cat.personality}。
        我已经掌握了{sum(len(v) for v in smart_cat.knowledge_base.values())}条知识！
        """
        smart_cat.speak(welcome_msg)
        
        # 显示猫猫信息
        print(f"\n{'='*40}")
        print(f"智能猫猫: {smart_cat.name}")
        print(f"版本: {smart_cat.version} | 作者: {smart_cat.author}")
        print(f"类型: {smart_cat.cat_type} | 性格: {smart_cat.personality}")
        print(f"知识量: {sum(len(v) for v in smart_cat.knowledge_base.values())}条")
        print(f"心情: {smart_cat.mood}/10 | 能量: {smart_cat.energy}")
        print(f"DeepSeek: {'已启用' if smart_cat.use_deepseek and smart_cat.deepseek_api_key else '未启用'}")
        print(f"{'='*40}\n")
        
        # 解锁初次见面成就
        smart_cat.check_achievements("first_boot")
        
    except Exception as e:
        print(f"创建猫猫失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 主循环
    while True:
        print("\n===== 主菜单 =====")
        print(f"猫猫: {smart_cat.name} | 心情: {smart_cat.mood}/10 | 能量: {smart_cat.energy}")
        print("1. 与DeepSeek猫猫聊天")
        print("2. 向猫猫提问")
        print("3. 训练猫猫新知识")
        print("4. 查看猫猫的知识库")
        print("5. 查看学习历史")
        print("6. 和猫猫玩游戏")
        print("7. 喂食补充能量")
        print("8. 休息")
        print("9. 配置DeepSeek API")
        print("10. 查看成就")
        print("11. 扩展库管理")  # 新增选项
        print("0. 退出")
        
        # 在菜单底部添加温馨提示
        print("\n" + "="*70)
        print("温馨提示:                                  赞助者：XMJ_js")
        print("1. Deepseek猫猫聊天功能仅推荐有Key（密钥）的人使用，我们会在未来为大家提供免费的接口！")
        print("2. “向猫猫提问”功能暂不支持CN地区（懂得都懂）但提问扩展知识库仍需用到")
        print("="*70)
        
        try:
            choice = input("\n请选择: ").strip()
        except KeyboardInterrupt:
            print("\n程序已中断")
            break
        
        if choice == '1':
            smart_cat.deepseek_chat()
                
        elif choice == '2':
            print("\n你可以问我任何问题！(输入'退出'结束)")
            while True:
                try:
                    question = input("\n你的问题: ").strip()
                except KeyboardInterrupt:
                    break
                
                if not question:
                    continue
                if question.lower() in ['退出', '结束', '返回']:
                    break
                
                # 回答问题
                answer = smart_cat.answer_question(question)
                smart_cat.speak(answer)
        
        elif choice == '3':
            teacher = input("请告诉我你叫什么名字（可留空）: ").strip()
            smart_cat.train_new_knowledge(teacher)
            
        elif choice == '4':
            print("\n📚📚📚📚📚📚📚📚📚📚 猫猫知识库 📚📚📚📚📚📚📚📚📚📚📚")
            print("请选择知识库分类:")
            
            # 创建分类列表（包括扩展知识）
            categories = list(smart_cat.knowledge_base.keys()) 
            if smart_cat.knowledge_extensions:
                categories += list(smart_cat.knowledge_extensions.keys())
                categories += ["扩展知识"]  # 单独显示扩展知识
            
            # 去重并排序
            categories = sorted(set(categories))
            
            # 显示所有分类
            for i, category in enumerate(categories, 1):
                if category in smart_cat.knowledge_base:
                    count = len(smart_cat.knowledge_base[category])
                    print(f"{i}. {category} ({count}条)")
                elif category in smart_cat.knowledge_extensions:
                    count = len(smart_cat.knowledge_extensions[category])
                    print(f"{i}. {category} (扩展, {count}条)")
                elif category == "扩展知识":
                    ext_count = sum(len(k) for k in smart_cat.knowledge_extensions.values())
                    print(f"{i}. 所有扩展知识 ({ext_count}条)")
            
            print(f"{len(categories)+1}. 返回主菜单")
            
            try:
                cat_choice = input("\n选择分类编号: ").strip()
                if cat_choice == str(len(categories)+1) or cat_choice.lower() in ['退出', '返回']:
                    continue
                    
                cat_idx = int(cat_choice) - 1
                if 0 <= cat_idx < len(categories):
                    selected_category = categories[cat_idx]
                else:
                    print("无效选择")
                    continue
            except:
                print("输入错误")
                continue
            
            # 显示知识库内容
            print(f"\n=== {selected_category}知识 ===")
            
            # 显示原始知识库
            if selected_category in smart_cat.knowledge_base:
                knowledge = smart_cat.knowledge_base[selected_category]
                for i, (q, a) in enumerate(knowledge.items()):
                    if i >= 15:  # 每类最多显示15条
                        print(f"  还有{len(knowledge)-15}条知识...")
                        break
                    print(f"  Q: {q}")
                    print(f"  A: {a[:60]}{'...' if len(a) > 60 else ''}")
            
            # 显示扩展知识
            elif selected_category in smart_cat.knowledge_extensions:
                knowledge = smart_cat.knowledge_extensions[selected_category]
                for i, (q, a) in enumerate(knowledge.items()):
                    if i >= 15:  # 每类最多显示15条
                        print(f"  还有{len(knowledge)-15}条知识...")
                        break
                    print(f"  Q: {q}")
                    print(f"  A: {a[:60]}{'...' if len(a) > 60 else ''}")
            
            # 显示所有扩展知识
            elif selected_category == "扩展知识":
                for ext_category, knowledge in smart_cat.knowledge_extensions.items():
                    print(f"\n  --- {ext_category} ---")
                    for i, (q, a) in enumerate(knowledge.items()):
                        if i >= 5:  # 每个扩展分类最多显示5条
                            print(f"    还有{len(knowledge)-5}条知识...")
                            break
                        print(f"    Q: {q}")
                        print(f"    A: {a[:50]}{'...' if len(a) > 50 else ''}")
            
            # 显示扩展文件信息
            if selected_category == "扩展知识" or selected_category in smart_cat.knowledge_extensions:
                print("\n📝 扩展知识库说明:")
                print("扩展知识存储在 knowledge_extensions 文件夹中")
                print("创建新的JSON文件格式: ")
                print('''{
    "category": "新分类名称",
    "knowledge": {
        "问题1": "答案1",
        "问题2": "答案2"
    }
}''')
            
            input("\n按回车返回主菜单")
            
        elif choice == '5':
            print("\n📅📅📅📅📅📅📅📅📅📅 学习历史记录 📅📅📅📅📅📅📅📅📅")
            print(f"共有{len(smart_cat.training_history)}次学习记录\n")
            for record in smart_cat.training_history[-10:]:  # 显示最近10条
                print(f"[{record['date']}]")
                print(f"  类别: {record['category']}")
                print(f"  问题: {record['question']}")
                if 'answer_snippet' in record:
                    print(f"  答案摘要: {record['answer_snippet']}")
            input("\n按回车返回主菜单")
            
        elif choice == '6':
            print("\n🎮🎮🎮🎮🎮🎮🎮🎮 游戏菜单 🎮🎮🎮🎮🎮🎮🎮🎮")
            print("1. 猫猫跳舞")
            print("2. 接球游戏")
            print("3. 喵星人赛跑")
            print("4. 捉迷藏")
            print("5. 数字炸弹游戏")
            print("6. 文字互动冒险")  # 新增文字互动游戏
            print("7. 返回主菜单")
            
            try:
                game_choice = input("选择游戏: ").strip()
            except KeyboardInterrupt:
                continue
            
            if game_choice == '1':
                smart_cat.dance()
            elif game_choice == '2':
                smart_cat.fetch_ball()
            elif game_choice == '3':
                smart_cat.meow_race()
            elif game_choice == '4':
                smart_cat.play_hide_and_seek()
            elif game_choice == '5':
                smart_cat.number_bomb_game()
            elif game_choice == '6':  # 文字互动游戏
                smart_cat.text_adventure_game()
            elif game_choice == '7':
                continue
            else:
                print("无效选择")
                
            # 解锁第一次游戏成就
            smart_cat.check_achievements("first_game")
                
        elif choice == '7':
            foods = ["小鱼干", "猫罐头", "营养膏", "鸡胸肉", "冻干", "三文鱼", "金枪鱼", "猫薄荷"]
            food = random.choice(foods)
            smart_cat.speak(f"喵~谢谢你喂我吃{food}！好幸福~")
            smart_cat.energy = min(100, smart_cat.energy + 30)
            smart_cat.mood = min(10, smart_cat.mood + 1.5)
            
            # 记录喂食记忆
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            smart_cat.memory["memories"].append({
                "date": today,
                "event": f"吃了美味的{food}",
                "importance": 3
            })
            
            smart_cat.save_config()
            
        elif choice == '8':
            rest_time = random.randint(3, 8)
            smart_cat.speak(f"喵~我去休息{rest_time}秒钟...zzz")
            
            # 休息动画
            for i in range(rest_time):
                print(f"休息中... {rest_time-i}秒")
                time.sleep(1)
                
            smart_cat.energy = min(100, smart_cat.energy + 50)
            smart_cat.mood = min(10, smart_cat.mood + 2)
            smart_cat.speak("喵呜~我回来啦！精力充沛！")
            smart_cat.save_config()
            
        elif choice == '9':
            print("\n🔧🔧🔧🔧🔧🔧🔧🔧🔧 DeepSeek API 配置 🔧🔧🔧🔧🔧🔧🔧🔧🔧")
            print("1. 启用/禁用 DeepSeek")
            print("2. 设置 API 密钥")
            print("3. 测试 DeepSeek 连接")
            print("4. 设置 猫猫 人格")
            print("5. 返回主菜单")
            
            try:
                config_choice = input("选择操作: ").strip()
            except KeyboardInterrupt:
                continue
            
            if config_choice == '1':
                smart_cat.use_deepseek = not smart_cat.use_deepseek
                status = "启用" if smart_cat.use_deepseek else "禁用"
                smart_cat.speak(f"喵~已{status}DeepSeek API支持")
                smart_cat.save_config()
                
            elif config_choice == '2':
                print("请访问 https://platform.deepseek.com/ 获取API密钥")
                api_key = input("输入DeepSeek API密钥: ").strip()
                if api_key:
                    smart_cat.deepseek_api_key = api_key
                    smart_cat.use_deepseek = True
                    smart_cat.speak("喵~API密钥已设置！已自动启用DeepSeek支持")
                    smart_cat.save_config()
                else:
                    smart_cat.speak("喵呜~未提供有效API密钥")
                    
            elif config_choice == '3':
                if not smart_cat.deepseek_api_key:
                    smart_cat.speak("喵~请先设置API密钥")
                    continue
                    
                smart_cat.speak("喵~正在测试DeepSeek连接...")
                test_question = "猫为什么喜欢盒子？"
                response = smart_cat.answer_with_deepseek([{"role": "user", "content": test_question}])
                
                if response:
                    print(f"\n测试问题: {test_question}")
                    print(f"DeepSeek响应: {response[:200]}")
                    smart_cat.speak("喵哈哈~DeepSeek连接成功！")
                else:
                    smart_cat.speak("喵呜~DeepSeek连接失败，请检查API密钥")
                
            elif config_choice == '4':
                personalities = {
                    "1": "猫猫助手",
                    "2": "学术专家",
                    "3": "简明风格",
                    "4": "哲学猫",        # 新增人格
                    "5": "幽默大师",      # 新增人格
                    "6": "诗歌诗人",      # 新增人格
                    "7": "科幻迷",        # 新增人格
                    "8": "历史学者"       # 新增人格
                }
                print("\n选择猫猫人格:")
                print("1. 猫猫助手 - 可爱风格，包含喵星人元素")
                print("2. 学术专家 - 严谨专业风格")
                print("3. 简明风格 - 简洁直接的风格")
                print("4. 哲学猫 - 深度思考，探讨生命的意义")        # 新增
                print("5. 幽默大师 - 用幽默的方式回答问题")         # 新增
                print("6. 诗歌诗人 - 用优美的诗句回答问题")         # 新增
                print("7. 科幻迷 - 从未来科技的角度思考问题")        # 新增
                print("8. 历史学者 - 从历史发展的角度分析问题")      # 新增
                
                try:
                    personality_choice = input("选择人格 (1-8): ").strip()
                except KeyboardInterrupt:
                    continue
                
                if personality_choice in personalities:
                    smart_cat.deepseek_personality = personalities[personality_choice]
                    smart_cat.speak(f"喵~已设置DeepSeek人格为: {smart_cat.deepseek_personality}")
                    smart_cat.save_config()
                else:
                    smart_cat.speak("喵~无效选择，人格未改变")
                    
            elif config_choice == '5':
                continue
                
        elif choice == '10':
            print("\n🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆 成就系统 🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆")
            total = len(smart_cat.achievements)
            unlocked = sum(1 for a in smart_cat.achievements.values() if a["achieved"])
            print(f"总成就数: {total} | 已解锁: {unlocked} | 进度: {unlocked/total*100:.1f}%")
            
            print("\n=== 已解锁成就 ===")
            for ach_id, achievement in smart_cat.achievements.items():
                if achievement["achieved"]:
                    print(f"  🏅🏅🏅🏅🏅🏅🏅 [{achievement['date']}] {achievement['name']}")
                    print(f"      {achievement['description']}")
            
            print("\n=== 未解锁成就 ===")
            for ach_id, achievement in smart_cat.achievements.items():
                if not achievement["achieved"]:
                    print(f"  🔒🔒🔒🔒 {achievement['name']}")
                    print(f"      {achievement['description']}")
            
            input("\n按回车返回主菜单")
            
        elif choice == '11':  # 扩展库管理
            print("\n📚📚📚📚📚📚📚📚📚📚📚 扩展库管理📚📚📚📚📚📚📚📚📚📚📚📚")
            print("1. 下载知识扩展库")
            print("2. 下载故事扩展库")
            print("3. 返回主菜单")
            
            try:
                ext_choice = input("请选择操作: ").strip()
            except KeyboardInterrupt:
                continue
            
            if ext_choice == '1':
                if smart_cat.download_knowledge_extension():
                    # 更新成就
                    smart_cat.unlock_achievement("extension_collector")
                input("\n按回车返回...")
                
            elif ext_choice == '2':
                smart_cat.download_story_extension()
                input("\n按回车返回...")
                
            elif ext_choice == '3':
                continue
                    
            
        elif choice == '0':
            smart_cat.speak("喵...下次再玩哦! 记得每天训练我，我会变得更聪明！")
            smart_cat.save_config()
            break
            
        else:
            print("无效的选择，请重新输入")
        
        # 每次交互后检查成就
        smart_cat.check_achievements()

if __name__ == "__main__":
    # 检查并安装必要库
    required_libs = {
        "pyttsx3": "pyttsx3",
        "requests": "requests",
        "wikipedia": "wikipedia",
        "html": "html"
    }
    
    print("正在检查依赖库...")
    for lib, pkg in required_libs.items():
        try:
            __import__(lib)
            print(f"  ✓ {lib} 已安装")
        except ImportError:
            print(f"  ✗✗ {lib} 未安装，正在安装...")
            os.system(f"pip install {pkg}")
    
    # 运行主程序
    try:
        main()
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车退出...")