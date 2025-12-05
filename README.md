
# AxTBot-v2.1

一个基于 Python 的可扩展 Bot 框架。
📖 完整文档请访问：[AxTBot-v2 | AxT Docs](https://docs.axtn.net/axtbot/v2.1/guide/intro.html)

---

> [!CAUTION]
> ⚠️ 当前分支正在进行灰度测试，可能存在问题。若存在问题请立即报告给管理员。

---

## 📜 许可 | License

> 本项目采用 **AGPLv3** 协议授权。
> **禁止任何企业直接将本代码用于商业产品或服务。**
> 但欢迎以下行为：
>
> * ✅ 学习代码思路
> * ✅ 独立实现类似功能（无论是否开源）
> * ✅ 在非商业场景下使用或修改本项目
>
> 若企业希望商业使用，请联系作者获取**例外许可**。
>
> *注：独立实现指未引用本项目任何源代码，且未侵犯著作权的新创作品。*

---

## ⚡ 快速开始 | Quick Start

### 1️⃣ 下载源码（或从Release下载Source Code.zip）

```bash
git clone https://github.com/AxT-Team/AxTBot.git
```

### 2️⃣ 创建虚拟环境（可选）

```bash
py -m venv .venv
.venv\Scripts\Activate
```

### 3️⃣ 安装依赖

```bash
pip install -e .[standard]
```

### 4️⃣ 配置环境变量

打开`config.yaml`，并按照指示填写你的机器人配置。

### 5️⃣ 启动 Bot

```bash
py main.py
```

---

## 🔧 快速开发 | Developer Guide

> 没错！现在你可以为你的 Bot 自行开发插件 ✨

开发指南请访问：[快速开发 - AxTBot-v2 | AxT Docs](https://docs.axtn.net/axtbot/v2.1/develop/intro.html)

---

## ⚠ 注意事项 | Attention

1. Advance - Debug模式打开后 可能会导致log重复生成，系重载进程导致，将尝试在日后版本修复

---

## 📓 计划更新 | Plan

- [ ] 细化报错日志 将更多细节公开给用户
- [ ] 检查SSL证书到期时间并通过配置文件里的邮箱推送给管理员
- [ ] 重新内构所有前端页面关联的后端API接口
- [ ] 适配完毕所有Uapis新功能
- [ ] 创建新的工单系统

---

## 🏷️ 其他版本迁移

* v2版本：
  [AxTBot-v2](https://github.com/AxT-Team/AxTBot/blob/AxTBot-v2)

* 旧版本（基于 `qq-botpy` + WebSocket）：

  * [https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1](https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1)
 
* Mirai & CQ 版（已存档的上古时期ATBot仓库）：

  * [https://github.com/XiaoXianHW/ATBot](https://github.com/XiaoXianHW/ATBot)
  * [https://github.com/AxT-Team/Ebackup](https://github.com/AxT-Team/Ebackup)

---

## [扩展] Hypixel 查询模块 （原仓库目前已关闭，暂不提供支持）

本项目中的 Hypixel 查询功能基于 [Spelako](https://github.com/Spelako) 项目进行修改。
**本仓库仅提供用于启动 PHP 服务器 API 接口的相关代码，其他功能请前往原仓库查看。**

### 🚀 启动 API 的方法：

1. 将 `SpelakoCore` 文件夹与 `index.php` 放置在同一目录中
2. 运行 `start.bat` 启动服务（Linux 用户请自行编写启动脚本）
3. 默认监听地址为 `0.0.0.0:30001`，如端口被占用请修改启动脚本中的端口设置


