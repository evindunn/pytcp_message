from socketserver import StreamRequestHandler
from .message import TcpMessage, TcpRequest


class _RequestHandler(StreamRequestHandler):
    """
    Handles TcpServer requests using TcpMessage
    """

    def setup(self):
        """
        Creates a new request handler
        """
        super().setup()
        self.request.settimeout(self.server.get_timeout())

    def handle(self):
        """
        Starts a loop that listens for TcpRequests from the client. Once a
        request is read, an empty TcpMessage response is created, and req, res
        are passed to the TcpServer's request handlers. After all handlers have
        run, the TcpMessage response is sent back to the client
        """
        is_connected = True

        while is_connected and self.server.is_running():

            request = TcpRequest.from_stream(self.client_address, self.rfile)

            if request is None:
                is_connected = False
            else:
                response = TcpMessage()

                request_listeners = self.server.get_request_handlers()
                for listener in request_listeners:
                    listener(request, response)

                response.to_stream(self.wfile)
