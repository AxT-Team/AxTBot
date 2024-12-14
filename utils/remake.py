import datetime
import random
import sqlite3
import os
import json

# ----------------------------预设值----------------------------  开始

# 自定义节日内容（开关打开时，以下带*号必填）
custom = False  # 开关 *
custom_location = "上海·AxT社区"  # 地点 
custom_objects = "Darf"  # 人物/动物/物

remake_default_set = {
    "locations": [
        "东京，日本", "巴黎，法国", "纽约，美国", "伦敦，英国", "北京，中国", "悉尼，澳大利亚",
        "洛杉矶，美国", "上海，中国", "巴西", "开罗，埃及", "马德里，西班牙", "墨尔本，澳大利亚",
        "阿姆斯特丹，荷兰", "柏林，德国", "莫斯科，俄罗斯", "新德里，印度", "曼谷，泰国", "伊斯坦布尔，土耳其",
        "雅加达，印度尼西亚", "罗马，意大利", "香港，中国", "台北，台湾", "吉隆坡，马来西亚", "迪拜，阿联酋",
        "拉斯维加斯，美国", "开普敦，南非", "布宜诺斯艾利斯，阿根廷", "墨西哥城，墨西哥", "圣保罗，巴西",
        "圣彼得堡，俄罗斯", "曼谷，泰国", "吉达，沙特阿拉伯", "卡萨布兰卡，摩洛哥", "卡尔加里，加拿大",
        "新加坡，新加坡", "巴黎岛，印尼", "巴黎的近郊（如凡尔赛），法国", "孟买，印度", "温哥华，加拿大"
    ],
    "objects": [
        "沙子", "玻璃", "电线", "电池", "油漆", "砖块", "橡胶", "铁矿", "黄金", "钻石", "煤炭", "塑料", "木板",
        "石灰石", "水桶", "木雕", "陶器", "皮革", "绸缎", "银器", "玻璃瓶", "钢铁", "木箱", "塑料袋", "镜子",
        "手电筒", "书本", "背包", "手表", "手机", "钥匙", "鞋子", "帽子", "腰带", "手套", "眼镜", "雨伞", "钓鱼竿",
        "狮子", "老虎", "大象", "长颈鹿", "袋鼠", "熊猫", "海豚", "鲨鱼", "鲸鱼", "狼", "狐狸", "兔子", "鹿", "野猪",
        "猴子", "大猩猩", "鹦鹉", "鹰", "鸽子", "蛇", "鳄鱼", "蜥蜴", "乌龟", "海龟", "蚂蚁", "蜜蜂", "蝴蝶", "苍蝇",
        "蜻蜓", "蚊子", "螳螂", "章鱼", "螃蟹", "海星", "海胆", "鲸鲨", "珊瑚", "虾", "鳗鱼", "鳍足动物", "斑马",
        "阿尔伯特·爱因斯坦", "玛丽·居里", "李白", "莎士比亚", "达芬奇", "达芬", "爱迪生", "丘吉尔", "比尔·盖茨",
        "史蒂夫·乔布斯", "林肯·佩里", "贝多芬", "巴赫", "齐白石", "尼尔·阿姆斯特朗", "奥黛丽·赫本", "马云",
        "唐纳德·特朗普", "弗朗茨·卡夫卡", "迈克尔·杰克逊", "李光耀", "彭博", "卡尔·马克思"
    ]
}

# 数据库名称
default_database = "remake.db"

# ----------------------------预设值----------------------------  结束

# ----------------------------主代码----------------------------  开始
async def remake(member_id):
    await update_database()  # 更新数据表
    return await update_db(member_id)  # 写数据库 ----> 如果未开启自定义，则令其随机

async def get_remake_data():
    if not os.path.exists("./data/remake.json"):
        os.mkdir('data')
        with open('./data/remake.json', 'w', encoding='utf-8') as file:
            json.dump(remake_default_set, file, ensure_ascii=False, indent=4)
    if custom:
        global custom_location, custom_objects
        location, objects = custom_location, custom_objects
    else:
        with open('./data/remake.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        location = random.choice(data["locations"])
        objects = random.choice(data["objects"])
    return location, objects

async def update_db(memid):  # 写数据库信息
    current_date = datetime.datetime.now().strftime("%Y%m%d")  # 获取系统时间
    conn = sqlite3.connect(default_database)  # 链接db
    cursor = conn.cursor()  # 指针选中
    table_name = f"表_{current_date}"  # 切换表头到当日时间
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY, location TEXT, objects TEXT)")  # 创建表

    # 查询是否存在此人的信息记录
    result = cursor.execute(f"SELECT location, objects FROM {table_name} WHERE id = ?", (memid,)).fetchone()
    
    if result:  # 如果已经有记录
        location, objects = result
        conn.close()  # 关闭数据库
        return f'''您今天已经重开过啦！再重开的话天堂就要过载啦！
您今天重开的地点是: {location}，是 {objects}'''
    else:  # 此人不在数据库中有记录
        location, objects = await get_remake_data()
        cursor.execute(f"INSERT INTO {table_name} (id, location, objects) VALUES (?, ?, ?)", (memid, location, objects))  # 插入信息
        conn.commit()  # 提交
        conn.close()  # 关闭
        return f"重开成功！祝您重开愉快！\n您重开的地点是：{location}，是：{objects}"

# 更新数据库
async def update_database():
    current_date = datetime.datetime.now().strftime("%Y%m%d")  # 当日时间
    conn = sqlite3.connect(default_database)  # 链接remake.db
    cursor = conn.cursor()  # 指针
    table_name = f"remake表_{current_date}"  # 列表
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY, location TEXT, objects TEXT)")  # 创建表
    conn.commit()  # 提交
    conn.close()  # 关闭
