"""
Original Author: Ryan Stracener
"""

import json, socket

class Device:
    def __init__(
        self,
        ipv4_addr,
        port,
        service=None,
        serial_number=None,
        firmware_version=None
    ):
        # Public fields
        self.ipv4_addr = ipv4_addr
        self.port = port
        self.service = service
        self.serial_number = serial_number
        self.firmware_version = firmware_version

        # Private fields
        self._sock = None



    def discover(self):
        # TODO
        pass



    def connect(self, api_token, timeout=1):
        # Return if socket is already connected
        if self._sock is not None:
            return {
                "status": "OKAY"
            }

        sock = None
        try:
            # Create TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((self.ipv4_addr, self.port))

            # Authenticate
            sock.sendall(f"auth {api_token}".encode())
            response = json.loads(sock.recv(1024).decode())

            # Check if authentication was successful
            if response.get("status") == "OKAY":
                self._sock = sock
            else:
                sock.close()
            
            # Successful or not, return the response
            return response

        except (socket.timeout, ConnectionRefusedError, OSError):
            self._sock = None
            if sock is not None:
                sock.close()

            # Return an error
            return {
                "status": "ERROR",
                "error-message": "the device cannot be reached"
            }



    def disconnect(self):
        # Return if socket is already disconnected
        if self._sock is None:
            return {
                "status": "OKAY"
            }

        # Void self._sock immediately
        sock = self._sock
        self._sock = None

        try:
            sock.close()
            return {
                "status": "OKAY"
            }

        except OSError:
            return {
                "status": "ERROR",
                "error-message": "failed to close socket"
            }



    def send(self, command):
        # Return if socket is disconnected
        if self._sock is None:
            return {
                "status": "ERROR",
                "error-message": "socket closed"
            }
        
        # Send the command and return the response
        self._sock.sendall(command.encode())
        return json.loads(self._sock.recv(1024).decode())
