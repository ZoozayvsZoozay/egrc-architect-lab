# GRC Architect Lab

So here's the thing. I've spent the past 10 years in the security field, doing engineering, DevSecOps, and making sure tools are compliant with NIST, FedRAMP, whatever framework the system needs. And recently I've been in conversations about a problem I keep seeing everywhere: a department drowning in GRC sprawl. One office keeps their accreditation records in one legacy GRC tool, another office is on a different one, and everybody else is basically living out of CSV files and shared drives. The fix is consolidating everything onto a single SaaS GRC platform, and to be honest, buying the tool is the easy part. The hard part is the access model, the messy data, and what life looks like for the admins after launch.

Three problems in particular would not leave my head. So instead of just thinking about them, I went and built working answers to each one. Nothing in here touches anyone's real environment. Everything runs against a mock API and sample data, so you can clone it and run it in about two minutes.

## The three problems

**1. The permission templating problem.**
In this kind of platform, every application is a container. Inside each container you have groups, and each group needs Create, Read, Update, Delete permissions assigned across roughly 28 modules. The painful part is that every module carries a unique ID scoped to that group, so you can't just say "this is an admin group, give it everything." You have to pull the group, read out its module IDs, merge them with a permission template, and push the config back. Doing that by hand for every group in every application is how human error gets into an audited system. So I wrote a templater that does the pull, merge, push cycle programmatically. See `scripts/group_permission_templater.py`.

**2. The 450 group problem.**
Three roles per application, fifty applications, that's 150 groups and 150 matching roles in Entra ID for claim mapping. Mirror that across three environments and now you're managing 450 groups and 450 roles in Entra, plus the same objects again inside the GRC platform, owned by two different teams. And three roles per app is the floor. The realistic number is closer to six. So I built a provisioner that generates the full naming plan, produces a change request package the directory team can actually review and approve (because the truth is, they're never handing you write access to their directory, and they shouldn't), and runs a drift check between what the platform expects and what the directory has. See `scripts/entra_provisioner.py`.

**3. The data segregation problem.**
One site has data that must stay in the tool but must never roll up to headquarters. Tenant admins can see everything by design, and the vendor's parent child hierarchy with inheritance hasn't shipped yet. There's no clean technical fix for the tenant admin visibility issue, and pretending otherwise would be dishonest. What you can do is put compensating controls around it and write the options down so leadership can make an informed call. That decision paper is in `docs/03-data-segregation-options.md`, and it's written the way I would actually hand it to a CISO: short, outcome driven, with a recommendation.

## What is in here

```
egrc-architect-lab/
  docs/          design docs, decision papers, runbook, exec brief, control mapping
  diagrams/      hand drawn style architecture diagrams, black and white
  scripts/       working python: templater, entra provisioner, csv normalizer
  templates/     role permission templates (yaml)
  ansible/       role that wraps the templater for repeatable O&M runs
  sample-data/   a deliberately messy inventory export, like the real ones
  mock-api/      local fixtures so everything runs offline
```

## Run it

```
pip install -r requirements.txt

# 1. apply a permission template to a group (against the mock api)
python scripts/group_permission_templater.py --app "Site-Alpha" --group "ISSO" --template isso --dry-run

# 2. generate the full entra naming plan and change request package
python scripts/entra_provisioner.py plan --apps 50 --envs dev test prod

# 3. check drift between platform expectations and the directory
python scripts/entra_provisioner.py drift

# 4. clean a messy migration export
python scripts/csv_normalizer.py sample-data/legacy-inventory-export.csv
```

Every script has a `--dry-run` mode and prints what it would change before it changes anything. In an accredited environment that's not a nice to have, that's the whole point.

## Why I built this

Anybody can stand a product up. The real question is what life looks like for the administrator who inherits it after launch. If the answer is "450 groups managed by hand in two systems," the service will rot. If the answer is "run this playbook, review the diff, approve," the service survives. This repo is basically my argument for the second answer.

Docs worth reading first: the [executive brief](docs/06-executive-brief.md) if you have two minutes, the [RBAC design](docs/02-rbac-design.md) if you have ten.
