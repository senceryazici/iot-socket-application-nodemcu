#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from IoTSocketServer.iot_socket_server import IoTServer, IoTClient
import os


class MyIoTDevice(IoTClient):
    """docstring for MyIoTDevice."""
    def callback(self, data):
        # Do whatever you want with the data
        pass


log_path = os.path.expanduser("~") + "/.log/IoTSocketServer"
if not os.path.exists(log_path + "/"):
    os.system("mkdir -p " + log_path + "/")

if __name__ == "__main__":
    device_lookup = {
        "192.168.1.205": MyIoTDevice
    }
    host = IoTServer(client_lookup=device_lookup, log_path=log_path)
    try:
        host.start()
        host.spin(diagnose=False)
    except KeyboardInterrupt:
        host.socket.close()
