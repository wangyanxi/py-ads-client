from py_ads_client import ARRAY, INT, STRING, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

int2dArraySymbol = ADSSymbol(name="GVL.int2dArrVar", plc_t=ARRAY(ARRAY(INT, 2), 5))
client.write_symbol(symbol=int2dArraySymbol, value=[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
int2dArrValue = client.read_symbol(int2dArraySymbol)
assert int2dArrValue == [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]

string2dArraySymbol = ADSSymbol(name="GVL.str2dArrVar", plc_t=ARRAY(ARRAY(STRING(10), 2), 5))
client.write_symbol(symbol=string2dArraySymbol, value=[["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"], ["i", "j"]])
str2dArrValue = client.read_symbol(string2dArraySymbol)
assert str2dArrValue == [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"], ["i", "j"]]

client.close()
