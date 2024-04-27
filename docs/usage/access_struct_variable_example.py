from datetime import datetime, timezone

from py_ads_client import DATE_AND_TIME, REAL, STRING, STRUCT, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

symbol = ADSSymbol(
    name="GVL.sensorInfoVar",
    plc_t=STRUCT(fields=[("name", STRING(30)), ("value", REAL), ("updateTime", DATE_AND_TIME)]),
)

client.write_symbol(
    symbol, value={"name": "top", "value": 100.0, "updateTime": datetime(2020, 2, 7, 12, 25, 1, tzinfo=timezone.utc)}
)
sensor_value = client.read_symbol(symbol)
assert sensor_value == {
    "name": "top",
    "value": 100.0,
    "updateTime": datetime(2020, 2, 7, 12, 25, 1, tzinfo=timezone.utc),
}

client.close()
