import random

from pytcp_message.message import TcpMessage, TcpRequest

MSG_LEN = TcpMessage._BYTES_MIN_COMPRESSION


def get_rand_content(length=MSG_LEN):
    return "".join(random.choices(["a", "b", "c"], k=length)).encode("utf-8")
