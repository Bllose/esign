from attr import define, field
from bllose.esign.sign_flow_vos.signFlowByFile.Docs import Docs
from bllose.esign.sign_flow_vos.signFlowByFile.SignFlowConfig import SignFlowConfig
from bllose.esign.sign_flow_vos.signFlowByFile.Signers import Signers

@define
class SignFlowByFile():
    """
    （精简版）基于文件发起签署 https://open.esign.cn/doc/opendoc/pdf-sign3/nxhgcl3bfgqz8qlz
    开发者可基于 已上传的合同文件 或 模板所填充生成的文件 来发起签署流程。

    【注意事项】
    1. 单个签署流程中对签署文件（docs）要求如下：
        单个签署流程中所添加的文件个数不可超过50个。
        单个文件大小不可超过50MB。
        单个文件内单页大小不可超过20MB（文件内含图片时，需特别关注单页大小）。
        单个签署流程中所添加的文件大小总和不可超过500MB。
    2. 单个签署流程中一次性添加的签署方（signers）不要超过10个，如果超过10个后续可以用《追加签署区》接口追加，整个流程不能超过50个签署方。
    3. 单个签署流程中所添加的签署区（signFields）总和不要超过300个。
    """
    
    docs: Docs = field(default= None)

    signFlowConfig: SignFlowConfig = field(default= None)

    signers: Signers = field(default= None)


if __name__ == '__main__':
    signFlowByFile = SignFlowByFile()
    print(signFlowByFile)