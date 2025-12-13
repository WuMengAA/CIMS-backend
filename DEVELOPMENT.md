# Development Setup

This document describes how to set up your development environment for CIMS (Go Backend).

## Prerequisites

*   Go 1.22 or higher
*   `protoc` (Protocol Buffers Compiler)
*   `make` (optional, for convenience)

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MINIOpenSource/CIMS-backend.git
    cd CIMS-backend
    ```

2.  **Install Go Tools:**

    ```bash
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
    ```
    Ensure your `$GOPATH/bin` is in your `$PATH`.

3.  **Download Dependencies:**

    ```bash
    go mod tidy
    ```

4.  **Generate Protobuf Files:**

    If you modify the `.proto` definitions in `api/Protobuf/`, you need to regenerate the Go code:

    ```bash
    make proto
    ```

5.  **Build and Run:**

    ```bash
    make build
    ./cims_server start
    ```

    Or run directly:

    ```bash
    go run cmd/cims/main.go start
    ```

## Database

The application uses SQLite (`cims.db`). It will be created automatically in the working directory on first run.

## IDE Support

We recommend using **VSCode** (with Go extension) or **GoLand**.
