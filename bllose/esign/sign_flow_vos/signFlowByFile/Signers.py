from attr import define, field
from bllose.esign.sign_flow_vos.signFlowByFile.signers.SignFields import SignField
from bllose.esign.sign_flow_vos.signFlowByFile.signers.SignConfig import SignConfig
from bllose.esign.sign_flow_vos.signFlowByFile.signers.OrgSignerInfo import OrgSignerInfo
from bllose.esign.sign_flow_vos.signFlowByFile.SignFlowConfig import NoticeConfig

@define
class Signers():

    # 签署方类型，0 - 个人，1 - 企业/机构，2 - 法定代表人，3 - 经办人
    signerType: int = field()

    signFields: list = field(default=[])
    # [SignField] = field(factory=list)

    signConfig: SignConfig = field(default=None)

    noticeConfig : NoticeConfig = field(default=None)

    orgSignerInfo : OrgSignerInfo = field(default=None)

    # @signFields.validator
    # def checkSignFields(self, attributions, value):
    #     for sign in value:
    #         if not isinstance(sign, SignField):
    #             raise ValueError(f"All elements in signFields must be SignField instances, got {type(sign)}")

    # @property   
    # def signFields(self):
    #     return self.signFields
    
    # @signFields.setter
    # def signFields(self, value):
    #     if all(isinstance(item, SignField) for item in value):
    #         self.signFields = value
    #     else :
    #         raise ValueError('signFields 中所有的参数都必须是SignField!')
            

if __name__ == '__main__':
    signers = Signers(signerType=0)
    signers.signFields = [SignField(fileId='')]
    print(signers)