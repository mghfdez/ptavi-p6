#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

# import random
import SocketServer
import sys
import os
import re


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """
    ALLOW = 'INVITE|ACK|BYE|CANCEL|OPTIONS|REGISTER'
    PROTOCOL = r'(' + ALLOW + ')\ssip:\w+@(\w+|\d+(\.\d+){3}):\d+\sSIP/2.0'
    PORT_RTP = 23032  # random.randint(1024, 65535)

    def send_single(self, text):
        print 'Send -- ', text[:-4]
        # send Tring Ring and ACK # Port sip: 5060
        self.socket.sendto(text, self.client_address)
        # self.wfile.write(text)

    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read().strip()
            # Recive INVITE|ACK|BYE sip:receptor@IP:port SIP/2.0
            m = re.match(self.PROTOCOL, line)
            if not m is None:
                if line.split()[0] == 'INVITE':
                    # INVITE: client 5065 --> servidor 5060
                    # 100 Trying
                    self.send_single('SIP/2.0 100 Trying\r\n\r\n')
                    # 180 Ring
                    self.send_single('SIP/2.0 180 Ring\r\n\r\n')
                    # Send 200 OK, No hay port random. no need 'sdp'
                    # sdp = 'm=audio ' + str(self.PORT_RTP) + \
                    #       ' RTP/AVP 8 101\r\n'
                    # self.send_single('SIP/2.0 200 OK\r\n' + sdp + '\r\n')
                    self.send_single('SIP/2.0 200 OK\r\n\r\n')
                elif line.split()[0] == 'ACK':
                    # ACK client 5065 -> servidor 5060
                    # RTP servidor 5010 --> client 12440 (random)
                    ip = self.client_address[0]
                    aEjecutar = './mp32rtp -i ' + ip + ' -p ' \
                                + '23032 < ' + sys.argv[3]
                    #            + str(self.PORT_RTP) + ' < ' + sys.argv[3]
                    print "Vamos a ejecutar $ ", aEjecutar
                    os.system(aEjecutar)  # otro task mejor
                    # client espera 5 seg.
                    print '-- Send end --'
                elif line.split()[0] == 'BYE':
                    # Solo Send 200 OK
                    # BYE: client 5065 -> servidor 5060
                    self.send_single('SIP/2.0 200 OK\r\n\r\n')
                else:
                    # YES -> INVITE|ACK|BYE   NOT -> CANCEL|OPTIONS|REGISTER
                    self.send_single('SIP/2.0 405 Method Not Allowed\r\n\r\n')
            elif line:
                # bad msg:
                self.send_single('SIP/2.0 400 Bad Request\r\n\r\n')
            else:
                break


if __name__ == "__main__":
    if len(sys.argv) != 4 or not os.path.exists(sys.argv[3]):
        # 1. pregunta -> IP servie para que?
        sys.exit('Usage: python server.py IP port audio_file')
    else:
        # Creamos servidor de eco y escuchamos
        serv = SocketServer.UDPServer(("", int(sys.argv[2])), EchoHandler)
        print "Listening..."
        serv.serve_forever()
