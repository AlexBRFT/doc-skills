---
description: Create a Feature Requirement Document (.docx), review and refine it, then publish to Confluence, SharePoint, and Jira on confirmation
argument-hint: "<feature name or problem statement> [--jira PROD-XXX]"
---

# /write-frd -- Feature Requirement Document + Publish Pipeline

## CRITICAL RULES — READ FIRST

1. **STOP AFTER GENERATING THE DRAFT.** Present the .docx to the user and WAIT. Do NOT proceed to Confluence, SharePoint, or Jira until the user explicitly says "publish", "go", "confirmed", or "ship it".
2. **NEVER ask for Confluence space, parent page, or SharePoint folder.** They are hardcoded below.
3. **ALWAYS pass `parentId: 53608488` when creating Confluence pages.** Without it the page lands at space root, which is WRONG.
5. **For SharePoint: save .docx to local OneDrive folder, wait 10 seconds for sync, construct SharePoint URL.** DO NOT use Microsoft 365 MCP. DO NOT use Chrome browser automation.
5. **NEVER skip the Jira step.** Always update customfield_10124 and add a comment with real URLs.
6. **Jira comment is LAST.** Only add the comment AFTER Confluence and SharePoint, with ACTUAL URLs — never placeholders.
7. **Filename MUST start with the Jira issue key.** Format: `PROD-XXX-FRD-[feature-name].docx` (e.g. `PROD-559-FRD-admin-block-user.docx`). Never save an FRD without the Jira key prefix.

## Hardcoded Configuration

These values are FIXED. Use them directly in API calls. Never ask the user for them.

```
CONFLUENCE_CLOUD_ID    = friendly-tech.atlassian.net
CONFLUENCE_SPACE_ID    = 53575693
CONFLUENCE_PARENT_ID   = 53608488
ONEDRIVE_LOCAL_PATH    = C:\Users\Alex.Baraginskii\OneDrive - Friendly Technologies\Product\Feature Requests\FRDs\Claude_FRD
SHAREPOINT_URL_PREFIX  = https://friendlytech.sharepoint.com/:w:/r/Shared%20Documents/Product/Feature%20Requests/FRDs/Claude_FRD
JIRA_FRD_FIELD         = customfield_10124
ONEDRIVE_SYNC_WAIT     = 10 seconds
```

---

## PHASE 1: DRAFT (always runs)

### Step 1: Collect Inputs

Ask only for:
1. **Feature or problem statement**
2. **Jira issue key** (e.g. PROD-456)

### Step 2: Gather Feature Context

Ask about: problem, target users, success criteria, constraints, scope. Skip what's already clear.

### Step 3: Generate FRD .docx

Create a Word document with this exact structure (no emojis):

1. NAME
2. WHY? — problem and customer/business impact
3. OBJECTIVE — solution objective and how it solves the problem
4. REQUIREMENTS — table: # | Requirement | User Story / Use Case | Description
5. FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS
6. USER INTERACTION AND DESIGN — text-based flow chart
7. ACCEPTANCE CRITERIA — checkbox list (NOT a table). Each criterion is a line with an unchecked checkbox: ☐ Given [X], when [Y], then [Z]. QA team checks the box when passed. In Confluence, use task-list elements. In .docx, use ☐ unicode character prefix.

Save as: `[JIRA-KEY]-FRD-[feature-name-kebab-case].docx` — the filename MUST start with the Jira issue key (e.g. `PROD-559-FRD-admin-block-user.docx`). This makes files searchable by ticket number.

### Step 4: STOP AND WAIT FOR USER REVIEW

Present the .docx file to the user. Then say exactly:

"FRD draft ready. Review it and tell me:
1. **Publish** — I'll push to Confluence, SharePoint, and update Jira
2. Give me **feedback** — tell me what to change
3. **Cancel** — keep the local file, skip publishing"

**DO NOT PROCEED TO PHASE 2. WAIT FOR THE USER TO RESPOND.**

### Step 5: Revision Loop

If user gives feedback: apply changes, regenerate .docx, present again, repeat Step 4.
If user says "publish": proceed to Phase 2.
If user says "cancel": stop.

---

## PHASE 2: PUBLISH (only after user says "publish")

Execute these steps in order. Each step uses hardcoded configuration above.

### Step 6: Create Confluence Page

Use the Atlassian MCP connector. Call `createConfluencePage` with EXACTLY these parameters:
- `cloudId`: `friendly-tech.atlassian.net`
- `spaceId`: `53575693`
- `parentId`: `53608488`  ← THIS IS REQUIRED. Without it the page lands at space root. ALWAYS pass parentId.
- `title`: `FRD: [Feature Name]`
- `contentFormat`: `html`
- `body`: Convert the FRD content to HTML (headings, tables, task-list checkboxes for acceptance criteria)

**If the page is created without parentId, it is WRONG. The page MUST be a child of page 53608488 ("Feature requirement document").**

