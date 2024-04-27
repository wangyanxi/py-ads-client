from py_ads_client import ARRAY, INT, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

symbol = ADSSymbol(name="GVL.int1dArrVar", plc_t=ARRAY(INT, 5))
client.write_symbol(symbol=symbol, value=[1, 2, 3, 4, 5])
sensors = client.read_symbol(symbol)
assert sensors == [1, 2, 3, 4, 5]

client.close()
