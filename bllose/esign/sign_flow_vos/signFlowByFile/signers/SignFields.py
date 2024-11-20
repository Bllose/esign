from attr import define, field


@define
class SignFieldPosition():
    # 骑缝章模式选择
    # ALL - 全部页盖骑缝章，AssignedPages - 指定页码盖骑缝章
    acrossPageMode: str = field(default=None)

    # 签章区所在页码
    positionPage: str = field(default=None)

    # 签章区所在X坐标（当signFieldStyle为2即骑缝签章时，该参数不生效，可不传值）
    positionX: float = field(default=None)

    # 签章区所在Y坐标
    positionY: float = field(default=None)




@define
class NormalSignFieldConfig():

    # 是否自由签章，默认值 false
    freeMode: bool = field(default=False)

    # 是否后台自动落章，默认值 false
    # true - 后台自动落章（无感知），false - 签署页手动签章
    autoSign: bool = field(default=False)

    # 页面是否可移动签章区，默认值 false
    # true - 可移动 ，false - 不可移动
    movableSignField: bool = field(default=False)

    # 指定印章ID（印章ID是e签宝SaaS官网的印章编号)
    assignedSealId: str = field(default=None)

    # 手动签章时页面可选的印章列表（印章ID是e签宝SaaS官网的印章编号）
    availableSealIds: list = field(default=None)

    # 页面可选机构印章类型，默认值ALL
    # ALL - 显示所有类型的印章
    # PUBLIC - 机构主体公章
    # CONTRACT - 合同专用章
    # FINANCE - 财务专用章
    # PERSONNEL -人事专用章
    # COMMON -其他类印章（无具体业务类型的章）
    orgSealBizTypes: str = field(default=None)

    # 页面可选个人印章样式，默认值0和1（英文逗号分隔）
    # 0 - 手写签名
    # 1 - 姓名印章
    # 2 - 手写签名AI校验
    psnSealStyles: str = field(default=None)

    # 签章区样式
    # 1 - 单页签章，2 - 骑缝签章
    signFieldStyle:int = field(default = 1)

    # 签章区位置信息
    signFieldPosition: SignFieldPosition  = field(default=None)



@define
class SignField():

    # 签署区所在待签署文件ID
    fileId: str = field()

    # 签章区配置项
    normalSignFieldConfig : NormalSignFieldConfig = field(default=None)




