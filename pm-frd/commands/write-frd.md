---
description: Create a Feature Requirement Document (.docx), publish to Confluence, upload to SharePoint, and link in Jira
argument-hint: "<feature name or problem statement> [--jira PROJ-123] [--confluence-space SPACE] [--sharepoint-folder path/to/folder]"
---

# /write-frd -- Feature Requirement Document + Publish Pipeline

Generate a structured FRD as a Word document, then push it through your delivery pipeline: Confluence page, SharePoint upload, Jira field update. Runs end-to-end in one command.

## Invocation

```
/write-frd SSO for enterprise customers --jira PROJ-456 --confluence-space ENG --sharepoint-folder "Product/FRDs"
/write-frd Users can't export reports in bulk --jira PROJ-789
/write-frd [upload a brief or research doc] --jira PROJ-101 --confluence-space PROD
/write-frd                                   # interactive — asks for everything
```

All flags are optional. If omitted, the command asks interactively.

## Workflow

### Step 1: Collect Inputs

If not provided via flags, ask for each — one question at a time, most critical first:

1. **Feature or problem statement** — accept anything: a name, a pain point, a user request, an uploaded doc
2. **Jira issue key** — e.g. `PROJ-123`. Required for linking. If unknown, ask if the user wants to create one or skip Jira linking.
3. **Confluence space key** — e.g. `ENG`, `PROD`. If unknown, list available spaces via Atlassian MCP and let user pick.
4. **SharePoint folder path** — e.g. `Product/FRDs/2025`. If unknown, ask or skip.

### Step 2: Gather Feature Context

Ask conversationally — prioritize gaps, skip what's already clear:

1. **Problem**: What problem does this solve? Who is affected? What's the business/customer impact?
2. **Target users**: Which segment(s)? Current workarounds?
3. **Success criteria**: How do we know this worked?
4. **Constraints**: Technical, timeline, regulatory, dependencies?
5. **Scope**: Full solution or phased?

If the user uploaded a document with context, extract what's available and only ask about genuine gaps.

### Step 3: Generate the FRD

Produce a Word document (.docx) following this exact structure. Do not use emojis.

```
FEATURE REQUIREMENT DOCUMENT
[Feature Name]

Author: [user]
Date: [today]
Status: Draft
Jira: [PROJ-123 — hyperlinked to Jira URL]

─────────────────────────────────────────

1. NAME
[Feature name — concise, unambiguous]

2. WHY?
[Describe the problem and how it impacts customer and/or business.
Be specific: quantify impact where possible. Reference user research,
support tickets, churn data, or competitive pressure if available.]

3. OBJECTIVE
[Describe the solution objective and how it will solve the problem.
State what changes for the user after this ships. Tie to business metrics.]

4. REQUIREMENTS

| # | Requirement | User Story / Use Case | Description |
|---|-------------|----------------------|-------------|
| 1 | [Req name]  | As a [user], I want [X] so that [Y] | [Detailed description, edge cases, constraints] |
| 2 | ...         | ...                  | ...         |

5. FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS

Functional:
- [F1: Description]
- [F2: Description]

Non-Functional:
- [NF1: Performance — e.g., response time < 200ms]
- [NF2: Security — e.g., RBAC, encryption at rest]
- [NF3: Scalability — e.g., support 10K concurrent users]
- [NF4: Accessibility — e.g., WCAG 2.1 AA]

6. USER INTERACTION AND DESIGN
[Include a text-based flow chart describing the primary user flow.
Use a clear step-by-step flow or decision tree format.]

Example format:
  User opens feature → Selects option A or B
    → Option A: [step] → [step] → Success state
    → Option B: [step] → Error handling → Retry or exit

[Note: attach wireframes/mockups separately if available.]

7. ACCEPTANCE CRITERIA

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | [Given X, when Y, then Z] | [Manual test / Automated / Review] |
| 2 | ... | ... |
```

Save as: `FRD-[feature-name-kebab-case].docx`

Embed the Jira issue URL as a hyperlink in the header section.

### Step 4: Publish to Confluence

Using the Atlassian MCP connector:

1. Create a new page in the specified Confluence space
2. Page title: `FRD: [Feature Name]`
3. Convert the FRD content to Confluence-compatible format (headings, tables, panels)
4. Add labels: `frd`, `feature-requirements`, `[project-key]`
5. Add a note at the top: "Source document: [SharePoint link — added after Step 5]"

Store the Confluence page URL for Step 6.

If Confluence is unavailable or the user skipped this step, continue to Step 5.

### Step 5: Upload to SharePoint

Using the Microsoft 365 MCP connector:

1. Upload the .docx file to the specified SharePoint folder
2. If the folder doesn't exist, ask the user — do not create folders without confirmation
3. Retrieve the SharePoint sharing URL for the uploaded file

Store the SharePoint URL for Step 6.

If SharePoint is unavailable or the user skipped this step, continue to Step 6.

### Step 6: Update Jira Issue

Using the Atlassian MCP connector:

1. Add a comment to the Jira issue:
   ```
   Feature Requirement Document published:
   - SharePoint: [SharePoint URL]
   - Confluence: [Confluence page URL]
   ```
2. If the issue has a custom field for document links (e.g., "Documentation", "FRD Link"), update it with the SharePoint URL
3. If no custom field exists, the comment is sufficient

### Step 7: Summary

After all steps complete, present a status table:

```
Pipeline complete:

| Step          | Status | Link                    |
|---------------|--------|-------------------------|
| FRD generated | Done   | [local file path]       |
| Confluence    | Done   | [Confluence page URL]   |
| SharePoint    | Done   | [SharePoint file URL]   |
| Jira updated  | Done   | [Jira issue URL]        |
```

If any step failed or was skipped, note it clearly with the reason.

### Step 8: Offer Next Steps

- "Want me to **break this into user stories** for the backlog?" → `/write-stories`
- "Should I **run a pre-mortem** on this feature?" → `/pre-mortem`
- "Want me to **generate test scenarios** from the acceptance criteria?" → `/test-scenarios`
- "Should I **create a stakeholder update** to socialize the FRD?"

## Error Handling

- **MCP connector not authenticated**: Tell the user which connector needs re-authentication and skip that step. Complete remaining steps.
- **Confluence space not found**: List available spaces and ask user to pick one.
- **SharePoint folder not found**: Ask user for the correct path. Do not create folders.
- **Jira issue not found**: Ask user to verify the issue key. Offer to search by summary.
- **Partial failure**: Complete all possible steps, report which ones failed, and provide the local .docx file regardless.

## Notes

- The FRD format is fixed — do not rearrange sections or add emojis
- Requirements table must use User Story OR Use Case format, not a mix, unless the user explicitly requests both
- Flow charts in Section 6 are text-based; suggest the user attach visual wireframes separately
- The .docx is the source of truth; Confluence page is a readable mirror
- If the feature is too large for one FRD, proactively suggest splitting into multiple FRDs by domain or phase
- Non-functional requirements are not optional — always include at minimum: performance, security, scalability
