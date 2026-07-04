"""A tiny client for the GRC platform API.

Two implementations behind one interface:

  MockClient  - reads and writes json fixtures in mock-api/, so the whole
                repo runs offline. This is what the demos use.
  LiveClient  - the same calls shaped for a real tenant. Deliberately left
                as a thin stub: base url, token auth, and the three calls
                the templater needs. Point it at a sandbox tenant and the
                templater works unchanged.

The important design decision is that module IDs are DISCOVERED, never
hardcoded. Every group carries its own unique per module IDs, which is
exactly the quirk that makes manual administration of this platform so
error prone at scale.
"""

import json
import os
import copy

MOCK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mock-api")


class MockClient:
    """Reads/writes the fixture file so demo runs are stateful."""

    def __init__(self, fixture=None):
        self.path = fixture or os.path.join(MOCK_DIR, "tenant.json")
        with open(self.path) as f:
            self.state = json.load(f)

    # -- reads -----------------------------------------------------------
    def list_applications(self):
        return [a["name"] for a in self.state["applications"]]

    def get_application(self, app_name):
        for a in self.state["applications"]:
            if a["name"].lower() == app_name.lower():
                return copy.deepcopy(a)
        raise LookupError(f"no application named {app_name!r} in tenant")

    def get_group(self, app_name, group_name):
        app = self.get_application(app_name)
        for g in app["groups"]:
            if g["name"].lower() == group_name.lower():
                return copy.deepcopy(g)
        raise LookupError(f"no group {group_name!r} in application {app_name!r}")

    # -- writes ----------------------------------------------------------
    def put_group_permissions(self, app_name, group_name, module_permissions):
        """module_permissions: list of {module_id, module, create, read,
        update, delete} dicts, one per module, IDs must match the group's."""
        for a in self.state["applications"]:
            if a["name"].lower() != app_name.lower():
                continue
            for g in a["groups"]:
                if g["name"].lower() != group_name.lower():
                    continue
                known = {m["module_id"] for m in g["modules"]}
                incoming = {m["module_id"] for m in module_permissions}
                if known != incoming:
                    raise ValueError(
                        "module id mismatch, refusing to write. "
                        f"unknown ids: {sorted(incoming - known)}")
                g["modules"] = module_permissions
                self._save()
                return True
        raise LookupError(f"{app_name}/{group_name} not found")

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)


class LiveClient:
    """Shape of the real thing. Fill in base_url and token, nothing else
    changes for the callers."""

    def __init__(self, base_url=None, token=None):
        self.base_url = base_url or os.environ.get("GRC_BASE_URL")
        self.token = token or os.environ.get("GRC_API_TOKEN")
        if not (self.base_url and self.token):
            raise RuntimeError(
                "LiveClient needs GRC_BASE_URL and GRC_API_TOKEN. "
                "For the offline demo use MockClient instead.")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}",
                "Accept": "application/json"}

    def get_group(self, app_name, group_name):
        raise NotImplementedError(
            "GET /api/applications/{app}/groups/{group} - wire to sandbox")

    def put_group_permissions(self, app_name, group_name, module_permissions):
        raise NotImplementedError(
            "PUT /api/applications/{app}/groups/{group}/permissions")
