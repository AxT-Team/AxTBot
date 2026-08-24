# AxTBot v2.2

## 介绍

一个基于 Python 的可扩展 Bot 框架。
📖 完整文档请访问：[AxTBot-v2.2 | AxT Docs](https://docs.axtn.net/axtbot/v2.2/guide/intro.html)

---
## 📜 许可 | License
> 本项目采用 AGPLv3 协议授权。 禁止任何企业直接将本代码用于商业产品或服务。 但欢迎以下行为：

> ✅ 学习代码思路
> ✅ 独立实现类似功能（无论是否开源）
> ✅ 在非商业场景下使用或修改本项目
> 若企业希望商业使用，请联系作者获取例外许可。

> 注：独立实现指未引用本项目任何源代码，且未侵犯著作权的新创作品。
---

## 安装
1. 拉取该存库：
```bash
git clone https://github.com/AxTBot.git
```

2. 在拉取目录下创建虚拟环境
```bash
python -m venv .venv
```

3. 进入虚拟环境
```bash
\.venv\Scripts\activate
```

4. 使用uv管理器安装依赖
```bash
pip install uv
uv sync
```

5. 修改配置文件
存库默认会在根目录新增 `example.env` 文件，请按照说明修改并改名为 `local.env`

6. 启动
在虚拟环境下执行
```bash
axtbot run
```
---
## 开发
有关开发内容 详阅 [AxT Docs](https://docs.axtn.net/)

---
## To Do

### API
- [ ] 规范化所有API接口输出

### 框架模块
- [ ] 添加框架WebUI组件和Console交互式控制台模块
- [x] 扩展模块的统一规格化
- [ ] 框架核心组件打包

### 框架安全性
- [ ] 接入AxT Dash Oauth2 进行后台API事件验证

### 高阶功能
- [ ] 框架热重载

### qq_adapter QQ适配器
- [ ] 支持Websocket/Webhook切换
- [ ] 与核心事件逻辑解耦

---
## 🏷️ 其他版本迁移

* v2版本：
  [AxTBot-v2.1](https://github.com/AxT-Team/AxTBot/blob/AxTBot-v2.1)
  [AxTBot-v2](https://github.com/AxT-Team/AxTBot/blob/AxTBot-v2)

* 旧版本（基于 `qq-botpy` + WebSocket）：

  * [https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1](https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1)
 
* Mirai & CQ 版（已存档的上古时期ATBot仓库）：

  * [https://github.com/XiaoXianHW/ATBot](https://github.com/XiaoXianHW/ATBot)
  * [https://github.com/AxT-Team/Ebackup](https://github.com/AxT-Team/Ebackup)

---

## [扩展] Hypixel 查询模块

本项目中的 Hypixel 查询功能基于 [Spelako](https://github.com/Spelako) 项目进行修改。

- 项目地址：[HypixelAPI-Python](https://github.com/AxT-Team/HypixelAPI-Python)