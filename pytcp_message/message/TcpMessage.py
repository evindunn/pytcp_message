import io
from socket import timeout
from typing import Optional
from zlib import compress, decompress


class TcpMessage:
    """
    Class representing an encoded byte array with the following format:
    ::
        | 1 byte         | 8 bytes        |    ...  |
        | is compressed? | content length | content |
    """

    #: Byte order that TcpMessage will use for integer encode/decode
    _BYTE_ORDER = "little"

    #: Minimum content size (in bytes) for which zlib compression is used
    _BYTES_MIN_COMPRESSION = 575

    #: Number of bytes used over the wire to indicate whether the message is
    #: compressed
    _HEADER_BYTES_COMPRESSION = 1

    #: Number of bytes used over the wire to indicate the message size (64-bit int)
    _HEADER_BYTES_SIZE = 8

    def __init__(self, content: bytes = None):
        """
        :param content: The TcpMessage content
        :type content: bytes
        """
        self._content = content

    def __bytes__(self):
        """
        :return: The message content
        :rtype: bytes
        """
        return self._content

    def get_content(self) -> bytes:
        """
        :return: The TcpMessage content
        :rtype: bytes
        """
        return bytes(self)

    def set_content(self, content: bytes):
        """
        :param content: The TcpMessage content
        :type content: bytes
        """
        self._content = content

    def to_stream(self, stream):
        """
        Writes the TcpMessage to the given stream

        :param stream: The stream to write to
        :type stream: io.FileIO
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
    def from_stream(stream) -> Optional["TcpMessage"]:
        """
        Reads a new TcpMessage from the given stream. If reading from the
        stream times out, returns None

        :param stream: The stream to read from
        :type stream: io.FileIO
        :return: The message read from the stream, or None if unable to read
        :rtype: TcpMessage
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
