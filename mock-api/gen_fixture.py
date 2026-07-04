"""Regenerates tenant.json, the offline stand in for the platform API.

Mirrors the real quirk faithfully: 28 modules per group, and every module's
id is unique PER GROUP (uuid5 of app/group/module), so nothing can be
hardcoded and the templater has to do the pull, merge, push cycle honestly.
Fresh groups start as read only across the board, like a newly created
group would.
"""

import json
import os
import uuid

MODULES = [
    "systems", "controls", "assessments", "artifacts", "poams", "ssp",
    "risks", "issues", "incidents", "policies", "procedures", "supply_chain",
    "assets", "data_calls", "questionnaires", "workflows", "reports",
    "dashboards", "catalogs", "profiles", "components", "interconnects",
    "exceptions", "evidence_requests", "milestones", "audit_log",
    "user_prefs", "admin_settings",
]
assert len(MODULES) == 28

APPS = [
    ("HQ-OCIO", ["ADMIN", "EXEC-RO", "USER", "ISSO"]),
    ("Site-Alpha", ["ADMIN", "EXEC-RO", "USER", "ISSO", "ASSESSOR"]),
    ("Site-Bravo", ["ADMIN", "EXEC-RO", "USER"]),
]

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def module_block(app, group):
    return [
        {
            "module_id": str(uuid.uuid5(NS, f"{app}/{group}/{m}")),
            "module": m,
            "create": False, "read": True, "update": False, "delete": False,
        }
        for m in MODULES
    ]


def main():
    tenant = {
        "tenant": "department-egrc-demo",
        "environments": ["dev", "test", "prod"],
        "applications": [
            {
                "name": app,
                "groups": [
                    {"name": g, "modules": module_block(app, g)} for g in groups
                ],
            }
            for app, groups in APPS
        ],
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tenant.json")
    with open(out, "w") as f:
        json.dump(tenant, f, indent=2)
    n_groups = sum(len(g) for _, g in APPS)
    print(f"wrote tenant.json: {len(APPS)} applications, {n_groups} groups, "
          f"{n_groups * len(MODULES)} module permission entries")


if __name__ == "__main__":
    main()
