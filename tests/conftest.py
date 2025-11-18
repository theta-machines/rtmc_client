import pytest
import rtmc_client as rtmc

@pytest.fixture
def emulator():
    api_token = "dummy_token"

    # Start the emulator
    emulator = rtmc.EmulationServer(api_token)
    emulator.start()

    try:
        yield emulator
    finally:
        emulator.stop()
