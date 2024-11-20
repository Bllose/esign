from attr import define, field

@define
class OrgInfo():

    # 企业/机构证件号
    orgIDCardNum : str

    # 企业/机构证件类型，可选值如下：
    #   - CRED_ORG_USCC - 统一社会信用代码
    #   - CRED_ORG_REGCODE - 工商注册号
    orgIDCardType : str

@define
class PsnInfo():
    # 经办人姓名
    psnName : str

    # 经办人证件号
    snIDCardNum: str

    # 经办人证件类型，可选值如下
    # CRED_PSN_CH_IDCARD - 中国大陆居民身份证（默认值）
    # CRED_PSN_CH_HONGKONG - 香港来往大陆通行证（回乡证）
    # CRED_PSN_CH_MACAO - 澳门来往大陆通行证（回乡证）
    # CRED_PSN_CH_TWCARD - 台湾来往大陆通行证（台胞证）
    # CRED_PSN_PASSPORT - 护照
    psnIDCardType: str
    
@define
class TransactorInfo():

        # 经办人账号标识，手机号或邮箱
        psnAccount : str = field()

        psnInfo : PsnInfo = field(default=None)


@define
class OrgSignerInfo():

    # 企业/机构名称（账号标识）
    orgName : str = field()

    orgInfo : OrgInfo = field(default=None)

    # 企业/机构经办人信息
    transactorInfo : TransactorInfo = field(default=None)

