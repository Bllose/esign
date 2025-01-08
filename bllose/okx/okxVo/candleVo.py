from pydantic import BaseModel, model_validator
from bllose.helper.timeHelper import formatter

def format_timestamp(ts):
    """将Unix时间戳（毫秒）转换为格式化的日期字符串"""
    if ts is None:
        return None
    return formatter(ts)  


class CandleVo(BaseModel):
    # 类型名称
    instType: str = None

    # 开始时间，Unix时间戳的毫秒数格式
    ts: int = None

    # 结束时间，Unix时间戳的毫秒数格式
    cs: int = None

    # 格式化的开始时间
    tsFormat: str = None

    # 格式化的结束时间
    csFormat: str = None

    # 开盘价格
    o: float = None

    # 最高价格
    h: float = None

    # 最低价格
    l: float = None

    # 收盘价格
    c: float = None

    # 交易量，以张为单位。
    # 如果是衍生品合约，数值为合约的张数。
    # 如果是币币/币币杠杆，数值为交易货币的数量。
    vol: float = None

    # 交易量，以币为单位
    # 如果是衍生品合约，数值为交易货币的数量。
    # 如果是币币/币币杠杆，数值为计价货币的数量。
    volCcy: float = None

    # 交易量，以计价货币为单位
    # 如 BTC-USDT和BTC-USDT-SWAP，单位均是USDT。
    # BTC-USD-SWAP单位是USD。
    volCcyQuote: float = None

    # K线状态
    # 0：K线未完结
    # 1：K线已完结
    confirm: str = None

    @model_validator(mode='before')
    def set_format_fields(cls, values):
        """在模型验证之前更新格式化的时间字段"""
        if 'ts' in values:
            values['tsFormat'] = format_timestamp(values.get('ts'))
        if 'cs' in values:
            values['csFormat'] = format_timestamp(values.get('cs'))
        return values

    class Config:
        validate_assignment = True  # 确保在赋值时也触发验证器

    # Target Increasement
    # 理论预计可能的涨幅空间
    ti: float = None

    def cal_elements(self):
        """
        根据当前值计算最新指标
        """
        if self.h is not None and self.c is not None:
            self.ti = self.h / self.c

    # Traget Trading Volume 
    # 目标成交量，即成交量的比较基准
    ttv: float = None
    # 活跃度，基于目标成交量，当前成交量所呈现出的活跃度
    vitality: float = None

    def cal_vitality(self, target: float):
        if target is None:
            return
        self.ttv = target
        self.vitality = self.volCcy / self.ttv