Add labels: `frd`, `PROD-XXX`

Save the resulting page URL. You need it for Step 8.

If this step fails, report the error and continue to Step 7.

### Step 7: Save to OneDrive (auto-syncs to SharePoint)

**DO NOT upload via Microsoft 365 MCP. DO NOT use Chrome browser automation.**

The user's OneDrive folder syncs to SharePoint automatically. Save the .docx locally, wait for sync, construct the URL.

**7a. Write the .docx to:**
```
C:\Users\Alex.Baraginskii\OneDrive - Friendly Technologies\Product\Feature Requests\FRDs\Claude_FRD\[FILENAME].docx
```

**7b. Wait 10 seconds** for OneDrive sync.

**7c. Get the proper SharePoint URL — MANDATORY.**

The path-only URL `https://friendlytech.sharepoint.com/:w:/r/.../file.docx` triggers a download. The web-viewer URL requires query parameters: `?d=[GUID]&csf=1&web=1&e=[TOKEN]`.

**You MUST get the URL with query parameters. A path-only URL is WRONG and will trigger downloads.**

**Try in this exact order:**

**Attempt 1: Microsoft 365 MCP search.** Call `sharepoint_search`:
```
query: "[JIRA-KEY]" (e.g. "PROD-559" — the filename starts with this, so it is unique and searchable)
folderName: "Claude_FRD"
fileType: "docx"
limit: 1
```
Extract `webUrl` from the result. Verify it contains `?d=` and `&web=1`. If yes, use this URL.

**Attempt 2: Retry after wait.** If search returned no results, wait another 15 seconds (OneDrive sync may be slow) and retry the search once more.

**Attempt 3: Manual fallback.** If both search attempts fail, DO NOT use the path-only URL. Instead:
1. Tell the user: "OneDrive sync seems delayed. Please open the file in SharePoint manually, click Share → Copy link, and paste the URL here."
2. Use the URL the user provides as the SharePoint link.

**Verification before continuing to Step 8:** The URL must contain `?d=` and `&web=1`. If it doesn't, do NOT proceed — get a proper URL first.

This URL goes into Jira customfield_10124 in Step 8.

**Error handling:**
- If folder doesn't exist → ask user to create it
- If file write fails → use Confluence URL as fallback in Jira
- Do NOT verify the SharePoint URL is reachable — just construct it

### Step 8: Update Jira

**THIS STEP IS MANDATORY. NEVER SKIP IT.** Even if Confluence or SharePoint failed, still update Jira with whatever URLs are available.

Use the Atlassian MCP connector. Do TWO things:

**8a. Update the "Link to FRD" field:**
Call `editJiraIssue` with:
- `cloudId`: `friendly-tech.atlassian.net`
- `issueIdOrKey`: `PROD-XXX`
- `fields`: `{"customfield_10124": "[SHAREPOINT_FILE_URL]"}`

If SharePoint upload was skipped, use the Confluence page URL instead.

**8b. Add a comment with ACTUAL URLs:**
Call `addCommentToJiraIssue` with:
- `cloudId`: `friendly-tech.atlassian.net`
- `issueIdOrKey`: `PROD-XXX`
- `commentBody`:
```
Feature Requirement Document published:
- SharePoint: [ACTUAL SHAREPOINT URL FROM STEP 7]
- Confluence: [ACTUAL CONFLUENCE URL FROM STEP 6]
```

**NEVER add a comment saying "links will be added later." Only add the comment with real URLs.**

### Step 9: Summary

Show this table:

```
| Step                | Status | Link                          |
|---------------------|--------|-------------------------------|
| FRD generated       | Done   | [filename]                    |
| Confluence page     | Done   | [actual confluence page URL]  |
| SharePoint upload   | Done   | [actual sharepoint file URL]  |
| Jira "Link to FRD"  | Done   | [jira issue URL]              |
| Jira comment        | Done   | comment with both URLs        |
```

### Step 10: Next Steps

Offer:
- Break into user stories → `/write-stories`
- Run a pre-mortem → `/pre-mortem`
- Generate test scenarios → `/test-scenarios`

---

## Error Handling

- **Chrome not connected**: Skip SharePoint, use Confluence URL in Jira field, provide .docx for manual upload
- **Confluence fails**: Report error, continue to SharePoint and Jira
- **SharePoint fails**: Report error, use Confluence URL in Jira field instead
- **Jira field update fails**: Fall back to comment only
- **Partial failure**: Always complete all possible steps and report what failed

## Notes

- FRD format is fixed — do not rearrange sections or add emojis
- The .docx is the source of truth, stored in SharePoint
- Confluence page is a readable mirror
- SharePoint URL (not Confluence) goes into Jira customfield_10124
- NEVER publish without explicit user confirmation
- NEVER add Jira comments with placeholder text — only real URLs
