import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(".env")

class Config:
    """
    配置类，用于管理应用程序的配置参数。

    参数可以通过构造函数传入，或者从环境变量中读取。如果未提供参数且环境变量也未设置，
    则使用默认值。

    Attributes:
        ip (str): Webhook 监听IP地址，默认 '127.0.0.1'。
        port (int): Webhook 监听端口，默认 8443。
        path (str): Webhook 监听路径，默认 '/webhook'。
        appid (int): 机器人AppID。无默认值，用于登录机器人、发送消息。 
        ssl_cert (str): SSL证书路径，默认 './data/cert.pem'。
        ssl_key (str): SSL证书私钥路径，默认 './data/key.pem'。
        bot_secret (str): 机器人AppSecret。无默认值，用于登录机器人、发送消息。
        log_level (str): 日志级别，默认 'INFO'。
        log_dir (str): 日志文件存储目录，默认 './logs'。
        data_dir (str): 数据文件存储目录，默认 './data'。
        plugins_dir (str): 插件文件存储目录，默认 './plugins'。
    """

    def __init__(self, ip=None, port=None, path=None, appid=None, bot_secret=None, ssl_cert=None, ssl_key=None, log_level=None, log_dir=None, data_dir=None, plugins_dir=None):
        """
        初始化配置实例。

        Args:
            ip (str, optional): IP地址。默认为环境变量中的 'IP' 或 '0.0.0.0'。
            port (int, optional): 端口号。默认为环境变量中的 'PORT' 或 8443。
            path (str, optional): Webhook 监听路径，默认为环境变量中的 'WEBHOOK_PATH' 或 '/'。
            appid (int): 机器人AppID。无默认值，用于登录机器人、发送消息。
            ssl_cert (str): SSL证书路径，默认 './data/cert.pem'。
            ssl_key (str): SSL证书私钥路径，默认 './data/key.pem'。
            bot_secret (str): 机器人AppSecret。无默认值，用于登录机器人、发送消息。
            log_level (str, optional): 日志级别。默认为环境变量中的 'LOG_LEVEL' 或 'INFO'。
            log_dir (str, optional): 日志目录。默认为环境变量中的 'LOG_DIR' 或 './logs'。
            data_dir (str, optional): 数据目录。默认为环境变量中的 'DATA_DIR' 或 './data'。
            plugins_dir (str, optional): 插件目录。默认为环境变量中的 'PLUGINS_DIR' 或 './plugins'。
        """
        self.ip = os.getenv('IP', ip or '0.0.0.0')
        try:
            self.port = int(os.getenv('PORT', port or 8443))
        except ValueError:
            raise ValueError("无效的端口号，请确保 PORT 是一个有效的整数")
        self.path = os.getenv('WEBHOOK_PATH', path or '/')
        self.appid = str(os.getenv('APPID', appid))
        self.bot_secret = os.getenv('BOT_SECRET', bot_secret)
        self.ssl_cert = os.getenv('SSL_CERT', ssl_cert or './data/cert.pem')
        self.ssl_key = os.getenv('SSL_KEY', ssl_key or './data/key.pem')
        self.log_level = os.getenv('LOG_LEVEL', log_level or 'INFO')
        self.log_dir = os.getenv('LOG_DIR', log_dir or './logs')
        self.data_dir = os.getenv('DATA_DIR', data_dir or './data')
        self.plugins_dir = os.getenv('PLUGINS_DIR', plugins_dir or './plugins')

        # 检查必填项
        required_fields = {
            'appid': self.appid,
            'bot_secret': self.bot_secret,
            'ssl_cert': self.ssl_cert,
            'ssl_key': self.ssl_key
        }
        missing_fields = [k for k, v in required_fields.items() if v is None]
        if missing_fields:
            raise ValueError(f"配置项丢失！以下配置项必须有值: {', '.join(missing_fields)}")

    def __repr__(self):
        """
        返回配置实例的字符串表示。

        Returns:
            str: 配置实例的字符串表示。
        """
        return f"Config(ip={self.ip}, port={self.port}, path={self.path}, appid={self.appid}, bot_secret={self.bot_secret}, ssl_cert={self.ssl_cert}, ssl_key={self.ssl_key}, log_level={self.log_level}, log_dir={self.log_dir}, data_dir={self.data_dir}, plugins_dir={self.plugins_dir})"

# 创建 Config 实例
config = Config()