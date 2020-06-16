import io
from zlib import compress, decompress
from socket import timeout
from typing import Union, Type, TypeVar

StreamType = TypeVar("StreamType", bound=io.FileIO)


class TcpMessage:
    """
    Class representing an encoded byte array with the following format:
    | 1 byte         | 8 bytes        |  ... |
    | is compressed? | content length | data |
    """
    _BYTE_ORDER = "little"
    _BYTES_MIN_COMPRESSION = 575
    _HEADER_BYTES_COMPRESSION = 1
    _HEADER_BYTES_SIZE = 8

    def __init__(self, content: bytes = None):
        """
        :param content: bytes The TcpMessage content
        """
        self._content = content

    def __bytes__(self):
        return self._content

    def get_content(self) -> bytes:
        """
        :return: bytes The TcpMessage content
        """
        return bytes(self)

    def set_content(self, content: bytes):
        """
        :param content: bytes The TcpMessage content
        """
        self._content = content

    def to_stream(self, stream: StreamType):
        """
        Writes the TcpMessage to the given stream
        :param stream: io.BufferedIOBase The stream to write to
        """
        content = self._content[:]
        content_len = len(content)
        is_compressed = 0

        # Compression
        if content_len >= TcpMessage._BYTES_MIN_COMPRESSION:
            is_compressed = 1
            content = compress(content)
            content_len = len(content)

        is_compressed = is_compressed.to_bytes(
            TcpMessage._HEADER_BYTES_COMPRESSION,
            byteorder=TcpMessage._BYTE_ORDER
        )
        content_len = content_len.to_bytes(
            TcpMessage._HEADER_BYTES_SIZE,
            byteorder=TcpMessage._BYTE_ORDER
        )

        stream.write(is_compressed + content_len + content)
        stream.flush()

    @staticmethod
    def from_stream(stream: StreamType) -> Union["TcpMessage", None]:
        """
        Reads a new TcpMessage from the given stream. If reading from the
        stream times out, returns None
        :param stream: The stream to read from
        :return: TcpMessage The message read from the stream, or None if
        unable to read
        """
        try:
            is_compressed = stream.read(TcpMessage._HEADER_BYTES_COMPRESSION)
            if len(is_compressed) == 0:
                return None

            is_compressed = int.from_bytes(
                is_compressed,
                byteorder=TcpMessage._BYTE_ORDER
            )

            content_len = stream.read(TcpMessage._HEADER_BYTES_SIZE)
            if len(content_len) == 0:
                return None

            content_len = int.from_bytes(
                content_len,
                byteorder=TcpMessage._BYTE_ORDER
            )

            content = stream.read(content_len)
            if len(content) < content_len:
                return None

            if is_compressed == 1:
                content = decompress(content)

            stream.flush()
            return TcpMessage(content)

        except timeout:
            return None
