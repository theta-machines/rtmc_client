import pytest
import rtmc_client as rtmc

@pytest.fixture
def device(emulator):
    # Connect to emulator
    device = rtmc.Device(emulator.ipv4_addr, emulator.tcp_port)
    response = device.connect(emulator.api_token)
    assert response.get("status") == "OKAY"

    try:
        yield device

    finally:
        # Disconnect from emulator
        response = device.disconnect()
        assert response.get("status") == "OKAY"



# Test that you can send commands to an RTMC Card
def test_send(emulator, device):
    response = device.send(f"auth {emulator.api_token}")
    assert response.get("status") == "OKAY"
