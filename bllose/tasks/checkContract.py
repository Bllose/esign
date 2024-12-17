from bllose.esign.Client import eqb_sign


req = '{"docs": [{"fileId": "392c48ebeb984a23a86b41def617b004", "fileName": "光伏电站屋顶租赁协议（B端无共签人）20241128_release.pdf"}], "flowInfo": {"autoArchive": true, "autoInitiate": true, "businessScene": "极光平台用户授权书, 光伏电站屋顶租赁协议", "flowConfigInfo": {"noticeDeveloperUrl": "https://callback1-pv.tcl.com/api/app/contract/unify/signed/callback/eqb", "noticeType": "", "redirectUrl": "", "signPlatform": "1", "willTypes": ["FACE_TECENT_CLOUD_H5"]}}, "signers": [{"platformSign": false, "signOrder": 1, "signerAccount": {"signerAccountId": "866ee2a166214d429b1ed34b8970c4bc"}, "signfields": [{"autoExecute": false, "fileId": "392c48ebeb984a23a86b41def617b004", "sealType": "0", "signDateBean": {"posPage": 5, "posX": 134.12, "posY": 81.95825}, "posBean": {"posPage": "5", "posX": 224.12, "posY": 183.63928}, "signDateBeanType": 2}]}, {"platformSign": false, "signOrder": 1, "signerAccount": {"signerAccountId": "866ee2a166214d429b1ed34b8970c4bc"}, "signfields": [{"autoExecute": false, "fileId": "392c48ebeb984a23a86b41def617b004", "sealType": "0", "posBean": {"posPage": "6", "posX": 198.88, "posY": 446.43927}}]}, {"platformSign": true, "signOrder": 2, "signfields": [{"autoExecute": true, "actorIndentityType": "2", "fileId": "392c48ebeb984a23a86b41def617b004", "posBean": {"posPage": "5", "posX": 214.12, "posY": 137.79926}, "sealId": "241c2d16-6492-4a58-83c6-3f0306edc2e3"}]}]}'
client = eqb_sign(env='pro')
flowId = client.createFlowOneStep(bodyRaw=req)

print(flowId)
