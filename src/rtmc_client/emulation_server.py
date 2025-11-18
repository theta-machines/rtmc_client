"""
Original Author: Ryan Stracener

This is a bare-bones RTMC Card emulator. It's sole purpose is to facilitate
the testing of a program's connection logic. It has the following functions:
  * Responds to UDP discovery queries
  * Acts as a TCP server for receiving commands

The only commands supported are the `discover` and `auth` commands. All other
inputs will respond with the following JSON string:
    {
        "status": "ERROR",
        "error-message": "command not supported by emulator"
    }
"""

import fnmatch, json, socket, threading

class EmulationServer:
    def __init__(
        self,
        api_token,
        service="rtmc-tcp-1.0-emulator",
        port=65001,
        device="bare-bones-emulator",
        serial_number="1234ABCD",
        firmware_version="0.0.0"
    ):
        # Public fields
        self.api_token = api_token
        self.service = service
        self.port = port
        self.device = device
        self.serial_number = serial_number
        self.firmware_version = firmware_version
        self.ipv4_addr = "127.0.0.1"
        self.is_running = False # TODO: there's a difference in stop_flag and is_stopped, since stopping takes time in a background thread

        # Private fields
        self._tcp_daemon = None
        self._tcp_socket = None




    def start(self):
        # Return early if emulator is already running
        if self.is_running:
            return
        
        self.is_running = True

        # Create the TCP socket
        # (Do this here instead of in the daemon to ensure that the socket is
        # up BEFORE start() finishes!)
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._tcp_socket.bind((self.ipv4_addr, self.port))
        self._tcp_socket.listen()
        self._tcp_socket.settimeout(0.1) # timeout (and loop) after 100ms

        # Spawn TCP server daemon
        self._tcp_daemon = threading.Thread(target=self._tcp_server, daemon=True)
        self._tcp_daemon.start()



    # TODO: document that this function is blocking until the threads join
    def stop(self):
        # Return early if emulator is already stopped
        if not self.is_running:
            return

        # Set the stop flag
        self.is_running = False

        # Join the TCP daemon
        if self._tcp_daemon is not None:
            self._tcp_daemon.join()
            self._tcp_daemon = None



    def _tcp_server(self):
        conn = None
        while self.is_running:
            # Ensure accept() can only block for 100ms before looping
            self._tcp_socket.settimeout(0.1)

            # Accept a client
            client_authenticated = False
            try:
                conn, addr = self._tcp_socket.accept()

            except OSError: # Socket closed while waiting in accept()
                break

            # Handle connection
            with conn:
                # Ensure recv() can only block for 100ms before looping
                conn.settimeout(0.1)
                failed_authentication = False
                while self.is_running and not failed_authentication:
                    try:
                        data = conn.recv(1024)

                    except OSError: # Connection abruptly closed
                        break
                    
                    # Break if no data was sent
                    if not data:
                        break
                    
                    # Call the appropriate command
                    if not client_authenticated:
                        response = self._auth_command(data.decode())
                        conn.sendall(response.encode())

                        # Check if authentication succeeded
                        if json.loads(response).get("status") == "OKAY":
                            client_authenticated = True
                        else:
                            # Flag the failure to break out of the loop
                            # (this closes the connection)
                            failed_authentication = True
                    else:
                        response = self._command_invoke(data.decode())
                        conn.sendall(response.encode())



    def _command_invoke(self, command):
        # List of supported commands
        command_handlers = {
            "auth": self._auth_command,
            "discover": self._discover_command,
        }
        
        # Choose handler from first word of the command
        first_word = command.split(" ")[0]
        handler = command_handlers.get(first_word)

        # Call the handler or return an error
        if handler is not None:
            return handler(command)
        else:
            return '{"status":"ERROR","error-message":"command not supported by emulator"}'



    def _auth_command(self, command):
        token = command[5:]
        if(token == self.api_token):
            return '{"status":"OKAY"}'
        else:
            return '{"status":"ERROR","error-message":"authentication failed"}'



    def _discover_command(self, command):
        # Make sure first word is "discover"
        first_word = command.split(" ")[0]
        if first_word != "discover":
            return
        
        # Substring to get the pattern
        pattern = command[9:]

        # Match the pattern and return JSON string
        if fnmatch.fnmatch(self.service, pattern):
            return (
                '{'
                    f'"service":"{self.service}",'
                    f'"port":{self.port},'
                    f'"device":"{self.device}",'
                    f'"serial_number":"{self.serial_number}",'
                    f'"firmware_version":"{self.firmware_version}"'
                '}'
            )
        else:
            return '{}'
