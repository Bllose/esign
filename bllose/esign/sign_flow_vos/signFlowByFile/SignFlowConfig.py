from attr import define, field


@define
class NoticeConfig():

    # 通知类型，通知发起方、签署方、抄送方，默认不通知（值为""空字符串），允许多种通知方式，请使用英文逗号分隔）
    # 传空 - 不通知（默认值）
    # 1 - 短信通知（如果套餐内带“分项”字样，请确保开通【电子签名流量费（分项）认证】中的子项：【短信服务】，否则短信通知收不到）
    # 2 - 邮件通知
    # 3 - 钉钉工作通知（需使用e签宝钉签产品）
    # 5 - 微信通知（用户需关注“e签宝电子签名”微信公众号且使用过e签宝微信小程序）
    noticeTypes: str = field(converter=str, default='')

    # 通知给企业印章用印审批人员的通知类型，按照账号中的手机号或邮箱的填写情况进行通知。
    # true - 发送消息（短信+邮件+e签宝官网站内信）
    # false - 不发送消息
    examineNotice: bool = field(default=False)

    @noticeTypes.validator
    def checkNoticeTypes(self, attributions, value):
        if value != '':
            intValue = int(value)
            if(intValue < 1 or intValue > 5 or intValue == 4):
                raise ValueError(f'noticeType illegal! {value} -> legal value [1, 2, 3, 5]')


@define
class SignFlowConfig():

    # 签署流程主题（将展示在签署通知和签署页的任务信息中） - 必输
    signFlowTitle: str = field()

    # 签署截止时间， unix时间戳（毫秒）格式 - 非必输
    signFlowExpireTime: int = field(default=None)

    # 自动开启签署流程，默认值 true
    autoStart: bool = field(default=True)

    # 所有签署方签署完成后流程自动完结，默认值 false
    # false - 非自动完结，需调用【完结签署流程】接口完结
    autoFinish: bool = field(default=False)

    # 身份校验配置项（当开发者指定的签署人信息与该签署人在e签宝已有的身份信息不一致时如何处理），默认：true
    identityVerify: bool = field(default=True)

    # 接收相关回调通知的Web地址，详见【签署回调通知接收说明】
    notifyUrl: str = field(default=None)

    noticeConfig: NoticeConfig = field(default=None)

    @signFlowTitle.validator
    def checkSignFlowTitle(self, attributions, value):
        if value is None or len(value) < 1:
            raise ValueError('signFlowTitle can not be empty!')
        


if __name__ == '__main__':
    signFlowConfig = SignFlowConfig(signFlowTitle='合同标题')
    print(signFlowConfig)