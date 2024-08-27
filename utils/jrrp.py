import datetime,random,sqlite3
# ----------------------------预设值----------------------------  开始

# jrrp图片链接（如https://static.axtn.net/axtbot/0.jpg，则填入https://static.axtn.net/axtbot/，带末尾斜杠/）
image_url = "https://static.axtn.net/axtbot/"
# image_url = "https://static.shanshui.site/axtbot/"

# 自定义jrrp（开关打开时，以下带*号必填）
custom = False  # 开关 *
cusjrrp = 100 # jrrp值 *
custom1 = "龙行龘龘 | AxT社区祝您新春快乐" # 段落1 
custom2 = "瑞兔辞旧去，龙腾新年来 在这辞旧迎新的美好时刻，AxT社区携全体员工给您拜年啦！" # 段落2 
custom3 = "在这喜庆的日子，祝您在新的一年里：万事如意，心想事成，顺风顺水顺财神！过龙年，用龙图，祝您在龙年里：有着龙马精神，鱼跃龙门，心想事成" # 段落3 
img = "https://static.axtn.net/axtbot/100.jpg" # 图片URL 
cus_size = "#264px #100px" # 图片尺寸 *

# 默认尺寸
size_0 = "#300px #100px"
size_1_20 = "#87px #100px"
size_21_40 = "#125px #100px"
size_41_60 = "#120px #100px"
size_61_80 = "#100px #100px"
size_81_99 = "#115px #100px"
size_100 = "#264px #100px"

# markdown 模板ID
custom_template_id = "102076583_1704852177"

# 数据库名称
default_database = "jrrp.db"
custom_database = "customjrrp.db"

# ----------------------------预设值----------------------------  结束



# ----------------------------主代码----------------------------  开始
async def get_jrrp(message): # 主操作
    await update_database()  # 更新数据表
    member_id = str(message.author.member_openid)  # 获取用户ID
    current_date = datetime.datetime.now().strftime("%Y%m%d")  # 获取系统时间
    if type(cusjrrp) == int and custom:
        jrrp = cusjrrp  # ----> 如果自定义打开并设定了正确的cusjrrp值，则将其定为默认值
    else:
        if member_id == 'DB6189E68D0C2D9EB79DB508B38E7594' and current_date == '20240712':
            jrrp = 100
        elif member_id == '652410AFBBF085268E7B9E6FEF2E3690' and current_date == '20240713':
            jrrp = 100
        else:
            jrrp = random.randint(0, 100)  # ----> 如果任意一条不符合，则生成随机数
    return await update_jrrp(member_id, jrrp) # 写数据库

async def update_jrrp(memid, jrrp): # 写数据库信息
    current_date = datetime.datetime.now().strftime("%Y%m%d")  # 获取系统时间
    if type(cusjrrp) == int and custom:
        conn = sqlite3.connect(custom_database) 
    else:    
        conn = sqlite3.connect(default_database)  # 链接jrrp.db
    cursor = conn.cursor()  # 指针选中
    table_name = f"今日人品表_{current_date}"  # 切换表头到当日时间
    cursor.execute(f"SELECT number FROM {table_name} WHERE id = ?", (memid,)) # 查询是否存在此人的信息记录
    result = cursor.fetchone()  # 结果
    if result:
        number = result[0]  # 选中此人的jrrp值
        conn.close()  # 关闭数据库
        return f'''  
您今天已经获取过人品值啦
您的人品值是: {number}''',0  # 返回获取完毕的值和msg_type
# 详见https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/send.html#群聊
    else:  # 此人不在数据库中有记录（即没进行jrrp操作）
        cursor.execute(f"INSERT INTO {table_name} (id, number) VALUES (?, ?)", (memid, jrrp))  # 插入信息
        conn.commit()  # 提交
        conn.close()  # 关闭
        if await content_load(jrrp) == "error":
            return f'''
======AxTBot======
错误：请联系管理员处理
详细信息：传入jrrp超出预期值
当前值:{jrrp}
==================''',0
        else:
            return await content_load(jrrp),2  # 返回这个函数的值，这个函数会通过jrrp判断要写的内容并返回一个markdown

