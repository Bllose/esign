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
    target = '{"docs":[{"fileId":"95bf212423864acab627b0c2994cd751","fileName":"光伏电站屋顶租赁协议（B端无共签人）20241128_release.pdf"}],"flowInfo":{"autoArchive":true,"autoInitiate":true,"businessScene":"极光平台用户授权书&光伏电站屋顶租赁协议","flowConfigInfo":{"noticeDeveloperUrl":"https://callback1-pv.tcl.com/api/app/contract/unify/signed/callback/eqb","noticeType":null,"redirectUrl":"","signPlatform":"1","willTypes":["FACE_TECENT_CLOUD_H5"],"personAvailableAuthTypes":null,"imageCode":null}},"signers":[{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"a776b83894944fc4b24bfbb7b8659689","authorizedAccountId":null,"noticeType":null},"signfields":[{"autoExecute":false,"actorIndentityType":null,"fileId":"95bf212423864acab627b0c2994cd751","sealType":"0","signDateBean":{"addSignTime":null,"fontSize":null,"format":null,"posPage":5,"posX":134.12,"posY":81.95825},"signType":null,"posBean":{"posPage":"5","posX":194.12,"posY":173.63928},"width":null,"sealId":null,"signDateBeanType":2}],"thirdOrderNo":null},{"platformSign":false,"signOrder":1,"signerAccount":{"signerAccountId":"a776b83894944fc4b24bfbb7b8659689","authorizedAccountId":null,"noticeType":null},"signfields":[{"autoExecute":false,"actorIndentityType":null,"fileId":"95bf212423864acab627b0c2994cd751","sealType":"0","signDateBean":null,"signType":null,"posBean":{"posPage":"6","posX":158.88,"posY":436.43927},"width":null,"sealId":null,"signDateBeanType":null}],"thirdOrderNo":null},{"platformSign":true,"signOrder":2,"signerAccount":null,"signfields":[{"autoExecute":true,"actorIndentityType":"2","fileId":"95bf212423864acab627b0c2994cd751","sealType":null,"signDateBean":null,"signType":null,"posBean":{"posPage":"5","posX":214.12,"posY":127.799255},"width":null,"sealId":"42ac600b-54c7-467c-ba58-25471f33c0dc","signDateBeanType":null}],"thirdOrderNo":null}],"atts":null}'
    targetJson = json.loads(target)
    print(json.dumps(deep_clean_null(target=targetJson), ensure_ascii=False))