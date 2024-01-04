# AxTBot-Public
基于QQ官方PythonSDK开发的AxTBot-Public机器人程序

## Hypixel查询注意事项:
Hypixel查询是基于Spelako项目修改而来<br>
此存库只提供用于启动PHP服务器API接口的代码，其他代码请到原存库进行获取<br>
https://github.com/Spelako<br><br>

使用方法:<br>
把 ``SpelakoCore`` 文件和 ``index.php`` 放在同目录下，使用 ``start.bat`` 启动即可（Linux自行编写启动脚本）
默认启动在 ``0.0.0.0:30001`` 如果端口被占用，请修改启动脚本中的端口号<br>

## 准备工作:

### 安装:
建议使用venv来控制项目依赖环境:

```bash
pip install qq-botpy
pip install psutil
pip install requests
```

### 使用:
在 ``main.py`` 里填入 ``appID`` ``secretKey``

```bash
python main.py
```

## Mirai&易语言版本已转移到以下存库(内部号)
- https://github.com/XiaoXianHW/ATBot
- https://github.com/AxT-Team/Ebackup

