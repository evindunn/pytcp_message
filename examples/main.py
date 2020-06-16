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

    tcpd.stop()
    time.sleep(5)
    print("Server stopped.\n")

    print("Client sending '{}'...".format(send_message.format("END")))
    tcpc.send(send_message.format("END").encode("utf-8"))
    response = tcpc.receive()
    print("Client Received: '{}'\n".format(response.decode("utf-8")))

    tcpc.stop()
    print("Client closed connection.")


if __name__ == "__main__":
    main()
