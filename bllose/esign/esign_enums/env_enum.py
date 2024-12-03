from enum import StrEnum

class EqbEnum(StrEnum):
    """
    e签宝环境选择
    默认返回 'test'环境
    当且仅当选择 'pro' 时才返回生产环境
    """
    TEST = 'test', '测试环境'
    PRO = 'pro', '生产环境'

    def __new__(cls, env, msg):
        obj = str.__new__(cls, env)
        obj._value_ = env
        obj.msg = msg
        return obj
    
    @classmethod
    def of(cls, env):
        for curEnv in cls:
            if curEnv.value == env.lower():
                return curEnv
        return cls.TEST
    

if __name__ == '__main__':
    print(type(EqbEnum.of('test')))
    print(type(EqbEnum.of('test').value))
    print(EqbEnum.of('pro'))
    print(EqbEnum.of('pro1').name)
    print(EqbEnum.of('pro1').msg)