# 更新数据库
async def update_database():
    current_date = datetime.datetime.now().strftime("%Y%m%d")  # 当日时间
    if type(cusjrrp) == int and custom:
        conn = sqlite3.connect(custom_database) 
    else:    
        conn = sqlite3.connect(default_database)  # 链接jrrp.db
    cursor = conn.cursor()  # 指针
    table_name = f"今日人品表_{current_date}"  # 列表
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY, number INTEGER)")  # 新开一个
    conn.commit()  # 提交
    conn.close()  # 关闭

async def content_load(jrrpnumber):  # 通过jrrp值判断输出内容
    paragraph1,paragraph2,paragraph3,image,imgsize = await jrrp_note(jrrpnumber)
    if paragraph1 == 0:
        return "error"
    else:
        content = {  # 构建消息串（用于Markdown）
		    "custom_template_id": custom_template_id,  # 模板ID
    	    "params": [
                {
				    "key": "jrrpnumber","values": [str(jrrpnumber)]
	    		},{
			    	"key": "paragraph1","values": [paragraph1]
    			},{
		    		"key": "paragraph2","values": [paragraph2]
        		},{
	        		"key": "paragraph3","values": [paragraph3]
        		},{
    	    		"key": "image","values": [image]
        		},{
    	    		"key": "imgsize","values": [imgsize]
        		}
	       	]
	    }
        return content  # 返回这个值用于发送markdown

async def jrrp_note(jrrpnumber):
    if custom:  # 特殊的地方
        paragraph1 = custom1
        paragraph2 = custom2
        paragraph3 = custom3
        image = img
        imgsize = '[' + 'img' + cus_size + ']'
    elif jrrpnumber == 0:  # 为0，下同
        paragraph1 = "你竟然抽到了最罕见的0！"  # 第一行，下同
        paragraph2 = "你今天所作的一切将会变得非常sad"  # 第二行，下同
        paragraph3 = " "  # 第三行，下同
        image = f"{image_url}0.jpg"  # 图片地址，下同
        imgsize = '[' + 'img' + size_0 + ']'
    elif jrrpnumber > 0 and jrrpnumber < 21:
        paragraph1 = "你今天可能会遭遇很多困难"
        paragraph2 = "加油吧！少年！"
        paragraph3 = " "
        image = f"{image_url}1-20.jpg"
        imgsize = '[' + 'img' + size_1_20 + ']'
    elif jrrpnumber > 20 and jrrpnumber < 41:
        paragraph1 = "还好啦，今天可能不会那么幸运"
        paragraph2 = "努努力！明天或许会抽到更好的！"
        paragraph3 = " "
        image = f"{image_url}21-40.jpg"
        imgsize = '[' + 'img' + size_21_40 + ']'
    elif jrrpnumber > 40 and jrrpnumber < 61:
        paragraph1 = "也许是中等人品（？"
        paragraph2 = "你今天会过的很平凡"
        paragraph3 = "幸运和遭遇会同时向你奔来"
        image = f"{image_url}41-60.jpg"
        imgsize = '[' + 'img' + size_41_60 + ']'
    elif jrrpnumber > 60 and jrrpnumber < 81:
        paragraph1 = "你今天可能会大部分时间被幸运眷顾"
        paragraph2 = "但一定要注意！遭遇也可能会偷偷来袭！"
        paragraph3 = " "
        image = f"{image_url}61-80.jpg"
        imgsize = '[' + 'img' + size_61_80 + ']'
    elif jrrpnumber > 80 and jrrpnumber < 100:
        paragraph1 = "哇！你今天的人品真好唉"
        paragraph2 = "或许可以买张CP？（bushi"
        paragraph3 = " "
        image = f"{image_url}81-99.jpg"
        imgsize = '[' + 'img' + size_81_99 + ']'
    elif jrrpnumber == 100:
        paragraph1 = "你抽到了最高人品值！！！"
        paragraph2 = "幸运的人类，你将会幸运的度过一整天！"
        paragraph3 = " "
        image = f"{image_url}100.jpg"
        imgsize = '[' + 'img' + size_100 + ']'
    else:
        print (f"未知的jrrp参数：{jrrpnumber}") # 若确实如此，直接返回此内容并返回00000，不再运行
        return 0,0,0,0,0
    return paragraph1,paragraph2,paragraph3,image,imgsize

# ----------------------------主代码----------------------------  结束
