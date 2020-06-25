from typing import Tuple, Optional

from .TcpMessage import TcpMessage


class TcpRequest(TcpMessage):
    """
    Class representing a TcpMessage with an additional client_addr member,
    referring to the client that sent the message
    """

    def __init__(self, client_addr: Tuple[str, int], content: bytes = None):
        """
        :param client_addr: The address and port of the client that sent the
            request
        :type client_addr: Tuple[str, int]
        :param content: The message content
        :type content: bytes
        """
        super().__init__(content)
        self._client_addr = client_addr

    def get_client_address(self):
        """
        :return: The (address, port) tuple of the client that sent the request
        :rtype: Tuple[str, int]
        """
        return self._client_addr

    @staticmethod
    def from_stream(client_addr: Tuple[str, int], stream) -> Optional["TcpRequest"]:
        """
        Reads a new TcpMessage from the given stream. If reading from the
        stream times out, returns None

        :param client_addr: The address and port of the client that sent the
            request
        :type client_addr: Tuple[str, int]
        :param stream: The stream to read from
        :type stream: io.FileIO
        :return: The request read from the stream, or None if unable to read
        :rtype: TcpRequest
        """
        tcp_msg = TcpMessage.from_stream(stream)
        if tcp_msg is None:
            return None
        return TcpRequest(client_addr, tcp_msg.get_content())
