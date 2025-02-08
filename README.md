# AxTBot-v2

*tips.这个框架我一共才花了三天时间写出来，稳定性待测试，史山也是指定会有的，轻喷*

<br />

## 使用文档
- [AxTBot | AxT Docs](https://docs.axtn.net/AxTBot/)

## Hypixel查询注意事项:
Hypixel查询是基于 **[Spelako](https://github.com/Spelako)** 项目修改而来<br>
此存库**只提供用于启动PHP服务器API接口的代码**，其他代码请到原存库进行获取<br>

### API使用方法:<br>
1. 把 ``SpelakoCore`` 文件夹和 ``index.php`` 放在同目录下<br>
2. 使用 ``start.bat`` 启动即可（Linux自行编写启动脚本）
3. 默认启动在 ``0.0.0.0:30001`` ，如果端口被占用，请修改启动脚本中的端口号<br>

<br />

## 快速开始

1. 下载源码

2. 创建虚拟环境(可选)

在控制台中输入如下命令创建venv虚拟环境
```bash
D:\AxTBot> py -m venv <文件夹名>
```

3. 安装依赖

如果你使用venv虚拟环境，那么在venv虚拟环境中安装依赖（我还没写依赖，后续版本会提供的（（（
```bash
D:\AxTBot> <虚拟环境文件夹>\Scripts\Activate
(venv) D:\AxTBot> pip install -r requirements.txt
```

4. 运行
```bash
(venv) D:\AxTBot> py main.py
```

## 注意事项
1. 由于配置Config.py尚未完成，目前的机器人参数散落在main.py与Core\Auth.py文件中，将会在后续版本中解决该问题

2. 由于未知原因，部分功能在被调用后会出现重复请求的现象，系开放平台逻辑有误，目前暂无解决办法

3. 日志并非即时更改，所以框架刚开机时日志文件为空，将在后续版本中解决该问题

4. 由于历史遗留问题，remake.db不会自动生成，将在后续版本中解决问题

5. 由于历史遗留问题，uapis请求接口返回错误之后不会回传给用户，将在后续版本中解决问题

## 快速开发

> [!CAUTION]
> 此章节未完工，请暂时参照plugins文件夹中的插件进行开发

*你没看错，新框架允许你自己开发插件供你自己机器人使用了（*


<br>

## Mirai&CQ版本已转移到以下存库(内部号)
- https://github.com/XiaoXianHW/ATBot
- https://github.com/AxT-Team/Ebackup

## 旧版本(基于qq-botpy + Websocket所写的)
- https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1