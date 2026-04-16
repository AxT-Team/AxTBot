# AxTBot v2.1.1

## 介绍

> [!CAUTION]
> 本项目未完工 请知悉

AxTBot 重制版本2.1.1

该版本旨在彻底模块化整个项目包，确保标准的、更完善的、简洁的项目代码结构，以及更快捷方便的模块卸载/加载

## 模块
到目前为止 该项目模块分布如下：
- app.classes  Python类型定义包
- app.router   FastAPI 路由映射
- app.service  Service服务模块
- app.module   核心工作组件
- app.main     项目主入口文件

## To Do

### 消息事件
- [x] 消息事件验证
- [ ] 新增基础消息事件
- [ ] 获取并缓存AccessToken （Service.AccessToken） <- 正在进行验证
- [ ] 补全基础消息事件的 Union 事件基类
- [ ] OpCode 0 的消息基类分类

### API
- [x] Router路由模块化
- [ ] 规范化所有API接口输出

### 框架健康检查
- [ ] 框架自主心跳检测和多模块检测态
- [ ] 模块读取错误自动回退并报错

### 框架模块
- [ ] 添加日志模块 <- 正在进行验证
- [ ] 添加Config配置模块
- [ ] 添加ORM数据库模块（Modules.Database）
- [ ] 添加框架插件管理模块
- [ ] 添加证书通知和热重载模块

### 框架安全性
- [ ] 接入AxT Dash Oauth2 进行后台API事件验证