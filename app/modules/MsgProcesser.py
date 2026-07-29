"""
Message Processing Modules for Union Framework

Author: Shanshui2024
Organization: AxT-Team
"""
handlers = {
    "command": [],   # 命令处理器
    "message": [],   # 消息处理器
}

def on_command(cmd_name):
    def decorator(func):
        handlers["command"].append({
            "name": cmd_name,
            "func": func
        })
        return func
    return decorator

def on_message(keyword=None):
    def decorator(func):
        handlers["message"].append({
            "keyword": keyword,
            "func": func
        })
        return func
    return decorator