#!/usr/bin/env python3
"""Plan, package, and verify the Entra ID group topology for the GRC service.

Three subcommands:

  plan     derive every group and app role name from the app list, role
           catalog, and environments. prints the counts that justify all
           this automation.

  package  emit a change request bundle the directory team can review and
           apply with their own tooling: summary.md, groups.csv,
           approles.json. we do not ask for write access to their
           directory, on purpose. see docs/04-entra-sync-design.md.

  drift    compare the expected topology against a directory export
           (csv of group names) and report missing / unexpected /
           misnamed. run it on a schedule and the output doubles as
           continuous monitoring evidence for AC-2 and CA-7.

Usage:
  python scripts/entra_provisioner.py plan --apps 50 --envs dev test prod
  python scripts/entra_provisioner.py package --out cr-bundle
  python scripts/entra_provisioner.py drift [--export sample-data/entra-export.csv]
"""

import argparse
import csv
import json
import os
import sys
from datetime import date

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grc_client import MockClient

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "..", "templates", "permission-templates.yaml")
PREFIX = "GRC"


def role_catalog():
    with open(TEMPLATES) as f:
        return list(yaml.safe_load(f)["roles"].keys())


def norm(name):
    return name.upper().replace(" ", "-").replace("_", "-")


def derive_names(apps, roles, envs):
    """The single source of truth for names. Nobody types these."""
    out = []
    for env in envs:
        for app in apps:
            for role in roles:
                out.append({
                    "group": f"{PREFIX}-{norm(env)}-{norm(app)}-{norm(role)}",
                    "env": env, "app": app, "role": role,
                })
    return out


def tenant_apps():
    return MockClient().list_applications()


def cmd_plan(args):
    roles = role_catalog()
    if args.apps:
        apps = [f"APP-{i:02d}" for i in range(1, args.apps + 1)]
        source = f"hypothetical {args.apps} applications"
    else:
        apps = tenant_apps()
        source = "applications discovered in tenant"

    names = derive_names(apps, roles, args.envs)
    per_env = len(apps) * len(roles)

    print(f"source        : {source}")
    print(f"role catalog  : {', '.join(roles)}  ({len(roles)} roles)")
    print(f"environments  : {', '.join(args.envs)}")
    print(f"groups per env: {per_env}")
    print(f"entra groups  : {len(names)}")
    print(f"entra approles: {len(names)}  (one claim mapping per group)")
    print(f"total objects : {len(names) * 2}  managed in the directory")
    print(f"plus the same {len(names)} groups again inside the platform.")
    print()
    print("sample of derived names:")
    for n in names[:5]:
        print(f"  {n['group']}")
    print(f"  ... and {len(names) - 5} more, none of them typed by a human.")


def cmd_package(args):
    roles = role_catalog()
    apps = tenant_apps()
    names = derive_names(apps, roles, args.envs)
    os.makedirs(args.out, exist_ok=True)

    with open(os.path.join(args.out, "groups.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["group", "env", "app", "role"])
        w.writeheader()
        w.writerows(names)

    approles = [{
        "displayName": n["group"],
        "value": n["group"],
        "description": f"GRC {n['role']} for {n['app']} ({n['env']})",
        "allowedMemberTypes": ["User"],
        "isEnabled": True,
    } for n in names]
    with open(os.path.join(args.out, "approles.json"), "w") as f:
        json.dump(approles, f, indent=2)

    with open(os.path.join(args.out, "summary.md"), "w") as f:
        f.write(f"""# Change request: GRC service group provisioning

Date: {date.today().isoformat()}
Requested by: GRC implementation team
Applies to: Entra ID, {', '.join(args.envs)}

## What we are asking for

Create {len(names)} security groups and {len(names)} matching app roles for
SSO claim mapping, named exactly as listed in groups.csv and approles.json.
Names follow the convention {PREFIX}-ENV-APP-ROLE and were generated, not
typed. No permissions inside Entra beyond group existence and app role
assignment are requested.

## Why

One group per role per application per environment for the departmental
GRC platform. The naming convention makes each group's purpose readable at
a glance and keeps claim mapping deterministic.

## What we are NOT asking for

Write access to the directory for our team or any service principal.
You apply this with your tooling, we verify with a read only drift check.
""")
    print(f"change request bundle written to {args.out}/")
    print(f"  groups.csv    {len(names)} rows")
    print(f"  approles.json {len(approles)} definitions")
    print(f"  summary.md    the part a human reads first")


def cmd_drift(args):
    roles = role_catalog()
    apps = tenant_apps()
    expected = {n["group"] for n in derive_names(apps, roles, args.envs)}

    with open(args.export, newline="") as f:
        actual = {row["group"].strip() for row in csv.DictReader(f) if row.get("group")}

    missing = sorted(expected - actual)
    unexpected = sorted(g for g in actual - expected if g.startswith(PREFIX + "-"))

    print(f"expected groups : {len(expected)}")
    print(f"directory export: {len(actual)} rows ({args.export})")
    print(f"missing         : {len(missing)}")
    for g in missing[:10]:
        print(f"  - {g}")
    if len(missing) > 10:
        print(f"  ... {len(missing) - 10} more")
    print(f"unexpected (our prefix, not in plan): {len(unexpected)}")
    for g in unexpected[:10]:
        print(f"  + {g}")
    status = "CLEAN" if not missing and not unexpected else "DRIFT DETECTED"
    print(f"\nstatus: {status}")
    return 0 if status == "CLEAN" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="derive names and show the scale math")
    p.add_argument("--apps", type=int, default=0,
                   help="model N hypothetical apps instead of the tenant's")
    p.add_argument("--envs", nargs="+", default=["dev", "test", "prod"])

    p = sub.add_parser("package", help="emit the change request bundle")
    p.add_argument("--out", default="cr-bundle")
    p.add_argument("--envs", nargs="+", default=["dev", "test", "prod"])

    p = sub.add_parser("drift", help="compare plan against a directory export")
    p.add_argument("--export", default=os.path.join(
        HERE, "..", "sample-data", "entra-export.csv"))
    p.add_argument("--envs", nargs="+", default=["dev", "test", "prod"])

    args = ap.parse_args()
    return {"plan": cmd_plan, "package": cmd_package, "drift": cmd_drift}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
