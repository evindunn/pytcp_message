from typing import Tuple, Union
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR

from .message.TcpMessage import TcpMessage


class TcpClient:
    """
    Class representing a client that sends TcpRequests and receives TcpMessages
    in response
    """

    #: Number of times to try receiving a TcpMessage from the server before
    #: giving up and throwing a ConnectionError
    RETRIES = 3

    def __init__(self, server_addr: Tuple[str, int]):
        """
        :param server_addr: The address of the server to communicate with
        :type server_addr: Tuple[str, int]
        """
        self._server_addr = server_addr
        self._socket = None
        self._wfile = None
        self._rfile = None
        self._retry_count = 0
        self._connect()

    def _connect(self):
        """
        Creates a new connection with server_addr
        """
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.connect(self._server_addr)
        self._rfile = self._socket.makefile("rb")
        self._wfile = self._socket.makefile("wb")

    def _disconnect(self):
        """
        Disconnects from server_addr
        """
        try:
            if self._rfile is not None:
                self._rfile.close()

            if self._wfile is not None:
                self._wfile.close()

            if self._socket is not None:
                self._socket.shutdown(SHUT_RDWR)
                self._socket.close()
        except OSError as e:
            raise ConnectionError("Client disconnected: '{}'".format(e))

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
        self._wfile.flush()

    def receive(self) -> bytes:
        """
        Waits for a response from server_addr. Should only be used after send()
        has been called. If no response is sent from the server, the
        connection is retried up to TcpClient.RETRIES times

        :return: The TcpMessage content from the server's response
        :rtype: bytes
        """
        response = TcpMessage.from_stream(self._rfile)

        if response is None:
            self._retry_count += 1
            if self._retry_count < TcpClient.RETRIES:
                self._disconnect()
                self._connect()
                return self.receive()
            raise ConnectionError("No response from server")

        self._rfile.flush()
        return response.get_content()
