#!/usr/bin/python3
import socket
import threading
import re
import time
import logging
import argparse

BUFFER = 2048
HOST = ''

parser = argparse.ArgumentParser(description="TCP echo server. Provides control to repetition multiplier "
                                             "and delay parameter. Those parameters can be set by sending special "
                                             "commands to server as a text message. "
                                             "cmd_repeat_[VALUE] - sets multiplier for echo data 1...99. "
                                             "cmd_delay_[VALUE] - sets delay in seconds for each echo data"
                                             "package 0...99. "
                                             "cmd_help - provides help information for echo server commands. "
                                             "Each TCP session starts with cmd_repeat set to 1 and cmd_delay "
                                             "set to 0. ")
parser.add_argument("port_number", help="port number for echo server", type=int)
parser.add_argument("-6", "--ipv6", help="runs server with IPv6 protocol", action="store_true")
parser.add_argument("-d", "--debug", help="turns on debug messages", action="store_true")
parser.add_argument("-v", "--version", help="returns version information", action="version", version="%(prog)s 1.1")
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MyThread(threading.Thread):
    def __init__(self, thread_id, socket_instance, address_instance):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.socket_instance = socket_instance
        self.address_instance = address_instance

    def run(self):
        logging.info("Starting {0}".format(self.name))
        handler(self.socket_instance, self.address_instance)
        logging.info("Exiting {0}".format(self.name))


def handler(current_socket, current_address):
    repetitions = 1
    send_delay = 0
    count_byte = 0
    while 1:
        logging.info('before recv() >>>>>>>>>>>>>>>>>>>>>>>')
        data = current_socket.recv(BUFFER)
        logging.info('data is >>>>>>>>>>>>>>>>: {0}'.format(data))

        if not data:
            logging.info(111111)
            break

        logging.info("received:{0} ".format(data))
        count_byte = count_byte + 1

        if re.match(b"cmd_repeat_\d{1,2}", data):
            detected_digits = re.findall(r"\d{1,2}", data.decode("utf-8"))
            repetitions = int(detected_digits[0])

            if repetitions == 0:
                message = "Multiplier cannot be set to 0\n"
                repetitions = 1
                current_socket.send(bytes(message, "utf-8"))

            message = "Detected repetition command. Returned data will be multiplied by " + str(repetitions) + "\n"
            current_socket.send(bytes(message, "utf-8"))
            continue

        if re.match(b"cmd_delay_\d{1,2}", data):
            detected_digits = re.findall(r"\d{1,2}", data.decode("utf-8"))
            send_delay = int(detected_digits[0])
            message = "Detected timeout command. Returned data will be delayed by " + str(send_delay) + " seconds\n"
            current_socket.send(bytes(message, "utf-8"))
            continue

        if re.match(b"cmd_help", data):
            message = "Available commands:\n" \
                      "cmd_repeat_[VALUE] - sets multiplier for echo data [1]...99\n" \
                      "cmd_delay_[VALUE] - sets delay in seconds for each echo data package [0]...99\n" \
                      "cmd_help - provides help information for echo server commands\n"
            current_socket.send(bytes(message, "utf-8"))
            continue

        for i in range(repetitions):
            time.sleep(send_delay)
            current_socket.send(data)

        logging.info("{0} sent {1}x {2}".format(current_address, repetitions, data))
        logging.info("the number of bytes are {0}".format(count_byte))

    current_socket.close()
    logging.info("{0} - connection closed".format(current_address))


if __name__ == '__main__':
    ADDRESS = (HOST, args.port_number)
    if args.ipv6:
        server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDRESS)
    server_socket.listen(5)
    thread_number = 1
    logging.info("Waiting for connections. Listening on port {0}".format(args.port_number))
    while 1:
        client_socket, address = server_socket.accept()
        logging.info("Incoming connection from: {0}".format(address))

        thread = MyThread(thread_number, client_socket, address)
        thread.start()
        thread_number += 1
