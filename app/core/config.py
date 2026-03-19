"""Global application configuration via environment variables.

Defines database endpoints, redis connection details, and
multi-tenancy security parameters used throughout the project.
"""

import os

# Database connectivity (PostgreSQL)
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgresql:password@localhost:5432/cims",
)

# Shared cache connectivity (Redis)
REDIS_URL: str = os.environ.get("REDIS_URL", "redis://:password@localhost:6379/0")

# Multi-tenancy hosting configuration
BASE_DOMAIN: str = os.environ.get("CIMS_BASE_DOMAIN", "localhost")

# Port assignments for partitioned services
CLIENT_PORT: int = int(os.environ.get("CIMS_CLIENT_PORT", "50050"))
ADMIN_PORT: int = int(os.environ.get("CIMS_ADMIN_PORT", "50051"))
GRPC_PORT: int = int(os.environ.get("CIMS_GRPC_PORT", "50052"))

# Root management security secret
ADMIN_SECRET: str = os.environ.get("CIMS_ADMIN_SECRET", "change-me")
