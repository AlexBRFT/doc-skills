---
description: Create a Feature Requirement Document (.docx), publish to Confluence, upload to SharePoint, and link in Jira
argument-hint: "<feature name or problem statement> [--jira PROD-XXX]"
---

# /write-frd -- Feature Requirement Document + Publish Pipeline

Generate a structured FRD as a Word document, then push it through your delivery pipeline: Confluence page, SharePoint upload, Jira field update. Runs end-to-end in one command.

## Defaults

These defaults are always applied unless the user explicitly overrides them:

- **Confluence space**: `Product` (space key: `PROD` or whatever the key is — resolve via Atlassian MCP on first run)
- **Confluence parent page**: The FRD page is created as a **child page** under the existing page titled "Feature requirement document" in the Product space
- **SharePoint folder**: `Shared Documents/Product/Feature Requests/FRDs` — URL: https://friendlytech.sharepoint.com/:f:/r/Shared%20Documents/Product/Feature%20Requests/FRDs
- **Jira project**: `PROD` — issue keys follow the pattern `PROD-XXXXX`
- **Jira FRD field**: The **SharePoint file URL** is written to the custom field **"Link to FRD"** on the Jira issue

## Invocation

```
/write-frd SSO for enterprise customers --jira PROD-456
/write-frd Users can't export reports in bulk --jira PROD-789
/write-frd [upload a brief or research doc] --jira PROD-101
/write-frd                                   # interactive — asks for feature and Jira key
```

Confluence space, parent page, and SharePoint folder are never asked — they use the hardcoded defaults above.

## Workflow

### Step 1: Collect Inputs

If not provided via flags, ask for each — one question at a time, most critical first:

1. **Feature or problem statement** — accept anything: a name, a pain point, a user request, an uploaded doc
2. **Jira issue key** — e.g. `PROD-456`. Must be a PROD project issue. If unknown, ask if the user wants to create one or skip Jira linking.

Do NOT ask for Confluence space, parent page, or SharePoint folder — use the defaults.

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
Jira: [PROD-XXX — hyperlinked to Jira URL]

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

1. Find the page titled "Feature requirement document" in the Product space. This is the parent page.
2. Create a **child page** under "Feature requirement document"
3. Page title: `FRD: [Feature Name]`
4. Convert the FRD content to Confluence-compatible format (headings, tables, panels)
5. Add labels: `frd`, `feature-requirements`, `PROD-XXX` (the Jira issue key)

If the parent page "Feature requirement document" is not found, warn the user and ask whether to create the page at the space root instead. Do not create the parent page without confirmation.

Store the Confluence page URL for Step 7.

If Confluence is unavailable, continue to Step 5.

### Step 5: Upload to SharePoint

Using the Microsoft 365 MCP connector:

1. Upload the .docx file to: `Shared Documents/Product/Feature Requests/FRDs` on the friendlytech.sharepoint.com site
2. The target folder URL is: https://friendlytech.sharepoint.com/:f:/r/Shared%20Documents/Product/Feature%20Requests/FRDs
3. If the folder is not accessible, warn the user — do not create folders without confirmation
4. Retrieve the SharePoint sharing URL for the uploaded file

Store the SharePoint file URL — this is the URL that goes into Jira.

If SharePoint is unavailable, continue to Step 6.

### Step 6: Update Jira Issue

Using the Atlassian MCP connector:

1. Update the **"Link to FRD"** custom field on the PROD-XXX issue with the **SharePoint file URL** from Step 5
2. If the "Link to FRD" field does not exist on the issue, try these fallbacks in order:
   a. Search for a field containing "FRD" in the name
   b. Search for a field containing "document" or "documentation" in the name
   c. If no matching field found, add a comment instead with the SharePoint URL
3. Add a comment to the Jira issue:
   ```
   Feature Requirement Document published:
   - SharePoint: [SharePoint file URL]
   - Confluence: [Confluence page URL]
   ```

The **SharePoint URL** is the primary link stored in the Jira field — not the Confluence URL. The Confluence page is a readable mirror; SharePoint is the source of truth.

### Step 7: Summary

After all steps complete, present a status table:

```
Pipeline complete:

| Step                  | Status | Link                    |
|-----------------------|--------|-------------------------|
| FRD generated         | Done   | [local file path]       |
| Confluence page       | Done   | [Confluence page URL]   |
| SharePoint upload     | Done   | [SharePoint file URL]   |
| Jira "Link to FRD"   | Done   | [Jira issue URL]        |
```

If any step failed or was skipped, note it clearly with the reason.

### Step 8: Offer Next Steps

- "Want me to **break this into user stories** for the backlog?" → `/write-stories`
- "Should I **run a pre-mortem** on this feature?" → `/pre-mortem`
- "Want me to **generate test scenarios** from the acceptance criteria?" → `/test-scenarios`
- "Should I **create a stakeholder update** to socialize the FRD?"

## Error Handling

- **MCP connector not authenticated**: Tell the user which connector needs re-authentication and skip that step. Complete remaining steps.
- **Parent page "Feature requirement document" not found**: Warn user, offer to create at space root or abort Confluence step.
- **"Link to FRD" field not found in Jira**: Try fallback field names, then fall back to comment with SharePoint URL.
- **SharePoint folder not accessible**: Warn user, provide local .docx, continue with other steps.
- **Jira issue not found**: Ask user to verify the issue key. Offer to search by summary.
- **Partial failure**: Complete all possible steps, report which ones failed, and provide the local .docx file regardless.

## Notes

- The FRD format is fixed — do not rearrange sections or add emojis
- Requirements table must use User Story OR Use Case format, not a mix, unless the user explicitly requests both
- Flow charts in Section 6 are text-based; suggest the user attach visual wireframes separately
- The .docx is the source of truth, stored in SharePoint
- Confluence page is a readable mirror of the same content
- The SharePoint URL (not Confluence URL) is what gets written to the Jira "Link to FRD" field
- If the feature is too large for one FRD, proactively suggest splitting into multiple FRDs by domain or phase
- Non-functional requirements are not optional — always include at minimum: performance, security, scalability
- Confluence page is always created under "Feature requirement document" parent in the Product space — never at root unless the parent page is missing and user confirms
