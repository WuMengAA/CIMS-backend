import json
from app.apps.client_app import client_app
from app.apps.admin_app import admin_app

with open("client_openapi.json", "w", encoding="utf-8") as f:
    json.dump(client_app.openapi(), f, ensure_ascii=False, indent=2)

with open("admin_openapi.json", "w", encoding="utf-8") as f:
    json.dump(admin_app.openapi(), f, ensure_ascii=False, indent=2)

print("OpenAPI schemas exported successfully to client_openapi.json and admin_openapi.json")
