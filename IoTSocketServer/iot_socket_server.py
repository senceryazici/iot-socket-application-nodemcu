#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from __future__ import print_function
import socket
import sys
import threading
import yaml
import time
import logging
from IoTSocketServer.iot_logger import IotServerLogger, IotClientLogger


class IotProtocol(object):
    """The procotol to follow for received bytes, when CR&NL are received,
    the message is packed up and the callback is fired

    :param callback: the callback function which will be fired.
    :type callback: function
    :param use_uc_time_as_default: the flag that sets the source of time, check self.receive() for more details.
    :type use_uc_time_as_default: bool
    """
    def __init__(self, callback, use_uc_time_as_default=True):
        self.callback = callback
        self.message = ""
        self.use_uc_time_as_default = use_uc_time_as_default

    def receive(self, rcv):
        """Appends the byte to the self.message, checks if CR and NL chars exist in self.message,
        if so, splits the message and runs self.callback()

        if self.use_uc_time_as_default is True(default), the data['time'] will be the original microcontroller
        time in seconds,
        if not, the data['time'] will be system time, time.time(); and the data['microcontroller-time'] will be
        the microcontroller time in seconds.

        :param rcv: Received byte.
        :type rcv: bytes
        :raises KeyError: If the message does not contain "time" or "device" keys.
        """
        rcv = rcv.decode('UTF-8')
        self.message += rcv
        if "\r\n" in self.message:
            parsablr_msg = self.message.split("\r\n")[0]
            self.message = ""
            try:
                data = yaml.safe_load(parsablr_msg)

                if not ("time" in data.keys() and "device" in data.keys()):
                    raise KeyError("Message packets must have, 'time' and 'device' arguments.")
                    return

                if not self.use_uc_time_as_default:
                    data["microcontroller-time"] = data["time"] / 1000.0
                    data["time"] = time.time()
                else:
                    data["time"] = data["time"] / 1000.0

                self.callback(data)
            except Exception as e:
                print("Parse Error:", e)


class IoTClient(object):
    """The IoT Client object, which briefly contains the device and connection information.
    :param socket: The connection-established socket object.
    :type socket: socket.socket

    :param address: IP Address of the client
    :type address: string

    :param port: The port of the socket.
    :type port: int

    :param hostname: The hostname of the device, for example; test@mypc$ -> hostname is 'mypc', username is 'test'
    :type hostname: string

    :param protocol: The protocol that is used to decode incoming bytes.
    :type protocol: IotProtocol

    :param server: The server object, for removing this client from the server.client_pool
    :type server: IoTServer

    :param log_path: The directory to create log files.
    :type log_path: string
    """

    def __init__(self, socket=None, address=None, port=None, hostname=None, protocol=IotProtocol, server=None, log_path="."):
        self.socket = socket
        self.address = address
        self.port = port
        self.hostname = hostname
        self._listen = False
        self.protocol = IotProtocol(self._callback)
        self.timeout = 5.0
        self.server = server
        self.log_path = log_path
        self.logger = IotClientLogger(self.__str__(), log_path=self.log_path)

    def _callback(self, data):
        self.callback(data)
        if "device" in data.keys() and self.hostname == "":
            self.hostname = "iot-device-" + str(data["device"])
            self.logger.name = self.__str__()
        self.logger.info(str(data))

    def callback(self, data):
        """On default, the client will just pass this function,
        Use your MyDevice object which has the IoTClient as a base class, which has a custom
        callback function."""
        pass

    def close(self):
        """Terminates the active connection, stops listening from the client, and removes this instace
        from the server.client_pool"""
        self._listen = False
        self.socket.close()
        if self.server is not None:
            self.server.client_pool.remove(self)

    def listen(self):
        """Creates a thread for self._receive function, starts listening the client.
        :raises: Any Exceptions threading.Thread object can throw."""

        self._listen = True
        self.thread = threading.Thread(target=self._receive)
        self.thread.daemon = True
        self.thread.start()
        self.socket.settimeout(self.timeout)
        # self.thread.join()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.address == other.address and self.port == other.port
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        hostname = "client"
        if self.hostname != "" and self.hostname is not None:
            hostname = self.hostname
        return hostname + "@" + str(self.address) + ":" + str(self.port)

    def _receive(self):
        try:
            while self._listen:
                rcv = self.socket.recv(1)
                if rcv == b"":
                    raise Exception(str(self) + " disconnected.")
                self.protocol.receive(rcv)

        except Exception as e:
            self.close()
            self.logger.exception("Exception on receiving for client@{}:{}\n{}".format(self.address, self.port, e))


