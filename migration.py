import os
import json
import appdirs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cims.database.models import (
    Base,
    Tenant,
    Resource,
    Client,
    ClientStatus,
    ProfileConfig,
    PreRegister,
)

# Get the user-specific data directory
APP_NAME = "CIMS"
APP_AUTHOR = "MINIOpenSource"
USER_DATA_DIR = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
DATABASE_FILE = os.path.join(USER_DATA_DIR, "cims.db")


def get_user_data_path(relative_path):
    """Constructs the full path to a file in the user data directory."""
    return os.path.join(USER_DATA_DIR, relative_path)


def migrate():
    # Set up the database
    engine = create_engine(f"sqlite:///{DATABASE_FILE}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a default tenant
    default_tenant = Tenant(name="default")
    session.add(default_tenant)
    session.commit()

    # Migrate Resources
    resource_types = [
        "ClassPlan",
        "DefaultSettings",
        "Policy",
        "Subjects",
        "TimeLayout",
    ]
    for resource_type in resource_types:
        path = get_user_data_path(resource_type)
        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.endswith(".json"):
                    name = filename[:-5]
                    with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    resource = Resource(
                        tenant_id=default_tenant.id,
                        resource_type=resource_type,
                        name=name,
                        data=data,
                    )
                    session.add(resource)

    # Migrate Clients
    clients_path = get_user_data_path("clients.json")
    if os.path.exists(clients_path):
        with open(clients_path, "r", encoding="utf-8") as f:
            clients_data = json.load(f)
        for uid, client_id in clients_data.items():
            client = Client(tenant_id=default_tenant.id, uid=uid, client_id=client_id)
            session.add(client)

    # Migrate Client Status
    client_status_path = get_user_data_path("client_status.json")
    if os.path.exists(client_status_path):
        with open(client_status_path, "r", encoding="utf-8") as f:
            client_status_data = json.load(f)
        for uid, status in client_status_data.items():
            client_status = ClientStatus(
                tenant_id=default_tenant.id,
                uid=uid,
                is_online=status["isOnline"],
                last_heartbeat=status["lastHeartbeat"],
            )
            session.add(client_status)

    # Migrate Profile Config
    profile_config_path = get_user_data_path("profile_config.json")
    if os.path.exists(profile_config_path):
        with open(profile_config_path, "r", encoding="utf-8") as f:
            profile_config_data = json.load(f)
        for uid, config in profile_config_data.items():
            profile_config = ProfileConfig(
                tenant_id=default_tenant.id, uid=uid, config=config
            )
            session.add(profile_config)

    # Migrate Pre-Register
    pre_register_path = get_user_data_path("pre_register.json")
    if os.path.exists(pre_register_path):
        with open(pre_register_path, "r", encoding="utf-8") as f:
            pre_register_data = json.load(f)
        for client_id, config in pre_register_data.items():
            pre_register = PreRegister(
                tenant_id=default_tenant.id, client_id=client_id, config=config
            )
            session.add(pre_register)

    session.commit()
    session.close()
    print("Data migration completed successfully.")


if __name__ == "__main__":
    migrate()
