# rtmc_client
This repository houses the source files for the `rtmc_client` Python library, a client-side library for managing RTMC Cards. Specifically, it handles:
* Device discovery
* Socket creation and authentication
* Updating the RTMC Card's firmware (future)
* Flashing user applications (future)

## Getting Started
Install the library with
```
pip install rtmc_client
```

A simple program looks like this:
```python
import rtmc_client as rtmc

# Discover all RTMC Cards on the network
devices = rtmc.discover()

# Select the first device
rtmc_card = devices[0]

# Connect, send some data, then disconnect
rtmc_card.connect("default_token")
rtmc_card.send("move x y z")
rtmc_card.disconnect()
```



## Building from Source
1. Always work in a virtual environment. You can create one by running these commands
    * **Linux/macOS (Bash/Zsh)**
        ```
        python -m venv .venv
        source .venv/bin/activate
        ```

    * **Windows (PowerShell)**
        ```
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        ```

    * **Other** - Refer to the [venv documentation](https://docs.python.org/3/library/venv.html).

<br/>

2. Make sure you have the latest version of `build` installed
    ```
    python -m pip install --upgrade build
    ```

<br/>

3. To build, run this command from the same directory as the `pyproject.toml` file.
    ```
    python -m build
    ```
