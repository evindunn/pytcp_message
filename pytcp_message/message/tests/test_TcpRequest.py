import io

from . import TcpRequest, TcpMessage, get_rand_content

TEST_ADDR = "127.0.0.1"
TEST_PORT = 8080


def test_constructor():
    client_addr = (TEST_ADDR, TEST_PORT)

    req = TcpRequest(client_addr)
    assert req._client_addr == client_addr

def test_get_client_addr():
    client_addr = (TEST_ADDR, TEST_PORT)

    req = TcpRequest(client_addr)
    assert req.get_client_address() == client_addr

def test_from_stream():
    client_addr = (TEST_ADDR, TEST_PORT)
    content = get_rand_content()

    with io.BytesIO() as test_stream:
        msg = TcpMessage(content)
        msg.to_stream(test_stream)
        test_stream.seek(0)

        req = TcpRequest.from_stream(client_addr, test_stream)
        assert req.get_client_address() == client_addr
        assert req.get_content() == content

        # Simulates 1 byte missing from the stream, like the server hung
        # up before sending the whole message
        test_stream.seek(1)
        req = TcpRequest.from_stream(client_addr, test_stream)
        assert req == None
