import pytest
import rtmc_client as rtmc

# Test that you can connect to an RTMC Card
def test_connect():
    api_token = "dummy_token"

    # Create emulator
    emulator = rtmc.EmulationServer(api_token)
    emulator.start()
    
    rtmc_card = rtmc.Device("127.0.0.1", 65001)
    response = rtmc_card.connect(api_token)
    assert response.get("status") == "OKAY"

    emulator.stop()



# Test that you can disconnect from an RTMC Card
def test_disconnect():
    api_token = "dummy_token"

    # Create emulator
    emulator = rtmc.EmulationServer(api_token)
    emulator.start()
    
    # Connect
    rtmc_card = rtmc.Device("127.0.0.1", 65001)
    response = rtmc_card.connect(api_token)
    assert response.get("status") == "OKAY"

    # Disconnect
    response = rtmc_card.disconnect()
    assert response.get("status") == "OKAY"

    emulator.stop()



# Test that you can send commands to an RTMC Card
def test_command():
    api_token = "dummy_token"

    # Create emulator
    emulator = rtmc.EmulationServer(api_token)
    emulator.start()
    
    # Connect
    # breakpoint()
    rtmc_card = rtmc.Device("127.0.0.1", 65001)
    response = rtmc_card.connect(api_token)
    assert response.get("status") == "OKAY"

    # Send a command
    response = rtmc_card.send(f"auth {api_token}")
    assert response.get("status") == "OKAY"

    # Disconnect
    response = rtmc_card.disconnect()
    assert response.get("status") == "OKAY"

    emulator.stop()