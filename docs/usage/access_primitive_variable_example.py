from py_ads_client import BOOL, INT, REAL, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

bool_symbol = ADSSymbol(name="GVL.boolVar", plc_t=BOOL)
client.write_symbol(symbol=bool_symbol, value=True)
bool_value = client.read_symbol(bool_symbol)
assert bool_value is True

int_symbol = ADSSymbol(name="GVL.intVar", plc_t=INT)
client.write_symbol(symbol=int_symbol, value=123)
int_value = client.read_symbol(int_symbol)
assert int_value == 123

real_symbol = ADSSymbol(name="GVL.realVar", plc_t=REAL)
client.write_symbol(symbol=real_symbol, value=100.23)
real_value = client.read_symbol(real_symbol)
assert round(real_value, 2) == 100.23

client.close()
