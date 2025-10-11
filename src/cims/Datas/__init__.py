import time
import appdirs
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from cims.database.models import Base, Tenant, Resource as DbResource, Client as DbClient, ClientStatus as DbClientStatus, ProfileConfig as DbProfileConfig, PreRegister as DbPreRegister

# Get the user-specific data directory
APP_NAME = "CIMS"
APP_AUTHOR = "MINIOpenSource"
USER_DATA_DIR = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
DATABASE_FILE = os.path.join(USER_DATA_DIR, "cims.db")

# Set up the database
engine = create_engine(f"sqlite:///{DATABASE_FILE}")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

def get_session() -> Session:
    return DBSession()

class Resource:
    def __init__(self, resource_type: str, name: str = None):
        self.resource_type = resource_type
        self.name = name if name is not None else resource_type

    def read(self, name: str, tenant_id: int = 1) -> dict:
        session = get_session()
        resource = session.query(DbResource).filter_by(tenant_id=tenant_id, resource_type=self.resource_type, name=name).first()
        session.close()
        if not resource:
            raise FileNotFoundError(f"{self.name} '{name}' not found.")
        return resource.data

    def write(self, name: str, data: dict, tenant_id: int = 1) -> None:
        session = get_session()
        resource = session.query(DbResource).filter_by(tenant_id=tenant_id, resource_type=self.resource_type, name=name).first()
        if not resource:
            session.close()
            raise FileNotFoundError(f"{self.name} '{name}' not found.")
        resource.data = data
        session.commit()
        session.close()

    def delete(self, name: str, tenant_id: int = 1) -> None:
        session = get_session()
        resource = session.query(DbResource).filter_by(tenant_id=tenant_id, resource_type=self.resource_type, name=name).first()
        if not resource:
            session.close()
            raise FileNotFoundError(f"{self.name} '{name}' not found.")
        session.delete(resource)
        session.commit()
        session.close()

    def new(self, name: str, data: dict = None, tenant_id: int = 1) -> None:
        if data is None:
            data = {}
        session = get_session()
        existing = session.query(DbResource).filter_by(tenant_id=tenant_id, resource_type=self.resource_type, name=name).first()
        if existing:
            session.close()
            raise FileExistsError(f"{self.name} '{name}' exists, please delete it first.")

        new_resource = DbResource(
            tenant_id=tenant_id,
            resource_type=self.resource_type,
            name=name,
            data=data
        )
        session.add(new_resource)
        session.commit()
        session.close()


ClassPlan = Resource("ClassPlan")
DefaultSettings = Resource("DefaultSettings")
Policy = Resource("Policy")
Subjects = Resource("Subjects")
TimeLayout = Resource("TimeLayout")


class _ClientStatus:
    def refresh(self, tenant_id: int = 1) -> dict:
        session = get_session()
        statuses = session.query(DbClientStatus).filter_by(tenant_id=tenant_id).all()
        session.close()
        return {status.uid: {"isOnline": status.is_online, "lastHeartbeat": status.last_heartbeat} for status in statuses}

    def update(self, uid: str, tenant_id: int = 1):
        session = get_session()
        status = session.query(DbClientStatus).filter_by(tenant_id=tenant_id, uid=uid).first()
        if status:
            status.is_online = True
            status.last_heartbeat = time.time()
        else:
            status = DbClientStatus(
                tenant_id=tenant_id,
                uid=uid,
                is_online=True,
                last_heartbeat=time.time()
            )
            session.add(status)
        session.commit()
        session.close()

    def offline(self, uid: str, tenant_id: int = 1):
        session = get_session()
        status = session.query(DbClientStatus).filter_by(tenant_id=tenant_id, uid=uid).first()
        if status:
            status.is_online = False
            session.commit()
        session.close()

ClientStatus = _ClientStatus()


class _ProfileConfig:
    def refresh(self, tenant_id: int = 1) -> dict:
        session = get_session()
        configs = session.query(DbProfileConfig).filter_by(tenant_id=tenant_id).all()
        session.close()
        return {config.uid: config.config for config in configs}

    def register(self, uid: str, client_id: str, tenant_id: int = 1):
        session = get_session()
        pre_register = session.query(DbPreRegister).filter_by(tenant_id=tenant_id, client_id=client_id).first()

        default_config = {
            "ClassPlan": "default",
            "Settings": "default",
            "Subjects": "default",
            "Policy": "default",
            "TimeLayout": "default",
        }

        config_data = pre_register.config if pre_register else default_config

        profile_config = session.query(DbProfileConfig).filter_by(tenant_id=tenant_id, uid=uid).first()
        if profile_config:
            profile_config.config = config_data
        else:
            profile_config = DbProfileConfig(
                tenant_id=tenant_id,
                uid=uid,
                config=config_data
            )
            session.add(profile_config)
        session.commit()
        session.close()

    def get_profile_config(self, uid, tenant_id=1):
        session = get_session()
        profile = session.query(DbProfileConfig).filter_by(tenant_id=tenant_id, uid=uid).first()
        session.close()
        if not profile:
            return {
                "ClassPlan": "default",
                "TimeLayout": "default",
                "Subjects": "default",
                "Settings": "default",
                "Policy": "default",
            }
        return profile.config

    def pre_register(self, client_id: str, conf=None, tenant_id: int = 1):
        if conf is None:
            conf = {
                "ClassPlan": "default",
                "Settings": "default",
                "Subjects": "default",
                "Policy": "default",
                "TimeLayout": "default",
            }
        session = get_session()
        pre_register = session.query(DbPreRegister).filter_by(tenant_id=tenant_id, client_id=client_id).first()
        if pre_register:
            pre_register.config = conf
        else:
            pre_register = DbPreRegister(
                tenant_id=tenant_id,
                client_id=client_id,
                config=conf
            )
            session.add(pre_register)
        session.commit()
        session.close()

ProfileConfig = _ProfileConfig()


class _Clients:
    def refresh(self, tenant_id: int = 1) -> dict:
        session = get_session()
        clients = session.query(DbClient).filter_by(tenant_id=tenant_id).all()
        session.close()
        return {client.uid: client.client_id for client in clients}

    def register(self, uid: str, client_id: str, tenant_id: int = 1):
        session = get_session()
        client = session.query(DbClient).filter_by(tenant_id=tenant_id, uid=uid).first()
        if client:
            client.client_id = client_id
        else:
            client = DbClient(
                tenant_id=tenant_id,
                uid=uid,
                client_id=client_id
            )
            session.add(client)
        session.commit()
        ProfileConfig.register(uid, client_id, tenant_id)
        session.close()

Clients = _Clients()
