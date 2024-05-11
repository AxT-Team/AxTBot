# AxTBot-Public
基于 **[QQ官方PythonSDK](https://github.com/tencent-connect/botpy)** 开发的 **AxTBot-Public** 机器人程序<br>
<br>

## Hypixel查询注意事项:
Hypixel查询是基于 **[Spelako](https://github.com/Spelako)** 项目修改而来<br>
此存库**只提供用于启动PHP服务器API接口的代码**，其他代码请到原存库进行获取<br>

### API使用方法:<br>
1. 把 ``SpelakoCore`` 文件夹和 ``index.php`` 放在同目录下<br>
2. 使用 ``start.bat`` 启动即可（Linux自行编写启动脚本）
3. 默认启动在 ``0.0.0.0:30001`` ，如果端口被占用，请修改启动脚本中的端口号<br>

<br>

## 准备工作:

### 安装:
建议使用venv来控制项目依赖环境:

```bash
pip install -r requirements.txt
```

### 使用:
在 ``config.toml`` 里填入 ``appID`` ``secretKey``
随后，在含有 ``main.py`` 文件的目录下运行：
```bash
python main.py
```

<br>

## Mirai&CQ版本已转移到以下存库(内部号)
- https://github.com/XiaoXianHW/ATBot
- https://github.com/AxT-Team/Ebackup

