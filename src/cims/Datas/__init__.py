import json
import os
import time
import appdirs
import shutil

# Get the user-specific data directory
APP_NAME = "CIMS"
APP_AUTHOR = "MINIOpenSource"
USER_DATA_DIR = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)

# The path to the default data directory within the package
PACKAGE_DATA_DIR = os.path.join(os.path.dirname(__file__))


# Ensure the user data directory exists
os.makedirs(USER_DATA_DIR, exist_ok=True)


def get_user_data_path(relative_path):
    """Constructs the full path to a file in the user data directory."""
    return os.path.join(USER_DATA_DIR, relative_path)


def get_package_data_path(relative_path):
    """Constructs the full path to a file in the package data directory."""
    return os.path.join(PACKAGE_DATA_DIR, relative_path)


class Resource:
    def __init__(self, path, name=None):
        self.path: str = path
        self.name: str = name if name is not None else path
        self.user_path = get_user_data_path(self.path)
        self.package_path = get_package_data_path(self.path)

        # Ensure the user subdirectory exists
        os.makedirs(self.user_path, exist_ok=True)

        # Copy default data on first run if the user directory is empty
        if not os.listdir(self.user_path):
            for item in os.listdir(self.package_path):
                s = os.path.join(self.package_path, item)
                d = os.path.join(self.user_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks=False, ignore=None)
                else:
                    shutil.copy2(s, d)

        self.file_list: list[str] = [
            f[:-5]
            for f in os.listdir(self.user_path)
            if f.endswith(".json")
        ]

    def refresh(self) -> list[str]:
        self.file_list = [
            f[:-5]
            for f in os.listdir(self.user_path)
            if f.endswith(".json")
        ]
        return self.file_list

    def read(self, name: str) -> dict:
        self.refresh()
        if name not in self.file_list:
            raise FileNotFoundError(f"{self.name} '{name}' not found.")
        with open(os.path.join(self.user_path, f"{name}.json"), encoding="utf-8") as f:
            return json.load(f)

    def write(self, name: str, data: dict) -> None:
        self.refresh()
        if name not in self.file_list:
            raise FileNotFoundError(f"{self.name} {name} not found.")

        file_path = os.path.join(self.user_path, f"{name}.json")
        bak_path = file_path + ".bak"

        if os.path.exists(file_path):
            shutil.copy2(file_path, bak_path)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def delete(self, name: str) -> None:
        self.refresh()
        if name not in self.file_list:
            raise FileNotFoundError(f"{self.name} {name} not found.")
        os.remove(os.path.join(self.user_path, f"{name}.json"))
        self.refresh()

    def rename(self, name: str, new_name: str) -> None:
        self.refresh()
        if name not in self.file_list:
            raise FileNotFoundError(f"{self.name} {name} not found.")
        if new_name in self.file_list:
            raise FileExistsError(f"{self.name} {new_name} exists, please delete it first.")

        os.rename(
            os.path.join(self.user_path, f"{name}.json"),
            os.path.join(self.user_path, f"{new_name}.json"),
        )
        self.refresh()

    def new(self, name: str) -> None:
        self.refresh()
        if name in self.file_list:
            raise FileExistsError(f"{self.name} {name} exists, please delete it first.")
        with open(os.path.join(self.user_path, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump({}, f)
        self.refresh()

    def __repr__(self):
        self.refresh()
        return f"{self.name}[" + ", ".join(self.file_list) + "]"

    def __str__(self):
        self.refresh()
        return f"{self.name}[" + ", ".join(self.file_list) + "]"

    def __iter__(self):
        self.refresh()
        for item in self.file_list:
            yield item, os.path.join(self.user_path, f"{item}.json")

    def __getitem__(self, item):
        self.refresh()
        if item in self.file_list:
            return os.path.join(self.user_path, f"{item}.json")
        raise IndexError(f"{self.name} '{item}' not found.")


ClassPlan = Resource("ClassPlan", "ClassPlan")
DefaultSettings = Resource("DefaultSettings", "DefaultSettings")
Policy = Resource("Policy", "Policy")
Subjects = Resource("Subjects", "Subjects")
TimeLayout = Resource("TimeLayout", "TimeLayout")


class _ClientStatus:
    def __init__(self):
        self.file_path = get_user_data_path("client_status.json")
        self._ensure_file_exists()
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.client_status: dict[str, dict[str, bool | float]] = json.load(f)

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def refresh(self) -> dict[str, dict[str, bool | float]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.client_status = json.load(f)
        return self.client_status

    def update(self, uid):
        self.client_status[uid] = {"isOnline": True, "lastHeartbeat": time.time()}
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.client_status, f)

    def offline(self, uid):
        if uid in self.client_status:
            self.client_status[uid]["isOnline"] = False
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.client_status, f)


ClientStatus = _ClientStatus()


class _ProfileConfig:
    def __init__(self):
        self.profile_config_path = get_user_data_path("profile_config.json")
        self.pre_register_path = get_user_data_path("pre_register.json")
        self._ensure_files_exist()
        with open(self.profile_config_path, "r", encoding="utf-8") as f:
            self.profile_config: dict[str, dict[str, str]] = json.load(f)
        with open(self.pre_register_path, "r", encoding="utf-8") as f:
            self.pre_registers = json.load(f)

    def _ensure_files_exist(self):
        for path in [self.profile_config_path, self.pre_register_path]:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    def refresh(self) -> dict[str, dict[str, str]]:
        with open(self.profile_config_path, "r", encoding="utf-8") as f:
            self.profile_config = json.load(f)
        return self.profile_config

    def register(self, uid, id):
        try:
            self.profile_config[uid] = self.pre_registers.get(
                id,
                {
                    "ClassPlan": "default",
                    "Settings": "default",
                    "Subjects": "default",
                    "Policy": "default",
                    "TimeLayout": "default",
                },
            )
        except KeyError:
            self.profile_config[uid] = {
                "ClassPlan": "default",
                "Settings": "default",
                "Subjects": "default",
                "Policy": "default",
                "TimeLayout": "default",
            }
        with open(self.profile_config_path, "w", encoding="utf-8") as f:
            json.dump(self.profile_config, f)
        self.refresh()

    def pre_register(self, id, conf=None):
        if conf is None:
            conf = {
                "ClassPlan": "default",
                "Settings": "default",
                "Subjects": "default",
                "Policy": "default",
                "TimeLayout": "default",
            }
        self.pre_registers[id] = conf
        with open(self.pre_register_path, "w", encoding="utf-8") as f:
            json.dump(self.pre_registers, f)
        self.refresh()


ProfileConfig = _ProfileConfig()


class _Clients:
    def __init__(self):
        self.clients_path = get_user_data_path("clients.json")
        self._ensure_file_exists()
        with open(self.clients_path, "r", encoding="utf-8") as f:
            self.clients: dict[str, str] = json.load(f)

    def _ensure_file_exists(self):
        if not os.path.exists(self.clients_path):
            with open(self.clients_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def refresh(self) -> dict[str, str]:
        with open(self.clients_path, "r", encoding="utf-8") as f:
            self.clients = json.load(f)
        return self.clients

    def register(self, uid, id):
        self.clients[uid] = id
        with open(self.clients_path, "w", encoding="utf-8") as f:
            json.dump(self.clients, f)
        ProfileConfig.register(uid, id)
        self.refresh


Clients = _Clients()
