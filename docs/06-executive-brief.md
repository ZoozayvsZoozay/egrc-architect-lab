# Executive Brief: EGRC Service, Where We Stand and What Needs a Decision

*One page. Written for the CISO and OCIO leadership. Current as of launch minus five months.*

## Bottom line

The departmental GRC service is on track for launch with the first office migration. Two items need leadership decisions this month. Everything else is execution.

## Status at a glance

| Workstream | State | Note |
|---|---|---|
| Platform tenant and environments | Green | Three environments stood up, SaaS vendor owns infrastructure |
| First office migration | Green | first wave scoped, data normalization underway |
| Access control at scale | Green | Automated provisioning designed and built, directory team change request submitted |
| Data segregation for restricted site | **Decision needed** | Options paper attached, recommendation is the split application model |
| Vendor hierarchy feature | Watch | Vendor says soon, launch does not depend on it |
| O&M staffing and SOPs | Amber | Runbook and automation ready, sustainment team not yet named |

## Decision 1: Restricted site data model

One site's data must not appear in headquarters roll up. No platform setting fully solves this, tenant administrators can see all tenant data by design. Recommended path: split the site into reportable and restricted applications, cap and audit tenant admin membership, and have the site sign the residual risk. Costs some duplicate administration until the vendor ships its hierarchy feature. The alternative, keeping restricted data out of the tool, would fail that site's adoption and recreate the spreadsheet problem this program exists to end. Full options paper: doc 03.

## Decision 2: Name the O&M team

Everything we are building assumes a sustainment team runs it: scheduled group management playbooks, drift reports someone actually reads, a fix loop for the first migration wave. Those need names against them by launch minus two months, or launch inherits risk that no amount of engineering removes.

## The number worth remembering

Without automation, the access model at fifty applications means roughly 900 directory objects managed by hand across environments, and about 1,800 when the role catalog matures. With the automation in place, it is six permission templates and a review step. That difference is the margin between a service that survives its first year and one that becomes the next legacy tool.

## What I need from this group

Option selection on segregation by the next governance board, and a named O&M lead by end of month. Both have owners waiting on the answer.
