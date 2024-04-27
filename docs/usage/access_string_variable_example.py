from py_ads_client import STRING, WSTRING, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

string_symbol = ADSSymbol(name="GVL.stringVar", plc_t=STRING(30))
client.write_symbol(symbol=string_symbol, value="Hello World!")
string_value = client.read_symbol(string_symbol)
assert string_value == "Hello World!"

wstring_symbol = ADSSymbol(name="GVL.wstringVar", plc_t=WSTRING(30))
client.write_symbol(symbol=wstring_symbol, value="你好 World!")
wstring_value = client.read_symbol(wstring_symbol)
assert wstring_value == "你好 World!"

client.close()
