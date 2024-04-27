import threading
import time

from py_ads_client import INT, ADSClient, ADSSymbol

plc_ip = "192.168.88.20"
plc_ams_net_id = "192.168.88.20.1.1"
local_ams_net_id = "192.168.88.100.1.1"

client = ADSClient(local_ams_net_id=local_ams_net_id)
client.open(target_ams_net_id=plc_ams_net_id, target_ip=plc_ip)

int_symbol = ADSSymbol(name="GVL.intVar", plc_t=INT)

client.write_symbol(symbol=int_symbol, value=000)

time.sleep(1)


def device_notification_watcher() -> None:
    while True:
        symbol, notification, data = client.device_notification_queue.get()
        print(f"device notification, name: {symbol.name}, value: {data}, update_time: {notification.update_time}")


device_notification_watcher_thread = threading.Thread(target=device_notification_watcher, daemon=True)
device_notification_watcher_thread.start()

client.add_device_notification(symbol=int_symbol)

client.write_symbol(symbol=int_symbol, value=111)
time.sleep(0.1)
client.write_symbol(symbol=int_symbol, value=222)
time.sleep(0.5)

client.close()
