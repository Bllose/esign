from bllose.okx.clients.blloseHttpClient import blloseHttpOKE
from bllose.okx.okxEnums.instTypeEnums import instrumentType
from bllose.okx.okxVo.candleVo import CandleVo
from pydantic_core import to_json
from typing import Optional, Tuple, List, Dict
import logging


def data_collection(instList: list) -> list:
    """
    将原始数据转化为vo对象, 返回初级数据列表

    Args:
        instList(list): 原始数据列表 from OKX
    Returns:
        list: 组装好后的 vo List
    """
    candlerList = []
    logging.info(f'开始处理{len(instList)}个inst ...')
    for instrument in instList:
        quoteCcy = instrument['quoteCcy']
        if quoteCcy == 'USDT':
            instId = instrument['instId']
            curData = client.marked_candlesticks(instId=instId, bar='3M', limit='4')
            
            curCandle = CandleVo()
            for candler in curData:
                if curCandle.instType is None:
                    curCandle.instType = instId
                    curCandle.ts = int(candler[0])
                    curCandle.cs = int(candler[0])
                    curCandle.o = float(candler[1])
                    curCandle.h = float(candler[2])
                    curCandle.l = float(candler[3])
                    curCandle.c = float(candler[4])
                    curCandle.vol = float(candler[5])
                    curCandle.volCcy = float(candler[6])
                    curCandle.volCcyQuote = float(candler[7])
                    curCandle.confirm = candler[8]                    
                else:
                    timeStamp = int(candler[0])
                    curCandle.ts = curCandle.ts if curCandle.ts > timeStamp else timeStamp
                    curCandle.cs = curCandle.cs if curCandle.cs < timeStamp else timeStamp
                    # 若结束时间不等于当前时间戳，说明该条数据不是末尾数据，即不是开盘价
                    # 若结束时间与当前时间戳相同，说明该条数据就是末尾数据，所以当前开盘价就是整体的开盘价
                    curCandle.o = float(candler[1]) if curCandle.cs == timeStamp else curCandle.o
                    curCandle.h = float(candler[2]) if curCandle.h < float(candler[2]) else curCandle.h
                    curCandle.l = float(candler[3]) if curCandle.l > float(candler[3]) else curCandle.l
                    # 若开始时间与当前时间戳相同，说明该条数据就是起始数据，所以收盘价就是整体的收盘价
                    curCandle.c = float(candler[4]) if curCandle.ts == timeStamp else curCandle.c
                    curCandle.vol = curCandle.vol + float(candler[5])
                    curCandle.volCcy = curCandle.volCcy + float(candler[6])
                    curCandle.volCcyQuote = curCandle.volCcyQuote + float(candler[7])
            if curCandle.ts is not None:
                candlerList.append(curCandle) 
    logging.info(f'最终处理得到{len(candlerList)}条初级信息 ...')
    return candlerList


def candles_analysis(candlerList: Optional[list]) -> Optional[Tuple[List[Dict[str, float]]]]:
    """
    通过处理初级数据，得到高级数据列表
    
    Args:
        candlerList(list) : 初级数据列表

    Retruns:
        tuple: 高级数据列表集合
        - ti_sorted_list 回报期望列表
        - vitality_sorted_list 活跃度列表
    """
    # 基于BTC的交易总量
    targetVol = next((curCandler.volCcy for curCandler in candlerList if curCandler.instType == 'BTC-USDT'), None)

    for curCandler in candlerList:
        curCandler.cal_elements()
        curCandler.cal_vitality(targetVol)

    # ti_list = sorted(candlerList, key=lambda x: x.ti, reverse=True)
    ti_list = [{candler.instType: candler.ti} for candler in candlerList]
    ti_sorted_list = sorted(ti_list, key=lambda x: list(x.values())[0], reverse=True)
    
    vitality_list = [{candler.instType: candler.vitality} for candler in candlerList]
    vitality_sorted_list = sorted(vitality_list, key=lambda x: list(x.values())[0], reverse=True)

    return ti_sorted_list, vitality_sorted_list

    