class IoTServer(object):
    """Server object which handles the client communications from the iot devices

    :param client_lookup: A dictionary containing 1 or more ip address as a key, and a client device class which has IoTClient as a base class, {"ip.adreess.of.device": MyIoTDevice}
    :type client_lookup: dict

    :raises socket.error: If the program fails to bind to given ip and port.
    :raises: Any exceptions logging.Logger or socket.socket objects can throw.
    """

    def __init__(self, log_path=".", client_lookup=None):
        self.host = '192.168.1.195'    # Symbolic name, meaning all available interfaces
        self.port = 8898               # Arbitrary non-privileged port
        self.spin_rate = 1.0           # Hz
        self.client_pool = []
        self.accept_new_connections = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_lookup = client_lookup
        self.start_time = time.time()
        self.log_path = log_path

        # SETUP LOGGER
        self.logger = IotServerLogger("logger-host@192.168.1.195:8898", log_path=self.log_path)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Socket Created.")

        try:
            self.socket.bind((self.host, self.port))
        except socket.error as msg:
            # self.logger.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] + "exiting...")
            sys.exit()
        self.logger.info('Socket bind complete')

    def print_diagnose(self):
        diag = ["Current IP Address: " + str(self.host),
                "Current Port: " + str(self.port),
                "Active Connections: " + str(len(self.client_pool)),
                "Known Devices: " + str(len([i for i in self.client_pool if i.address in self.client_lookup.keys()])),
                "Started On: " + str(self.start_time),
                "Alive for: " + str(str(time.time() - self.start_time) + " seconds."),
                "Currently Accepting New Connections: " + str(self.accept_new_connections)]
        print("\033[H\033[J”"[:-1] + "\n".join(diag))

    def start(self):
        """Starts a thread for self.listen() function."""
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def listen(self):
        """Starts threads for incoming connections

        :raises socket.herror: If a hostname couldn't be determined for clients' ip address
        """
        self.socket.listen(10)
        self.logger.info("Socket now listening")

        while self.accept_new_connections:
            conn, addr = self.socket.accept()

            hostname = ""
            try:
                # hostname = "iot-device-0"
                hostname = socket.gethostbyaddr(addr[0])
            except socket.herror as e:
                self.logger.warning("Couldn't find hostname for ip:{}".format(addr[0]))

            client = None
            if isinstance(self.client_lookup, type({})):
                if addr[0] in self.client_lookup.keys():
                    client = self.client_lookup[addr[0]](server=self, hostname=hostname,
                                                         address=addr[0], port=addr[1], socket=conn,
                                                         log_path=self.log_path)
                else:
                    client = IoTClient(server=self, hostname=hostname, address=addr[0],
                                       port=addr[1], socket=conn, log_path=self.log_path)
            else:
                client = IoTClient(server=self, hostname=hostname, address=addr[0],
                                   port=addr[1], socket=conn, log_path=self.log_path)
            self.logger.info("Registering client: " + client.__str__())
            self.client_pool.append(client)
            client.listen()

    def spin(self, diagnose=False):
        """Runs diagnosing functions for the server,
        :todo: Add cleanup() to maintain a clean server."""
        while True:
            if diagnose:
                self.print_diagnose()
            time.sleep(1.0 / self.spin_rate)

    def close(self):
        """Stops receiving new connections, terminates all active connections,
        closes the host socket."""
        self.accept_new_connections = False
        kill = [c.close for c in self.client_pool]
        self.socket.close()


class MyIoTDevice(IoTClient):
    """Test Device."""
    def callback(self, data):
        # self.protocol.use_uc_time_as_default = False
        # print(str(data))
        pass


if __name__ == "__main__":
    import os
    log_path = os.path.expanduser("~") + "/.log/IoTSocketServer"
    if not os.path.exists(log_path + "/"):
        os.system("mkdir -p " + log_path + "/")

    device_lookup = {
        "192.168.1.205": MyIoTDevice
    }
    host = IoTServer(device_lookup, log_path)
    try:
        host.start()
        host.spin(diagnose=False)
    except KeyboardInterrupt:
        host.socket.close()
