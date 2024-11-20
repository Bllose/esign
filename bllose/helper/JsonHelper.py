import json

def deep_clean_null(target) -> object:
    """
    深度清理json报文中值为null的字段
    """
    if isinstance(target, dict):
        return {k: deep_clean_null(v) for k, v in target.items() if v is not None}
    elif isinstance(target, list):
        return [deep_clean_null(item) for item in target if item is not None and len(item) > 0]
    else :
        return target
    

if __name__ == '__main__':
    target = '{"docs":{"fileId":"d41941eed835448ba8f03028823b766a","fileName":"租金表合同","neededPwd":false,"fileEditPwd":null,"contractBizTypeId":null,"order":1},"signFlowConfig":{"signFlowTitle":"租金表合同","signFlowExpireTime":null,"autoStart":true,"autoFinish":true,"identityVerify":true,"notifyUrl":"https://aurora-test1-callback.tclpv.com/api/app/contract/unify/signed/callback/eqb","noticeConfig":null},"signers":[{"signerType":1,"signFields":[{"fileId":"d41941eed835448ba8f03028823b766a","normalSignFieldConfig":{"freeMode":false,"autoSign":false,"movableSignField":false,"assignedSealId":"b51b9a3d-1f6b-4212-9738-c25d1f2faed5","availableSealIds":[],"orgSealBizTypes":"ALL","psnSealStyles":"0,1","signFieldStyle":1,"signFieldPosition":{"acrossPageMode":null,"positionPage":3,"positionX":138.0,"positionY":146.82}}},{"fileId":"d41941eed835448ba8f03028823b766a","normalSignFieldConfig":{"freeMode":false,"autoSign":false,"movableSignField":false,"assignedSealId":"997fa482-8c54-40f3-9526-5717598ee957","availableSealIds":[],"orgSealBizTypes":"ALL","psnSealStyles":"0,1","signFieldStyle":1,"signFieldPosition":{"acrossPageMode":null,"positionPage":3,"positionX":270.0,"positionY":278.02002}}}],"signConfig":{"signOrder":"1","forcedReadingTime":0},"noticeConfig":null,"orgSignerInfo":{"orgName":"九江泰盈惠合新能源科技有限公司","orgInfo":{"orgIDCardNum":"91360430MACL8M6Q2B","orgIDCardType":"CRED_ORG_USCC"},"transactorInfo":{"psnAccount":"18129705502","psnInfo":{"psnName":"陈曦","snIDCardNum":"431026198801130018","psnIDCardType":"CRED_PSN_CH_IDCARD"}}}}]}'
    result = deep_clean_null(json.loads(target))
    print(result)