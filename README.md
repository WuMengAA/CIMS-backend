# CIMS Backend (Go)

This is the Go implementation of the ClassIsland Management Server (CIMS).

## Features

- **Management API**: Manage ClassPlans, TimeLayouts, Subjects, Policies, etc.
- **Client API**: Serve configuration to ClassIsland clients.
- **gRPC Service**: Real-time communication (Register, Commands, Heartbeat).
- **Service Management**: Run as a system service (Windows Service, Systemd, Launchd).
- **Single Binary**: Easy deployment with SQLite embedded.

## Installation

### From Source

1. Install Go 1.22+.
2. Install `protoc` (Protocol Buffers compiler).
3. Clone the repo.
4. Run:
   ```bash
   make proto
   go mod tidy
   make build
   ```

### Running

#### Interactive Mode

```bash
./cims_server start
```
By default, it listens on HTTP :50050 and gRPC :50051.

#### Service Mode

Install as a system service to start automatically on boot:

```bash
# Install the service
sudo ./cims_server service install

# Start the service
sudo ./cims_server service run

# Stop the service
sudo ./cims_server service stop

# Uninstall the service
sudo ./cims_server service uninstall
```

**Note:** On Windows, run cmd/powershell as Administrator.

## Configuration

- Database: Defaults to `cims.db` in the current directory (or service directory). Use `--db <path>` to override.
- Ports: Use `--port` (HTTP) and `--grpc-port` (gRPC).

## Development

- `make proto`: Generate Go code from `.proto` files.
- `make build`: Build the binary.
- `internal/model/domain.go`: Domain models matching ClassIsland JSON structure.
