from bllose.okx.clients.blloseHttpClient import blloseHttpOKE
from bllose.okx.okxEnums.instTypeEnums import instrumentType
from bllose.okx.okxVo.candleVo import CandleVo
import json
from cattr import unstructure

client = blloseHttpOKE()
instList = client.get_account_instruments(instType=instrumentType.SPOT.code)
# print(instList)

candlerMap = {}
for instrument in instList:
    quoteCcy = instrument['quoteCcy']
    if quoteCcy == 'USDT':
        instId = instrument['instId']
        # print(instId)
        curData = client.marked_candlesticks(instId=instId, bar='3M', limit='4')
        # print(f'{instId} -> {curData}')
        
        curCandle = CandleVo()
        for candler in curData:
            if curCandle.ts is None:
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
                curCandle.o = curCandle.o + float(candler[1])
                curCandle.h = curCandle.h + float(candler[2])
                curCandle.l = curCandle.l + float(candler[3])
                curCandle.c = curCandle.c + float(candler[4])
                curCandle.vol = curCandle.vol + float(candler[5])
                curCandle.volCcy = curCandle.volCcy + float(candler[6])
                curCandle.volCcyQuote = curCandle.volCcyQuote + float(candler[7])
        if curCandle.ts is not None:
            candlerMap[instId] = curCandle
            print(json.dumps(unstructure(candlerMap)))

print(json.dumps(unstructure(candlerMap)))

