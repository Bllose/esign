from functools import wraps
import sys
import os
import logging
import json
from enum import Enum

class scope(Enum):
    """
    加载配置范围
    FILE
    各种文件定义的配置项，包括yaml, properties, xml等
    默认会加载根目录config.yml, 当前运行根目录 ./config.yml, 当前文件所在目录的config.yml
    """
    SYS = 0
    ENV = 1
    FILE = 2
    

class Config():
    def __init__(self, *args):
        self.scopeList = self.initScopeList(list(args))
        self.config = {}

    def initScopeList(self, rawList) -> list:
        if rawList is None:
            rawList = []
        scopeList = []
        for config in rawList:
            if isinstance(config, scope):
                scopeList.append(config)
            elif isinstance(config, int):
                try:
                    scopeList.append(scope(config))
                except ValueError as e:
                    logging.warning(f'忽略非法配置环境{config}: 异常信息{e}')
            else:
                logging.warning(f'忽略非法配置环境{config}')
        if len(scopeList) < 1:
            """
            一旦无法获取到合理的配置环境，
            则默认返回所有环境
            """
            scopeList = [scope.FILE, scope.ENV, scope.SYS]
        return scopeList


    def load(self):
        for curScope in self.scopeList:
            match curScope:
                case scope.FILE:
                    self.loadFileConfig()
                case scope.SYS:
                    self.loadSystemConfig()
                case scope.ENV:
                    self.loadEnvironmentConfig()
        return self

    def loadFileConfig(self):
        """
        最大可能性加载文件配置
        1、首先在当前执行文件所在目录找
        2、然后再运行环境所在目录找
        3、在根目录找
        """

        # 当前文件的绝对路径
        exe_path = sys.argv[0]
        root_path = os.path.abspath(os.sep)
        """
        默认逻辑下尝试寻找可以加载的配置文件
        """
        default_config_file_list = ['config.yml', 'config.yaml', 'config.properties']
        loaded_config_file_list = []
        for cur_file in default_config_file_list:
            absPath = os.path.dirname(exe_path) + os.sep + cur_file
            logging.debug(f'尝试加载配置文件{absPath}')
            if os.path.exists(absPath):
                if self.loadingTheFile(absPath, cur_file):
                    loaded_config_file_list.append(absPath)
            
            absPath = os.getcwd() + os.sep + cur_file
            logging.debug(f'尝试加载配置文件{absPath}')
            if os.path.exists(absPath):
                if self.loadingTheFile(absPath, cur_file):
                    loaded_config_file_list.append(absPath)
            
            absPath = root_path + cur_file
            logging.debug(f'尝试加载配置文件{absPath}')
            if os.path.exists(absPath):
                if self.loadingTheFile(absPath, cur_file):
                    loaded_config_file_list.append(absPath)

        logging.debug(f'加载有效配置文件 {loaded_config_file_list}')

    def loadingTheFile(self, absPath, cur_file):
        suffix = cur_file.split('.')[-1].lower()
        match suffix:
            case 'yml' | 'yaml':
                self.load_yaml_config_file(absPath)
                return True
            case 'xml':
                pass
            case 'properties':
                self.load_properties_config_file(absPath)
                return True
        return False
    
    def load_properties_config_file(self, absPath: str) -> None:
        """
        加载properties文件, 读取配置信息，并填充到 config 对象中
        """
        logging.debug(f'当前加载配置文件 -> {absPath}')

        from javaproperties import Properties
        properties = Properties()
        with open(absPath, 'rb') as f:  
            properties.load(f)
        self.config.update(properties.data)
        logging.debug(f'加载配置文件{absPath}完成\r\n一共加载配置{len(properties.data)}项')

    def load_yaml_config_file(self, absPath: str) -> None:
        """
        加载yml文件, 读取配置信息，并填充到 config 对象中
        """
        logging.debug(f'当前加载配置文件 -> {absPath}')
        import yaml

        with open(absPath, 'r', encoding='utf-8') as file:  
            yaml_config = yaml.safe_load(file)
            self.config.update(yaml_config)
            logging.debug(f'加载配置文件{absPath}完成\r\n一共加载配置{len(yaml_config)}项')



    def loadSystemConfig(self):
        import sys
        sys_type = sys.platform
        match(sys_type):
            case 'win32':
                self.loadWindowSystemConfig()
        pass

    def loadWindowSystemConfig(self):
        """
        加载Windows
        """
        import os
        self.config.update({key: value for key, value in os.environ.items()})



    def loadEnvironmentConfig(self):
        pass

    def hasConfig(self, key) -> bool:
        return key in self.config
    
    def get(self, key):
        """
        尝试从配置池中获取配置
        若存在则返回配置 key 所对应的 value
        否则返回 None
        """
        if self.hasConfig(key):
            return self.config[key]
        else:
            return None

def bConfig():
    """
    <p>给方法装饰，为方法增加可用配置内容</p>
    <p>被装饰方法需要通过参数 config 来接受这些配置内容</p>
    <p>如果被装饰方法的调用方已经为config赋值， 那么新增的配置将添加进去</p>
    ```
    @bConfig()
    def my_function_need_config(*args, config):
        # 方法中便可以使用已经加载好的配置项了
        myValue = config['myKey']
    ```
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            load_config(kwargs)
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def load_config(kwargs):
    theConfig = Config().load()
    if 'config' not in kwargs:
        kwargs['config'] = {}
    kwargs['config'].update(theConfig.config)
    logging.debug(f'加载配置项{json.dumps(theConfig.config)}')

def class_config(cls):
    """
    <p>给类装饰，为类的初始化方法增加可用配置内容</p>
    <p>被装饰类的初始化方法需要通过参数 config 来接受这些配置内容</p>
    ```
    @class_config
    class myClass():
        def __init__(self, config):
            # 方法中便可以使用已经加载好的配置项了
            myValue = config['myKey']
    ```
    """
    class wrapper_class(cls):
        def __init__(self, *args, **kwargs):
            load_config(kwargs)
            super().__init__(*args, **kwargs)
    return wrapper_class

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myConfig = Config()
    myConfig.load()
    app_id = myConfig.get('eqb')['pro']['appId']
    print(app_id)
    print(myConfig.get('okx.Bllose.apiKey'))
