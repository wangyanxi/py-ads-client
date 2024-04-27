from datetime import datetime, timezone

from py_ads_client import ARRAY, DATE_AND_TIME, REAL, STRING, STRUCT, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

structArrValues = [
    {"name": "top", "value": 100.0, "updateTime": datetime(2020, 2, 7, 12, 25, 1, tzinfo=timezone.utc)},
    {"name": "middle", "value": 200.0, "updateTime": datetime(2020, 2, 7, 12, 35, 2, tzinfo=timezone.utc)},
    {"name": "bottom", "value": 300.0, "updateTime": datetime(2020, 2, 7, 12, 55, 3, tzinfo=timezone.utc)},
]

symbol = ADSSymbol(
    name="GVL.sensorInfoArrVar",
    plc_t=ARRAY(STRUCT(fields=[("name", STRING(30)), ("value", REAL), ("updateTime", DATE_AND_TIME)]), 3),
)
client.write_symbol(symbol=symbol, value=structArrValues)
values = client.read_symbol(symbol)
assert values == structArrValues

client.close()
