import os
from typing import Tuple, Union
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from errno import ENOTCONN

from .message.TcpMessage import TcpMessage


class TcpClient:
    """
    Class representing a client that sends TcpRequests and receives TcpMessages
    in response
    """

    #: Number of times to try receiving a TcpMessage from the server before
    #: giving up
    RETRIES = 3

    #: Number of seconds to wait before a connection times out
    _DEFAULT_TIMEOUT = 3

    def __init__(self, server_addr: Tuple[str, int], timeout: int = _DEFAULT_TIMEOUT):
        """
        :param server_addr: The address of the server to communicate with
        :type server_addr: Tuple[str, int]
        :param timeout: Number of seconds to wait for a response before timing out
        :type timeout: int
        """
        self._server_addr = server_addr
        self._socket = None
        self._wfile = None
        self._rfile = None
        self._retry_count = 0
        self._timeout = timeout
        self._connect()

    def _connect(self):
        """
        Creates a new connection with server_addr
        """
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect(self._server_addr)
        self._rfile = self._socket.makefile("rb")
        self._wfile = self._socket.makefile("wb")

    def _disconnect(self):
        """
        Disconnects from server_addr
        """
        try:
            if not self._rfile.closed:
                self._rfile.close()

            if not self._wfile.closed:
                self._wfile.close()

            self._socket.shutdown(SHUT_RDWR)
            self._socket.close()

        except OSError as e:
            if e.errno != ENOTCONN:
                raise ConnectionError("Could not connect: '{}'".format(e))

    def stop(self):
        """
        Public method for disconnecting from server_addr
        """
        self._disconnect()

    def send(self, data: Union[bytes, str]):
        """
        Sents a TcpMessage to server_addr with data as the message content

        :param data: The TcpMessage content
        :type data: Union[bytes, str]
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        request = TcpMessage(data)
        request.to_stream(self._wfile)

    def receive(self) -> bytes:
        """
        Waits for a response from server_addr. Should only be used after send()
        has been called. If no response is sent from the server, the
        connection is retried up to TcpClient.RETRIES times

        :return: The TcpMessage content from the server's response
        :rtype: bytes
        """
        response = TcpMessage.from_stream(self._rfile)

        while response is None and self._retry_count < TcpClient.RETRIES:
            self._disconnect()
            self._connect()

            response = TcpMessage.from_stream(self._rfile)
            self._retry_count += 1

        self._retry_count = TcpClient.RETRIES

        if response is None:
            return bytes()

        return response.get_content()
