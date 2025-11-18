import json
import pytest
import rtmc_client as rtmc
import socket

# Test the behavior of a proper authentication
def test_auth_success():
    api_token = "dummy_token"

    emulator = rtmc.EmulationServer(api_token)
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Send data and assert what the response should be
    sock.sendall(f"auth {api_token}".encode())
    response = json.loads(sock.recv(1024).decode())
    assert response.get("status") == "OKAY"

    emulator.stop()



# Test the behavior of an incorrect token
def test_auth_wrong_token():
    emulator = rtmc.EmulationServer("correct_token")
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Send data and assert what the response should be
    sock.sendall("auth wrong_token".encode())
    response = json.loads(sock.recv(1024).decode())
    assert response.get("status") == "ERROR"

    emulator.stop()



# Test the behavior of sending something other than `auth <token>`
def test_auth_malformed():
    emulator = rtmc.EmulationServer("correct_token")
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Send data and assert what the response should be
    sock.sendall("xyz".encode()) # Send "xyz" instead of "auth <token>"
    response = json.loads(sock.recv(1024).decode())
    assert response.get("status") == "ERROR"

    emulator.stop()



# Test to ensure that the connection is closed if auth is failed
def test_auth_closes_connection():
    emulator = rtmc.EmulationServer("correct_token")
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Send wrong token
    sock.sendall("auth wrong_token".encode())
    response = json.loads(sock.recv(1024).decode())
    assert response.get("status") == "ERROR"

    # Make sure the socket is closed
    socket_closed = False
    try:
        # Try sending the correct token
        sock.sendall("auth correct_token".encode())
        response = json.loads(sock.recv(1024).decode())
    except Exception:
        socket_closed = True
    
    assert socket_closed

    emulator.stop()



# Test running the auth command after authenticating
def test_auth_twice():
    api_token = "dummy_token"

    emulator = rtmc.EmulationServer(api_token)
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Send the auth command twice
    for _ in range(2):
        # Send data and assert what the response should be
        sock.sendall(f"auth {api_token}".encode())
        response = json.loads(sock.recv(1024).decode())
        assert response.get("status") == "OKAY"

    emulator.stop()



# Test the discover command over the TCP socket
def test_discover_tcp():
    api_token = "dummy_token"

    emulator = rtmc.EmulationServer(api_token)
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Authenticate
    sock.sendall(f"auth {api_token}".encode())
    response = json.loads(sock.recv(1024).decode())
    assert response.get("status") == "OKAY"

    # Send the discover query
    sock.sendall("discover rtmc*".encode())
    response = json.loads(sock.recv(1024).decode())

    # Verify the response data
    assert response.get("service") == "rtmc-tcp-1.0-emulator"
    assert response.get("port") == emulator.tcp_port
    assert response.get("device") == emulator.device
    assert response.get("serial_number") == emulator.serial_number
    assert response.get("firmware_version") == emulator.firmware_version

    emulator.stop()



# Test the discover command over the TCP socket
def test_discover_tcp_bad_query():
    api_token = "dummy_token"

    emulator = rtmc.EmulationServer(api_token)
    emulator.start()

    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    # Authenticate
    sock.sendall(f"auth {api_token}".encode())
    response = json.loads(sock.recv(1024).decode())
    assert response.get("status") == "OKAY"

    # Send the discover query
    sock.sendall("discover bad_query".encode())
    response = sock.recv(1024).decode()

    # Verify the response data
    assert response == "{}"

    emulator.stop()



# Test the discover command via UDP multicast
def test_discover_udp():
    emulator = rtmc.EmulationServer("dummy_token")
    emulator.start()

    # Create UDP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.1)
    sock.sendto(b"discover rtmc*", (emulator.udp_multicast_group, emulator.udp_port))

    # Parse response
    response, server = sock.recvfrom(1024)
    json_data = json.loads(response.decode())

    # Verify the response data
    assert json_data.get("service") == "rtmc-tcp-1.0-emulator"
    assert json_data.get("port") == emulator.tcp_port
    assert json_data.get("device") == emulator.device
    assert json_data.get("serial_number") == emulator.serial_number
    assert json_data.get("firmware_version") == emulator.firmware_version

    emulator.stop()



# Test the discover command via UDP multicast
def test_discover_udp_bad_query():
    emulator = rtmc.EmulationServer("dummy_token")
    emulator.start()

    # Create UDP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.1)
    sock.sendto(b"bad query", (emulator.udp_multicast_group, emulator.udp_port))

    # Parse response
    socket_timeout = False
    try:
        response, server = sock.recvfrom(1024)
    except socket.timeout:
        socket_timeout = True
    
    assert socket_timeout

    emulator.stop()
