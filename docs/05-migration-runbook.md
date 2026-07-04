# Migration Runbook: First Wave, One Office, Done Right

Scope: the first program office wave, moving off the legacy tools and spreadsheets into the platform ahead of the service launch. This runbook is written so that the second wave can be run by someone who was not in the room for the first one.

## Phase 0: Intake (before anything is touched)

Sit with the office and capture how they actually work today, not how their SOP says they work. For each workflow, record: the trigger, the artifacts produced, who touches it, and where it lives now. Then split every requirement into one of two buckets:

- **Mission or compliance need.** Maps to a departmental standard. Non negotiable, gets built.
- **Local preference.** Gets an honest conversation. Some preferences are free to honor, some cost the department standardization. The decision and the why get written down either way.

Exit criteria: signed intake sheet, agreed control catalog and overlay set, named office POC with authority to answer questions in hours rather than weeks.

## Phase 1: Prepare

1. Run the export from the legacy source (whichever GRC tool or spreadsheet pile they live in).
2. Run `csv_normalizer.py` against the export. Review the exception report. Every row it rejects is a conversation with the office, not a silent fix. Data quality sins committed during migration become permanent residents.
3. Generate the office's application, groups, and Entra change request with the provisioner. Submit to the directory team. This is the long pole, submit it first.
4. Apply permission templates to the platform groups with the templater, dry run reviewed, then live.

## Phase 2: Load

1. Import normalized CSVs into the office's application in the test environment.
2. Office POC validates: system inventory complete, artifacts attached to the right systems, POA&M counts match the legacy source. Get the sign off in writing.
3. Repeat the import in production. Same files, no edits between environments. If production needs a different file than test did, something is wrong, stop.

## Phase 3: Cutover

1. Freeze the legacy source. Read only, dated banner, named exceptions only.
2. Users get access through their Entra groups, verified by the drift check the same morning.
3. Vendor led targeted training within the first week while the office still remembers their questions.
4. Run the office's first real data call out of the platform within the first month. Nothing builds trust in a new tool like the moment it answers a question the spreadsheets could not.

## Phase 4: Handoff to O&M

The wave is not done when the data is in. It is done when:

- The office's SOPs exist in the platform's terms (if they had none, we wrote them together during intake)
- The Ansible playbook for their group management runs clean on a schedule
- Drift check is scheduled and someone is named to read it
- The lessons learned doc for this wave is written and the runbook is updated, because wave two starts from this document, not from memory

## The unglamorous truth about GRC migrations

People do not resist new tools, they resist losing fluency. The analyst who could answer any question in ninety seconds from their spreadsheet is starting over, and for the first month the new platform makes them slower. Training, visible SOPs, and a responsive fix loop during the first weeks matter more to adoption than any feature the platform has. Budget the time for it.
