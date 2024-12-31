from enum import StrEnum

class OrgTypeEnum(StrEnum):

    USCC = 'CRED_ORG_USCC', '统一社会信用代码'
    REGCODE = 'CRED_ORG_REGCODE', '工商注册号'

    def __new__(cls, key, content):
        obj = str.__new__(cls, key)
        obj._value_ = key
        obj.msg = content
        return obj
    
    @classmethod
    def of(cls, key):
        for curKey in cls:
            if curKey.value == key:
                return curKey
        return cls.USCC
    
if __name__ == '__main__':
    print(type(OrgTypeEnum.of('test')))
    print(type(OrgTypeEnum.of('CRED_ORG_REGCODE').value))
    print(OrgTypeEnum.of('CRED_ORG_REGCODE'))
    print(OrgTypeEnum.of('CRED_ORG_USCC').name)
    print(OrgTypeEnum.of('CRED_ORG_USCC').msg)