if __name__ == '__main__':
    client = blloseHttpOKE()
    instList = client.get_account_instruments(instType=instrumentType.SPOT.code)
    # instList = [{"auctionEndTime":"","baseCcy":"BTC","ctMult":"","ctType":"","ctVal":"","ctValCcy":"","expTime":"","instFamily":"","instId":"BTC-USDT","instType":"SPOT","lever":"10","listTime":"1611907686000","lotSz":"0.00000001","maxIcebergSz":"9999999999.0000000000000000","maxLmtAmt":"20000000","maxLmtSz":"9999999999","maxMktAmt":"1000000","maxMktSz":"1000000","maxStopSz":"1000000","maxTriggerSz":"9999999999.0000000000000000","maxTwapSz":"9999999999.0000000000000000","minSz":"0.00001","optType":"","quoteCcy":"USDT","ruleType":"normal","settleCcy":"","state":"live","stk":"","tickSz":"0.1","uly":""},{"auctionEndTime":"","baseCcy":"ETH","ctMult":"","ctType":"","ctVal":"","ctValCcy":"","expTime":"","instFamily":"","instId":"ETH-USDT","instType":"SPOT","lever":"10","listTime":"1611907686000","lotSz":"0.000001","maxIcebergSz":"999999999999.0000000000000000","maxLmtAmt":"20000000","maxLmtSz":"999999999999","maxMktAmt":"1000000","maxMktSz":"1000000","maxStopSz":"1000000","maxTriggerSz":"999999999999.0000000000000000","maxTwapSz":"999999999999.0000000000000000","minSz":"0.0001","optType":"","quoteCcy":"USDT","ruleType":"normal","settleCcy":"","state":"live","stk":"","tickSz":"0.01","uly":""},{"auctionEndTime":"","baseCcy":"OKB","ctMult":"","ctType":"","ctVal":"","ctValCcy":"","expTime":"","instFamily":"","instId":"OKB-USDT","instType":"SPOT","lever":"10","listTime":"1611907686000","lotSz":"0.000001","maxIcebergSz":"999999999999.0000000000000000","maxLmtAmt":"20000000","maxLmtSz":"999999999999","maxMktAmt":"1000000","maxMktSz":"1000000","maxStopSz":"1000000","maxTriggerSz":"999999999999.0000000000000000","maxTwapSz":"999999999999.0000000000000000","minSz":"0.1","optType":"","quoteCcy":"USDT","ruleType":"normal","settleCcy":"","state":"live","stk":"","tickSz":"0.01","uly":""},{"auctionEndTime":"","baseCcy":"SOL","ctMult":"","ctType":"","ctVal":"","ctValCcy":"","expTime":"","instFamily":"","instId":"SOL-USDT","instType":"SPOT","lever":"10","listTime":"1611907686000","lotSz":"0.000001","maxIcebergSz":"999999999999.0000000000000000","maxLmtAmt":"20000000","maxLmtSz":"999999999999","maxMktAmt":"1000000","maxMktSz":"1000000","maxStopSz":"1000000","maxTriggerSz":"999999999999.0000000000000000","maxTwapSz":"999999999999.0000000000000000","minSz":"0.001","optType":"","quoteCcy":"USDT","ruleType":"normal","settleCcy":"","state":"live","stk":"","tickSz":"0.01","uly":""},{"auctionEndTime":"","baseCcy":"TON","ctMult":"","ctType":"","ctVal":"","ctValCcy":"","expTime":"","instFamily":"","instId":"TON-USDT","instType":"SPOT","lever":"10","listTime":"1651203490000","lotSz":"0.0001","maxIcebergSz":"99999999999999.0000000000000000","maxLmtAmt":"20000000","maxLmtSz":"99999999999999","maxMktAmt":"1000000","maxMktSz":"1000000","maxStopSz":"1000000","maxTriggerSz":"99999999999999.0000000000000000","maxTwapSz":"99999999999999.0000000000000000","minSz":"0.1","optType":"","quoteCcy":"USDT","ruleType":"normal","settleCcy":"","state":"live","stk":"","tickSz":"0.001","uly":""},{"auctionEndTime":"","baseCcy":"DOGE","ctMult":"","ctType":"","ctVal":"","ctValCcy":"","expTime":"","instFamily":"","instId":"DOGE-USDT","instType":"SPOT","lever":"10","listTime":"1611907686000","lotSz":"0.000001","maxIcebergSz":"999999999999.0000000000000000","maxLmtAmt":"20000000","maxLmtSz":"999999999999","maxMktAmt":"1000000","maxMktSz":"1000000","maxStopSz":"1000000","maxTriggerSz":"999999999999.0000000000000000","maxTwapSz":"999999999999.0000000000000000","minSz":"10","optType":"","quoteCcy":"USDT","ruleType":"normal","settleCcy":"","state":"live","stk":"","tickSz":"0.00001","uly":""}]
    candlerList = data_collection(instList)
    # print(to_json(candlerMap))

    ti_sorted_list, vitality_sorted_list = candles_analysis(candlerList)
    print(ti_sorted_list)
    print(vitality_sorted_list)