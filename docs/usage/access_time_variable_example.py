from datetime import date, datetime, time, timedelta, timezone

from py_ads_client import DATE, DATE_AND_TIME, LTIME, TIME, TIME_OF_DAY, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

time_symbol = ADSSymbol(name="GVL.timeVar", plc_t=TIME)
client.write_symbol(symbol=time_symbol, value=timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5))
time_value = client.read_symbol(time_symbol)
assert time_value == timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5)

ltime_symbol = ADSSymbol(name="GVL.ltimeVar", plc_t=LTIME)
client.write_symbol(symbol=ltime_symbol, value=timedelta(days=200000, hours=2, minutes=3, seconds=4, milliseconds=5))
ltime_value = client.read_symbol(ltime_symbol)
assert ltime_value == timedelta(days=200000, hours=2, minutes=3, seconds=4, milliseconds=5)

date_symbol = ADSSymbol(name="GVL.dateVar", plc_t=DATE)
client.write_symbol(symbol=date_symbol, value=date(year=2020, month=2, day=8))
date_value = client.read_symbol(date_symbol)
assert date_value == date(year=2020, month=2, day=8)

date_and_time_symbol = ADSSymbol(name="GVL.dateAndTimeVar", plc_t=DATE_AND_TIME)
client.write_symbol(
    symbol=date_and_time_symbol,
    value=datetime(year=2106, month=2, day=7, hour=6, minute=28, second=15, tzinfo=timezone.utc),
)
date_and_time_value = client.read_symbol(date_and_time_symbol)
assert date_and_time_value == datetime(year=2106, month=2, day=7, hour=6, minute=28, second=15, tzinfo=timezone.utc)

time_of_day_symbol = ADSSymbol(name="GVL.timeOfDayVar", plc_t=TIME_OF_DAY)
client.write_symbol(symbol=time_of_day_symbol, value=time(hour=23, minute=59, second=59, microsecond=123000))
time_of_day_value = client.read_symbol(time_of_day_symbol)
assert time_of_day_value == time(hour=23, minute=59, second=59, microsecond=123000)

client.close()
