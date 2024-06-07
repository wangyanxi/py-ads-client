from py_ads_client import (
    STRING,
    STRUCT,
    ADSClient,
    ADSCommand,
    ADSReadWriteRequest,
    ADSReadWriteResponse,
    IndexGroup,
    decode_ams_payload,
    encode_ams_payload,
)

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

# https://infosys.beckhoff.com/content/1033/tc3_adssamples_net/1046349195.html?id=5909744511650977426

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

method_handle = client.get_handle_by_name("MAIN.test#echo")

request_payload = encode_ams_payload(
    data={"user": "Alice", "message": "Hello World!"},
    plc_t=STRUCT(fields=[("user", STRING(20)), ("message", STRING(100))]),
)

response_type = STRING(130)

request = ADSReadWriteRequest(
    index_group=IndexGroup.SYMVAL_BYHANDLE,
    index_offset=method_handle,
    read_length=response_type.bytes_length,
    write_data=request_payload,
)

response = client._send_ams_packet(command=ADSCommand.ADSSRVID_READWRITE, payload=request.to_bytes())
assert isinstance(response, ADSReadWriteResponse)

response_message = decode_ams_payload(raw_data=response.data, plc_t=response_type)
print(response_message)

client.release_handle(method_handle)
client.close()
