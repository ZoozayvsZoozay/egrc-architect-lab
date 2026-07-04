# Control Mapping: How This Work Becomes Accreditation Evidence

A GRC platform has to pass the same bar it holds everyone else to. The automation in this repo is not just operational convenience, each piece produces artifacts that map directly into the SSP and the continuous monitoring program. This table is how I would write it up.

| NIST SP 800-53 Rev 5 | Control | What in this repo satisfies or evidences it |
|---|---|---|
| AC-2 | Account Management | Provisioner change request packages are the documented account/group creation approvals. Drift reports evidence periodic account reviews. Naming convention makes group purpose self documenting. |
| AC-2(1) | Automated Account Management | Templater and Ansible playbook are the automated mechanisms. Dry run diffs are the review record. |
| AC-3 | Access Enforcement | Permission templates define enforced authorizations per role. Applied CRUD matrices per module are exportable as evidence. |
| AC-5 | Separation of Duties | Directory team applies Entra changes, application team applies platform changes, neither can do both. The change request workflow is the artifact. |
| AC-6 | Least Privilege | Role catalog grants by intent, ASSESSOR and AUDITOR roles are read biased and time boxed. Restricted application split limits exposure of the sensitive site. |
| AC-6(9) | Auditing Privileged Functions | Tenant admin access to the restricted application is logged and reviewed on cadence per the segregation paper's compensating controls. |
| CA-6 | Authorization | Decision papers (doc 03) and signed risk acceptances are the authorizing official's record for residual risks. |
| CA-7 | Continuous Monitoring | Scheduled drift checks and playbook runs produce timestamped, diffable evidence of configuration stability. |
| CM-2 | Baseline Configuration | permission-templates.yaml is the access baseline, version controlled, with change history in git. |
| CM-3 | Configuration Change Control | Every change flows through plan, package, review, apply. The repo history and CR bundles are the change records. |
| CM-6 | Configuration Settings | Templater enforces defined settings across all groups, drift check verifies they stay enforced. |
| AU-6 | Audit Record Review | Drift reports and admin access reviews are standing review artifacts with named readers. |
| PL-8 | Security Architecture | Docs 01 through 04 and the diagrams are the security architecture description, written to be lifted into the SSP. |
| SA-9 | External System Services | The SaaS boundary analysis (vendor owns instance, we own tenant) and the tenant admin visibility risk are documented honestly in docs 01 and 03. |

## The point behind the table

Most teams build automation and then scramble to describe it for the assessors. Flip it: design the automation so its normal outputs are the evidence. A drift report nobody asked for is toil. A drift report mapped to AC-2 and CA-7, produced on schedule, with a named reviewer, is a control implementation. Same work, different framing, and the second framing is what an accreditation strategy actually means in practice.
