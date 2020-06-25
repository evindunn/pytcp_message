from socketserver import ThreadingTCPServer

from .message import TcpMessage
from .message import TcpRequest

from ._RequestHandler import _RequestHandler
from threading import Thread, Lock
from typing import Callable, List


class TcpServer(ThreadingTCPServer):
    """
    A threaded TCP server that listens for :class:`TcpRequests <.TcpRequest>`
    and returns :class:`TcpMessages <.TcpMessage>` based on user-defined request
    handlers
    """

    #: See :py:attr:`socketserver.BaseServer.allow_reuse_address`.
    allow_reuse_address = True

    _LISTENER_TYPE = Callable[[TcpRequest, TcpMessage], None]

    def __init__(self, port, address="0.0.0.0", timeout=30):
        """
        :param port: The port to listen on
        :param address: The ip address to listen on
        :param timeout: Seconds to wait for an existing client
            to send a request before closing the connection

        :type port: int
        :type address: str
        :type timeout: int
        """
        super().__init__((address, port), _RequestHandler)
        self._main_thread = None
        self._client_timeout = timeout
        self._request_handlers = list()
        self._thread_lock = Lock()
        self._is_running = False

    def get_timeout(self) -> int:
        """
        :return: The configured session timeout
        :rtype: int
        """
        return self._client_timeout

    def is_running(self) -> bool:
        """
        :return: Whether stop() has been called on the server
        :rtype: bool
        """
        return self._is_running

    def start(self):
        """
        Starts the server in a background thread
        """
        self._is_running = True
        self._main_thread = Thread(target=self.serve_forever, daemon=False)
        self._main_thread.start()

    def stop(self):
        """
        Stops the server's background thread
        """
        with self._thread_lock:
            self._is_running = False
        self.shutdown()
        self._main_thread.join()

    def wait(self):
        """
        Waits for the server to stop. Can be used to bring the server's main
        background thread to the foreground.
        """
        try:
            self._main_thread.join()
        except KeyboardInterrupt:
            self.stop()

    def add_request_handler(self, listener: _LISTENER_TYPE):
        """
        Adds a request handler to the server. Request handlers will be called
        in order and passed (request: TcpRequest, response: TcpMessage).
        After all request handlers have been called, the response is sent to
        the client.

        :param listener: A request handler function that manipulates an incoming
            request/response pair
        :type listener: Callable[[TcpRequest, TcpMessage], None]

        .. code-block:: python3

            def no_op(tcp_req_obj, tcp_msg_obj):
                assert isinstance(tcp_req_obj, TcpRequest)
                assert isinstance(tcp_msg_obj, TcpMessage)
        """
        self._request_handlers.append(listener)

    def get_request_handlers(self) -> List[_LISTENER_TYPE]:
        """
        :return: The list of request handlers for this server
        :rtype: List[Callable[[TcpRequest, TcpResponse], None]]
        """
        return self._request_handlers
