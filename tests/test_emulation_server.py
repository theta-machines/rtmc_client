import json
import pytest
import rtmc_client as rtmc
import socket

@pytest.fixture
def tcp_socket(emulator):
    # Create TCP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((emulator.ipv4_addr, emulator.tcp_port))

    try:
        yield sock
    finally:
        sock.close()    



@pytest.fixture
def udp_socket(emulator):
    # Create UDP client
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.1)

    try:
        yield sock
    finally:
        sock.close()



# Test the behavior of a proper authentication
def test_auth_success(emulator, tcp_socket):
    tcp_socket.sendall(f"auth {emulator.api_token}".encode())
    response = json.loads(tcp_socket.recv(1024).decode())

    assert response.get("status") == "OKAY"



# Test the behavior of an incorrect token
def test_auth_wrong_token(emulator, tcp_socket):
    tcp_socket.sendall("auth wrong_token".encode())
    response = json.loads(tcp_socket.recv(1024).decode())

    assert response.get("status") == "ERROR"



# Test the behavior of sending something other than `auth <token>`
def test_auth_malformed(emulator, tcp_socket):
    tcp_socket.sendall("xyz".encode()) # Send "xyz" instead of "auth <token>"
    response = json.loads(tcp_socket.recv(1024).decode())

    assert response.get("status") == "ERROR"



# Test to ensure that the connection is closed if auth is failed
def test_auth_closes_connection(emulator, tcp_socket):
    # Send wrong token
    tcp_socket.sendall("auth wrong_token".encode())
    response = json.loads(tcp_socket.recv(1024).decode())
    assert response.get("status") == "ERROR"

    # Ensure the socket is closed
    socket_closed = False
    try:
        # Try sending the correct token
        tcp_socket.sendall("auth correct_token".encode())
        response = json.loads(tcp_socket.recv(1024).decode())
    except Exception:
        socket_closed = True
    
    assert socket_closed



# Test running the auth command after authenticating
def test_auth_twice(emulator, tcp_socket):
    for _ in range(2):
        # Send data and assert what the response should be
        tcp_socket.sendall(f"auth {emulator.api_token}".encode())
        response = json.loads(tcp_socket.recv(1024).decode())
        assert response.get("status") == "OKAY"



# Test the discover command over the TCP socket
def test_discover_tcp(emulator, tcp_socket):
    # Authenticate
    tcp_socket.sendall(f"auth {emulator.api_token}".encode())
    response = json.loads(tcp_socket.recv(1024).decode())
    assert response.get("status") == "OKAY"

    # Send the discover query
    tcp_socket.sendall("discover rtmc*".encode())
    response = json.loads(tcp_socket.recv(1024).decode())

    # Verify the response data
    assert response.get("service") == emulator.service
    assert response.get("port") == emulator.tcp_port
    assert response.get("device") == emulator.device
    assert response.get("serial_number") == emulator.serial_number
    assert response.get("firmware_version") == emulator.firmware_version



# Test the discover command over the TCP socket
def test_discover_tcp_bad_query(emulator, tcp_socket):
    # Authenticate
    tcp_socket.sendall(f"auth {emulator.api_token}".encode())
    response = json.loads(tcp_socket.recv(1024).decode())
    assert response.get("status") == "OKAY"

    # Send the discover query
    tcp_socket.sendall("discover bad_query".encode())
    response = tcp_socket.recv(1024).decode()

    # Verify the response data
    assert response == "{}"



# Test the discover command via UDP multicast
def test_discover_udp(emulator, udp_socket):
    udp_socket.sendto(b"discover rtmc*", (emulator.udp_multicast_group, emulator.udp_port))

    response, server = udp_socket.recvfrom(1024)
    json_data = json.loads(response.decode())

    # Verify the response data
    assert json_data.get("service") == emulator.service
    assert json_data.get("port") == emulator.tcp_port
    assert json_data.get("device") == emulator.device
    assert json_data.get("serial_number") == emulator.serial_number
    assert json_data.get("firmware_version") == emulator.firmware_version



# Test the discover command via UDP multicast
def test_discover_udp_bad_query(emulator, udp_socket):
    udp_socket.sendto(b"bad query", (emulator.udp_multicast_group, emulator.udp_port))

    # Make sure there's no response (check for timeout)
    socket_timeout = False
    try:
        response, server = udp_socket.recvfrom(1024)
    except socket.timeout:
        socket_timeout = True
    
    assert socket_timeout
