import attr
from attr.validators import instance_of
from attr import define, field, asdict, astuple
from attrs import validators

@define
class Docs():

    # 待签署文件ID - 必输
    fileId: str = field(converter=str)

    # 文件名称（需要添加PDF文件后缀名，“xxx.pdf”） - 非必输
    fileName: str = None

    # 是否需要密码，默认false - 非必输
    neededPwd: bool = False

    # 文件编辑密码 - 非必输
    fileEditPwd: str = None

    # 合同类型ID - 非必输
    contractBizTypeId: str = None

    # 文件在签署页面的展示顺序 - 非必输
    # 按序展示时支持传入顺序值：1 - 50（值越小越靠前）
    order: int = field(converter=int, default=1)

    @fileId.validator
    def checkFileId(self, attribute, value):
        if value is None or len(value) < 1:
            raise ValueError('fileId can not be EMPTY!')
        
    @order.validator
    def checkOrder(self, attribute, value):
        if value is None or value < 1 or value > 50:
            raise ValueError(f'文件顺序为1~50, 当前顺序值{value}非法!')

if __name__ == '__main__':
    myDocs = Docs(fileId=123, order=1)
    print(myDocs)
    print(asdict(myDocs))
    print(astuple(myDocs))

