from io import BufferedIOBase
from typing import Tuple, Union
from .TcpMessage import TcpMessage


class TcpRequest(TcpMessage):
    """
    Class representing a TcpMessage with an additional client_addr member,
    refering to the client that sent the message
    """

    def __init__(self, client_addr: Tuple[str, int], content: bytes = None):
        """
        :param client_addr: Tuple[str, int] The address and port of the client
        that sent the request
        :param content: bytes The message content
        """
        super().__init__(content)
        self._client_addr = client_addr

    def get_client_address(self):
        return self._client_addr

    @staticmethod
    def from_stream(client_addr: Tuple[str, int], stream: BufferedIOBase) -> Union["TcpRequest", None]:
        """
        Reads a new TcpMessage from the given stream. If reading from the
        stream times out, returns None
        :param client_addr: Tuple[str, int] The address and port of the client
        that sent the request
        :param stream: The stream to read from
        :return: TcpRequest The request read from the stream, or None if unable
        to read
        """
        tcp_msg = TcpMessage.from_stream(stream)
        if tcp_msg is None:
            return None
        return TcpRequest(client_addr, tcp_msg.get_content())
