from enum import StrEnum

class IdentityEnum(StrEnum):
    CODE_SMS = '短信验证码'
    CODE_VOICE = '语言短信验证码'
    FACE_ZHIMA_XY = '支付宝刷脸'
    FACE_TECENT_CLOUD_H5 = '腾讯云刷脸FACE_FACE_LIVENESS_RECOGNITION 快捷刷脸'
    FACE_WE_CHAT_FACE = '微信小程序刷脸'
    FACE_ALI_MINI_PROGRAM = '支付宝小程序刷脸'
    FACE_AUDIO_VIDEO_DUAL = '支付宝智能视频认证'
    VIDEO_WE_CHAT_VIDEO_DUAL = '微信智能视频认证'
    INDIVIDUAL_TELECOM_3_FACTOR = '个人运营商三要素'
    INDIVIDUAL_BANKCARD_4_FACTOR = '个人银行卡四要素'
    FACEAUTH_ZMXY = '支付宝刷脸'
    FACEAUTH_TECENT_CLOUD = '腾讯云刷脸'
    FACEAUTH_ESIGN = '快捷刷脸'
    FACEAUTH_WE_CHAT_FACE = '微信小程序刷脸'
    INDIVIDUAL_ALIPAY_ONECLICK = '个人支付宝一键认证（支付宝小程序实名）'
    INDIVIDUAL_ARTIFICIAL = '个人人工实名'
    ILLEGAL = '未知类型'

    @classmethod
    def of(cls, key: str) -> str:
        for identity in cls:
            if identity.name == key.upper():
                return identity.value
        return cls.ILLEGAL.value
    
if __name__ == '__main__':
    print(IdentityEnum.of('FACE_WE_CHAT_FACE'))