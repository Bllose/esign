from blloseHttpClient import blloseHttpOKE
from datetime import datetime

client = blloseHttpOKE()

list = client.get_taker_volume()

for cur in list:
    date_time = datetime.fromtimestamp(int(cur[0]) / 1000)
    formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
    print(formatted_date_time, cur)