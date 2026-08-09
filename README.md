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
- app.modules   核心工作组件
- app.main     项目主入口文件

## To Do

### 消息事件
- [x] 消息事件验证
- [x] 新增基础消息事件
- [x] 获取并缓存AccessToken （Service.AccessToken）
- [x] 补全基础消息事件的 Union 事件基类
- [x] OpCode 0 的消息基类分类
- [x] 新增其他独立信息事件和session内依赖事件
- [x] 允许耦合/解耦框架自带的Message等基类（Classes.framework）


### API
- [x] Router路由模块化
- [ ] 规范化所有API接口输出
- [ ] 新增对Milky协议的支持
- [x] 消息流向外传递 并写入OpenAPI文档

### 框架模块
- [x] 添加日志模块
- [x] 添加Config配置模块
- [x] 细化配置项和配置功能管理
- [x] 添加ORM数据库模块（Modules.Database）
- [x] 添加框架插件管理模块
- [x] 添加证书重载模块
- [ ] 添加框架WebUI组件和Console交互式控制台模块
- [ ] 扩展模块的统一规格化
- [ ] 框架核心组件打包

### 插件
- [x] 新增插件元数据
- [x] 新增插件商店 验证插件
- [x] 新增插件自动验证ci

### 框架安全性
- [ ] 接入AxT Dash Oauth2 进行后台API事件验证

### 高阶功能
- [ ] 框架热重载
- [x] 新增cli控制工具

### qq_adapter QQ适配器
- [ ] 支持Websocket/Webhook切换
- [ ] 与核心事件逻辑解耦


### 存库
- [ ] 完成`tests`上线前测试功能
- [ ] 完成`issue_template`和其他联动