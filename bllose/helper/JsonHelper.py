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
    target = {"docs":[{"fileId":"defc0b391be14432bee7972bb6db9053","fileName":"极光平台用户授权书20241118.pdf"},{"fileId":"e97f9700fd3c4c3cafe28f154efe65ae","fileName":"光伏电站屋顶租赁协议（B端无共签人）20241128_release.pdf"}],"flowInfo":{"autoArchive":True,"autoInitiate":True,"businessScene":"极光平台用户授权书&光伏电站屋顶租赁协议","flowConfigInfo":{"noticeDeveloperUrl":"https://callback1-pv.tcl.com/api/app/contract/unify/signed/callback/eqb","noticeType":None,"redirectUrl":"","signPlatform":"1","willTypes":["FACE_TECENT_CLOUD_H5"],"personAvailableAuthTypes":None,"imageCode":None}},"signers":[{"platformSign":False,"signOrder":1,"signerAccount":{"signerAccountId":"87ca3d2710fa45158dfeae1466ad1d5b","authorizedAccountId":None,"noticeType":None},"signfields":[{"autoExecute":False,"actorIndentityType":None,"fileId":"defc0b391be14432bee7972bb6db9053","sealType":"0","signDateBean":{"addSignTime":None,"fontSize":None,"format":None,"posPage":3,"posX":340.0,"posY":191.19905},"signType":None,"posBean":{"posPage":"3","posX":420.0,"posY":235.118},"width":None,"sealId":None,"signDateBeanType":2}],"thirdOrderNo":None},{"platformSign":False,"signOrder":1,"signerAccount":{"signerAccountId":"87ca3d2710fa45158dfeae1466ad1d5b","authorizedAccountId":None,"noticeType":None},"signfields":[{"autoExecute":False,"actorIndentityType":None,"fileId":"e97f9700fd3c4c3cafe28f154efe65ae","sealType":"0","signDateBean":{"addSignTime":None,"fontSize":None,"format":None,"posPage":5,"posX":134.12,"posY":81.95825},"signType":None,"posBean":{"posPage":"5","posX":224.12,"posY":183.63928},"width":None,"sealId":None,"signDateBeanType":2}],"thirdOrderNo":None},{"platformSign":False,"signOrder":1,"signerAccount":{"signerAccountId":"87ca3d2710fa45158dfeae1466ad1d5b","authorizedAccountId":None,"noticeType":None},"signfields":[{"autoExecute":False,"actorIndentityType":None,"fileId":"e97f9700fd3c4c3cafe28f154efe65ae","sealType":"0","signDateBean":None,"signType":None,"posBean":{"posPage":"6","posX":198.88,"posY":446.43927},"width":None,"sealId":None,"signDateBeanType":None}],"thirdOrderNo":None},{"platformSign":True,"signOrder":2,"signerAccount":None,"signfields":[{"autoExecute":True,"actorIndentityType":"2","fileId":"e97f9700fd3c4c3cafe28f154efe65ae","sealType":None,"signDateBean":None,"signType":None,"posBean":{"posPage":"5","posX":214.12,"posY":137.79926},"width":None,"sealId":"18b36ce3-32dd-4cc6-8d4d-7462ff661cc9","signDateBeanType":None}],"thirdOrderNo":None}],"atts":None}

    print(json.dumps(deep_clean_null(target=target), ensure_ascii=False))