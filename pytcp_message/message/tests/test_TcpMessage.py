import io
from zlib import decompress

from . import TcpMessage, get_rand_content, MSG_LEN

def test_constructor():
    content = get_rand_content()
    msg = TcpMessage(content)
    assert msg._content == content

    msg = TcpMessage()
    assert msg._content is None


def test_to_bytes():
    content = get_rand_content()
    msg = TcpMessage(content)
    assert bytes(msg) == content


def test_get_content():
    content = get_rand_content()
    msg = TcpMessage(content)
    assert msg.get_content() == content


def test_set_content():
    content = get_rand_content()
    msg = TcpMessage()
    msg.set_content(content)
    assert msg._content == content


def test_to_stream_compressed():
    # Test a compressed message
    with io.BytesIO() as test_stream:
        content = get_rand_content()
        msg = TcpMessage(content)
        msg.to_stream(test_stream)

        test_stream.seek(0)

        # Is compressed
        stream_is_compressed = int.from_bytes(
            test_stream.read(TcpMessage._HEADER_BYTES_COMPRESSION),
            byteorder=TcpMessage._BYTE_ORDER
        )
        assert stream_is_compressed == 1

        # Content length
        stream_content_len = int.from_bytes(
            test_stream.read(TcpMessage._HEADER_BYTES_SIZE),
            byteorder=TcpMessage._BYTE_ORDER
        )

        # Make sure compression is working properly; If this fails, probably
        # increment TcpMessage._BYTES_MIN_COMPRESSION
        assert stream_content_len < len(content)

        # Content
        assert decompress(test_stream.read(stream_content_len)) == content


def test_to_stream_decompressed():
    # Test a compressed message
    with io.BytesIO() as test_stream:
        content = get_rand_content(length=MSG_LEN - 1)
        msg = TcpMessage(content)
        msg.to_stream(test_stream)

        test_stream.seek(0)

        # Is compressed
        stream_is_compressed = int.from_bytes(
            test_stream.read(TcpMessage._HEADER_BYTES_COMPRESSION),
            byteorder=TcpMessage._BYTE_ORDER
        )
        assert stream_is_compressed == 0

        # Content length
        stream_content_len = int.from_bytes(
            test_stream.read(TcpMessage._HEADER_BYTES_SIZE),
            byteorder=TcpMessage._BYTE_ORDER
        )

        # Make sure compression is working properly; If this fails, probably
        # increment TcpMessage._BYTES_MIN_COMPRESSION
        assert stream_content_len == len(content)

        # Content
        assert test_stream.read(stream_content_len) == content


def test_from_stream():
    with io.BytesIO() as test_stream:
        # Compressed
        content = get_rand_content()
        msg = TcpMessage(content)
        msg.to_stream(test_stream)

        test_stream.seek(0)

        msg_received = TcpMessage.from_stream(test_stream)

        assert msg.get_content() == msg_received.get_content()

        test_stream.seek(0)

        # Decompressed
        content = get_rand_content(MSG_LEN - 1)
        msg = TcpMessage(content)
        msg.to_stream(test_stream)

        test_stream.seek(0)

        msg_received = TcpMessage.from_stream(test_stream)

        assert msg.get_content() == msg_received.get_content()


def test_connection_closed():
    with io.BytesIO() as test_stream:
        assert TcpMessage.from_stream(test_stream) == None

    with io.BytesIO() as test_stream:
        # "Break connection" after compression byte is written
        test_stream.write(b"0")
        test_stream.seek(0)
        assert TcpMessage.from_stream(test_stream) == None

    with io.BytesIO() as test_stream:
        # "Break connection" after size bytes are written
        test_stream.write(b"0")
        test_stream.write(b"00000000")
        test_stream.seek(0)
        assert TcpMessage.from_stream(test_stream) == None

    with io.BytesIO() as test_stream:
        # "Break connection" after only some of content is written
        test_stream.write(b"0")
        test_stream.write(MSG_LEN.to_bytes(
            TcpMessage._HEADER_BYTES_SIZE,
            byteorder=TcpMessage._BYTE_ORDER
        ))
        test_stream.write(get_rand_content(MSG_LEN // 2))
        test_stream.seek(0)
        assert TcpMessage.from_stream(test_stream) == None
