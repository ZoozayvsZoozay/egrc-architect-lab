#!/usr/bin/env python3
"""Apply a role permission template to a platform group.

The problem this solves: in this platform every group needs CRUD assigned
across ~28 modules, and every module carries a unique ID scoped to that
group. So "make this an ISSO group" is not one setting, it is 28 precise
writes, and doing that by hand across hundreds of groups is how drift and
findings happen.

The cycle is: PULL the group (discover its module ids), MERGE the ids with
the role template (intent), PUSH the resolved config back.

Usage:
  python scripts/group_permission_templater.py --app Site-Alpha --group ISSO --template isso --dry-run
  python scripts/group_permission_templater.py --app Site-Alpha --group ISSO --template isso
  python scripts/group_permission_templater.py --list-templates
"""

import argparse
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grc_client import MockClient

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "..", "templates", "permission-templates.yaml")

ACCESS = {
    "full":       dict(create=True,  read=True,  update=True,  delete=True),
    "contribute": dict(create=True,  read=True,  update=True,  delete=False),
    "update":     dict(create=False, read=True,  update=True,  delete=False),
    "read":       dict(create=False, read=True,  update=False, delete=False),
    "none":       dict(create=False, read=False, update=False, delete=False),
}


def load_templates():
    with open(TEMPLATES) as f:
        return yaml.safe_load(f)["roles"]


def resolve(group, template):
    """Merge discovered module ids with template intent. Returns the full
    permission list ready to push."""
    default = template.get("default", "read")
    overrides = template.get("overrides") or {}
    resolved = []
    for mod in group["modules"]:
        level = overrides.get(mod["module"], default)
        if level not in ACCESS:
            raise ValueError(f"unknown access level {level!r} for module {mod['module']}")
        entry = {"module_id": mod["module_id"], "module": mod["module"]}
        entry.update(ACCESS[level])
        resolved.append(entry)
    return resolved


def diff(current_modules, resolved):
    """Human readable diff so the dry run means something."""
    cur = {m["module_id"]: m for m in current_modules}
    changes = []
    for m in resolved:
        old = cur[m["module_id"]]
        flips = []
        for k in ("create", "read", "update", "delete"):
            if bool(old.get(k)) != m[k]:
                flips.append(f"{k}: {bool(old.get(k))} -> {m[k]}")
        if flips:
            changes.append((m["module"], flips))
    return changes


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--app", help="application (container) name")
    ap.add_argument("--group", help="group name inside the application")
    ap.add_argument("--template", help="role template key, e.g. isso, admin")
    ap.add_argument("--dry-run", action="store_true",
                    help="show the diff, write nothing")
    ap.add_argument("--list-templates", action="store_true")
    args = ap.parse_args()

    templates = load_templates()

    if args.list_templates:
        for name, t in templates.items():
            print(f"{name:10s} default={t.get('default'):10s} {t.get('description','')}")
        return 0

    if not (args.app and args.group and args.template):
        ap.error("--app, --group and --template are required (or --list-templates)")

    key = args.template.upper().replace("_", "-")
    if key not in templates:
        print(f"no template {key!r}. available: {', '.join(templates)}")
        return 2

    client = MockClient()
    group = client.get_group(args.app, args.group)
    resolved = resolve(group, templates[key])
    changes = diff(group["modules"], resolved)

    print(f"application : {args.app}")
    print(f"group       : {args.group}  ({len(group['modules'])} modules discovered)")
    print(f"template    : {key}")

    if not changes:
        print("result      : already compliant with template, nothing to do")
        return 0

    print(f"result      : {len(changes)} module(s) would change")
    for module, flips in changes:
        print(f"  {module:20s} " + "; ".join(flips))

    if args.dry_run:
        print("\ndry run, nothing written. drop --dry-run to apply.")
        return 0

    client.put_group_permissions(args.app, args.group, resolved)
    print("\napplied. rerun with --dry-run to verify it reports clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
