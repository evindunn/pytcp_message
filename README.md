# pytcp_message
[View on PyPI](https://pypi.org/project/pytcp-message/)

[<img src="https://github.com/evindunn/pytcp_message/workflows/Test/Publish/badge.svg">](https://github.com/evindunn/pytcp_message/actions?query=workflow%3ATest%2FPublish)
[![Coverage Status](https://coveralls.io/repos/github/evindunn/pytcp_message/badge.svg?branch=master)](https://coveralls.io/github/evindunn/pytcp_message?branch=master)

Sends/receives messages in the following format:
```text
| 1 byte         | 8 bytes        |  ... |
| is compressed? | content length | data |
```
Messages over 575 bytes are automatically compressed/decompressed with zlib

The main classes are [TcpServer](pytcp_message/TcpServer.py) and
[TcpClient](pytcp_message/TcpClient.py), which use the above message format
to communicate with each other.

TCP response messages are implemented in [TcpMessages](pytcp_message/message/TcpMessage.py).
`TcpMessage` has one member, `content`, which is the `bytes` content of the message 
that will be sent. It also includes convenience methods for writing that content
to and from a TCP socket using the above format.

`TcpServer` opens a connection when a request comes in, then listens on that
connection until either the client closes the connection or `timeout` seconds, 
passed to the constructor, have elapsed. The default is 30. This allows multiple
messages to be sent without re-creating new connections.

TCP request messages are implemented using [TcpRequests](pytcp_message/message/TcpMessage.py),
which inherit from `TcpMessage`. `TcpRequests` include an additional member,
`client_addr`, the requester's address. 

When a request comes in, `TcpServer` creates a `TcpRequest` object with the 
client's address and content of the incoming message, along with an empty `TcpMessage` 
response. These objects are passed to a list of request handlers attached
to the server. After all handlers have run, `TcpServer` sends the `TcpMessage`
response object to the client.

This allows the server to implement a Chain of Responsibility similar to 
Express/NodeJS. By passing objects to the various handlers, requests and 
responses can be modified by each method in the chain.

Example:
```python
import time

from pytcp_message import TcpServer, TcpClient
from datetime import datetime

ADDR = "127.0.0.1"
PORT = 8080


def log_request(req, _):
    now = datetime.now().strftime("%F %T")
    print(
        "[{}] {} <-- {}".format(
            now,
            req.get_client_address()[0],
            req.get_content().decode("utf-8")
        )
    )


def send_response(req, res):
    res.set_content("You are {}:{}".format(
        *req.get_client_address()
    ).encode("utf-8"))


def log_response(req, res):
    now = datetime.now().strftime("%F %T")
    print("[{}] {} --> {}".format(
        now,
        res.get_content().decode("utf-8"),
        req.get_client_address()[0]
    ))


def main():
    send_message = "Hello{}"

    tcpd = TcpServer(address=ADDR, port=PORT, timeout=5)
    tcpd.add_request_handler(log_request)
    tcpd.add_request_handler(send_response)
    tcpd.add_request_handler(log_response)

    tcpd.start()
    print("Server running on tcp://{}:{}...".format(ADDR, PORT))

    tcpc = TcpClient((ADDR, PORT))

    for i in range(0, 10):
        print("Client sending '{}'...".format(send_message.format(i)))
        tcpc.send(send_message.format(i).encode("utf-8"))
        response = tcpc.receive()
        print("Client Received: '{}'\n".format(response.decode("utf-8")))

    tcpc.stop()
    print("Client closed connection.")

    tcpd.stop()
    time.sleep(5)
    print("Server stopped.\n")


if __name__ == "__main__":
    main()
```

Output:
```text
Server running on tcp://127.0.0.1:8080...
Client sending 'Hello0'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello0
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello1'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello1
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello2'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello2
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello3'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello3
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello4'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello4
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello5'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello5
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello6'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello6
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello7'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello7
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello8'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello8
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client sending 'Hello9'...
[2020-06-19 21:01:28] 127.0.0.1 <-- Hello9
[2020-06-19 21:01:28] You are 127.0.0.1:34360 --> 127.0.0.1
Client Received: 'You are 127.0.0.1:34360'

Client closed connection.
Server stopped.
```
