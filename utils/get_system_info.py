import psutil


async def get_system_info():
    info = {}

    # 获取CPU信息
    info['cpu_usage'] = f"{psutil.cpu_percent(interval=1)}%"

    # 获取内存信息
    memory = psutil.virtual_memory()
    memory_total_gb = memory.total / (1024 ** 3)
    memory_used_gb = memory.used / (1024 ** 3)
    info['ram'] = f"{memory_used_gb:.2f}/{memory_total_gb:.2f}GB"
    info['ram_usage'] = f"{memory.percent}%"

    return info
