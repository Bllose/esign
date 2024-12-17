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
    target = '{"version":"v10","isSign":true,"isRushSign":false,"templateId":null,"objectNo":"GF241214143630002323","sceneCode":"PCI001","signFlowNo":null,"imageCode":null,"sceneName":null,"signMethod":1,"controlSignNodes":null,"channel":3,"tenantKey":null,"organACode":null,"organAName":null,"organBCode":null,"organBName":null,"legalName":null,"legalIdNo":null,"legalMobile":null,"legalBName":null,"legalBIdNo":null,"legalBMobile":null,"spouseName":null,"spouseIdCard":null,"fillElement":null,"reqFillElement":null,"lockId":null,"isReuse":null,"reuseValidDays":null,"needSignUrl":true,"needCosignerUrl":true,"createAccountId":true,"signTasks":[{"sceneCode":"OBO001","imageCode":"OBO001_image","version":"v1"}],"signerName":null,"signerId":null,"signerMobile":null}'
    targetJson = json.loads(target)
    print(json.dumps(deep_clean_null(target=targetJson), ensure_ascii=False))