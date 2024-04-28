# py-ads-client

## Description

`py-ads-client` is a Python library for communicating with Beckhoff's TwinCAT PLC.

## Installation

You can install it via pip:

```bash
pip install py-ads-client
```

## Usage

```
from py_ads_client import ARRAY, INT, ADSClient, ADSSymbol

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

arr_symbol = ADSSymbol(name="GVL.int2dArrVar", plc_t=ARRAY(ARRAY(INT, 2), 5))
arr_value = client.read_symbol(arr_symbol)
print(arr_value)

client.close()
```

it will print something like this: `[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]`

for more information, please refer to the [documentation](https://py-ads-client.readthedocs.io)
