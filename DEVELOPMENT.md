# Development Setup

This document describes how to set up your development environment for CIMS.

## Prerequisites

*   Python 3.8 or higher
*   pip

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MINIOpenSource/CIMS-backend.git
    cd CIMS-backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -e ".[dev]"
    ```

4.  **Compile Protobuf files:**

    ```bash
    python -m grpc_tools.protoc --proto_path=src/cims/Protobuf --python_out=src/cims --grpc_python_out=src/cims $(find src/cims/Protobuf -name "*.proto")
    ```

5.  **Run the application:**

    ```bash
    cims
    ```
