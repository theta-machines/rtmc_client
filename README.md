# RTMC Client Library
The RTMC Client library (`rtmc-client`) is a client-side Python library for managing RTMC Cards. Specifically, it handles:

* device discovery
* socket connections
* bare-bones device emulation



## Building from Source
When building from source, always work in a virtual environment. You can create one by running these commands
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

Building, testing, and deployment are all handled by the `make.py` script.

1. Initialize your workspace and install all dependencies by running
    ```
    python make.py init
    ```

2. To build the library, run
    ```
    python make.py build
    ```

3. To run the test suite, run
    ```
    python make.py test
    ```

4. If you have permission to deploy to PyPI, you can do so by running
    ```
    python make.py deploy
    ```