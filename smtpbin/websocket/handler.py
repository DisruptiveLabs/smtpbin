import asyncore
import base64
import hashlib
import logging
import re
import struct

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Constants
MAGIC_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

CLOSE_CODES = {
    1000: "OK",
    1001: "going away",
    1002: "protocol error",
    1003: "unsupported type",
    # 1004: - (reserved)
    # 1005: no status code (internal)
    # 1006: connection closed abnormally (internal)
    1007: "invalid data",
    1008: "policy violation",
    1009: "message too big",
    1010: "extension required",
    1011: "unexpected error",
    # 1015: TLS failure (internal)
}


class WebSocketProtocolError(Exception): pass


class WebSocket(asyncore.dispatcher_with_send):
    handshake = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "WebSocket-Origin: %(origin)s\r\n"
        "WebSocket-Location: ws://%(bind)s:%(port)s/\r\n"
        "Sec-Websocket-Origin: %(origin)s\r\n"
        "Sec-Websocket-Location: ws://%(bind)s:%(port)s/\r\n"
    )
    handshake_accept = "Sec-WebSocket-Accept: %(acceptstring)s\r\n"
    handshake_foot = "\r\n"

    OP_CONT = 0x00
    OP_TEXT = 0x01
    OP_BINARY = 0x02

    OP_CLOSE = 0x08
    OP_PING = 0x09
    OP_PONG = 0x0A

    def __init__(self, client, addr, server):
        asyncore.dispatcher.__init__(self, client)
        self.out_buffer = b''
        self.data = b""

        self.addr, self.port = addr
        self.client = client
        self.server = server
        self.database = self.server.database

        self.handshaken = False
        self.header = ""

        self.partial_frame = b''
        self.partial_opcode = 0

    def handle_read(self):
        if not self.handshaken:
            data = self.recv(1024)
            self.header += data.decode()
            if self.header.find('\r\n\r\n') != -1:
                parts = self.header.split('\r\n\r\n', 1)
                self.header = parts[0]
                if self.dohandshake(self.header, parts[1]):
                    log.info("WebSocket open from {}:{}".format(self.addr, self.port))
                    self.handshaken = True
        else:
            opcode, data = self.read_frame()
            if opcode == WebSocket.OP_PING:
                self.send(data, WebSocket.OP_PONG)
            elif opcode == WebSocket.OP_CLOSE:
                self.close()
            elif opcode == WebSocket.OP_BINARY:
                self.ondata(data)
            elif opcode == WebSocket.OP_TEXT:
                self.onmessage(data)

    def dohandshake(self, header, key=None):
        log.debug("Begin handshake: %s" % header)
        digitRe = re.compile(r'[^0-9]')
        spacesRe = re.compile(r'\s')
        part_1 = part_2 = origin = None

        response = None

        for line in header.split('\r\n')[1:]:
            name, value = line.split(': ', 1)
            if name.lower() == "sec-websocket-key":
                combined = value + MAGIC_GUID
                response = base64.b64encode(hashlib.sha1(combined.encode()).digest()).decode()

            elif name.lower() == "sec-websocket-key1":
                key_number_1 = int(digitRe.sub('', value))
                spaces_1 = len(spacesRe.findall(value))
                if spaces_1 == 0:
                    return False
                if key_number_1 % spaces_1 != 0:
                    return False
                part_1 = key_number_1 / spaces_1
            elif name.lower() == "sec-websocket-key2":
                key_number_2 = int(digitRe.sub('', value))
                spaces_2 = len(spacesRe.findall(value))
                if spaces_2 == 0:
                    return False
                if key_number_2 % spaces_2 != 0:
                    return False
                part_2 = key_number_2 / spaces_2
            elif name.lower() == "origin":
                origin = value

        if part_1 and part_2:
            log.debug("Using challenge + response")
            challenge = struct.pack('!I', part_1) + struct.pack('!I', part_2) + key
            response = hashlib.md5(challenge).digest()
            handshake = WebSocket.handshake + response + WebSocket.handshake_foot

        elif response:
            log.debug("Using sec-websocket-key")
            handshake = WebSocket.handshake + WebSocket.handshake_accept + WebSocket.handshake_foot

        else:
            log.warning("Not using challenge + response")
            handshake = WebSocket.handshake + response + WebSocket.handshake_foot

        handshake = handshake % {'origin': origin,
                                 'port': self.server.port,
                                 'bind': self.server.socketbind,
                                 'acceptstring': response}

        log.debug("Sending handshake %s" % handshake)
        self.out_buffer = handshake.encode()
        return True

    def read_frame(self, require_mask=False):
        data = self.recv(2)
        head1, head2 = struct.unpack('!BB', data)

        # #TODO: Handle FIN properly
        fin = head1 & 0b10000000
        rsv = head1 & 0b01110000
        opcode = head1 & 0b00001111
        mask = head2 & 0b10000000
        length = head2 & 0b01111111

        if rsv:
            raise WebSocketProtocolError("Reserved bits must be 0")
        if require_mask and not mask:
            raise WebSocketProtocolError("Frames must be masked")

        if length == 126:
            data = self.recv(2)
            length, = struct.unpack('!H', data)
        elif length == 127:
            data = self.recv(8)
            length, = struct.unpack('!Q', data)

        if mask:
            mask_bits = self.recv(4)

        data = self.recv(length)

        if mask:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        if not fin:
            if opcode != WebSocket.OP_CONT:
                self.partial_opcode = opcode
            self.partial_frame += data
            return None, None

        if fin and opcode == WebSocket.OP_CONT:
            opcode = self.partial_opcode
            data = self.partial_frame + data

            self.partial_opcode = 0
            self.partial_frame = b''

        return opcode, data.decode()

    def write_frame(self, opcode, message):
        if not isinstance(message, bytes):
            message = message.encode()

        frame = b''
        fin = 0b10000000
        rsv = 0b00000000
        mask = 0b00000000

        length = len(message)

        frame += struct.pack('!B', fin | rsv | opcode)

        if length < 126:  # Short
            frame += struct.pack('!B', mask | length)
        elif length < 0xFFFF:  # Word length
            frame += struct.pack('!B', mask | 126)
            frame += struct.pack('!H', length)
        elif length < 0xFFFFFFFFFFFFFFFF:  # 8 Byte length
            frame += struct.pack('!B', mask | 127)
            frame += struct.pack('!Q', length)

        frame += message

        return frame

    def ondata(self, data):
        print("Got data: %s" % data)

    def onmessage(self, data):
        print("Got message: %s" % data)

    def send(self, data, opcode=OP_TEXT):
        if self.handshaken:
            self.out_buffer += self.write_frame(opcode, data)
        else:
            self.out_buffer += ("\x00%s\xff" % data).encode()
