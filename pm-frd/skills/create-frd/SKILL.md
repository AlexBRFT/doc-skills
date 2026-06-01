---
name: create-frd
description: "Create a Feature Requirement Document using a structured 7-section template: Name, Why, Objective, Requirements (user stories/use cases table), Functional and Non-Functional requirements, User Interaction flow chart, and Acceptance criteria (checkbox list). Then publish to Confluence, SharePoint, and Jira. Two-phase workflow: draft first, publish only after user confirms."
---

# Create a Feature Requirement Document

## CRITICAL RULES — ALWAYS FOLLOW

1. **TWO-PHASE WORKFLOW.** Phase 1: generate .docx draft and PRESENT IT TO THE USER. Phase 2: publish. NEVER go to Phase 2 without user saying "publish".
2. **STOP AFTER GENERATING THE DRAFT.** Show the .docx, ask user to review. WAIT for "publish", "go", or "confirmed" before touching Confluence/SharePoint/Jira.
3. **NEVER call `getConfluenceSpaces` or list spaces. NEVER ask which space.** The space ID is `53575693`. Use it directly.
4. **ALWAYS pass `parentId: "53608488"` when creating Confluence pages.** Without parentId the page lands at space root which is WRONG.
5. **NEVER use Microsoft 365 MCP connector for SharePoint upload.** It is read-only and returns 403. Use Claude in Chrome browser automation instead.
6. **NEVER skip the Jira update step.** Always update customfield_10124 and add a comment with actual URLs.
7. **Acceptance criteria = FLAT checkbox list, NOT a table.** Each item is a paragraph: `☐ Given X, when Y, then Z`. NO columns, NO Verification Method column.

## Hardcoded Configuration — NEVER ASK THE USER FOR THESE

```
CONFLUENCE_CLOUD_ID    = friendly-tech.atlassian.net
CONFLUENCE_SPACE_ID    = 53575693
CONFLUENCE_PARENT_ID   = 53608488
SHAREPOINT_SITE        = friendlytech.sharepoint.com
SHAREPOINT_FOLDER      = /Shared Documents/Product/Feature Requests/FRDs
JIRA_FRD_FIELD         = customfield_10124
```

## Purpose

You are an experienced product manager creating a Feature Requirement Document (FRD). This document specifies a single feature with enough detail for engineering to build, QA to test, and stakeholders to approve.

---

## PHASE 1: DRAFT

### Step 1: Collect Inputs
Ask only for:
1. Feature or problem statement
2. Jira issue key (e.g. PROD-456)

Do NOT ask for Confluence space, parent page, or SharePoint folder.

### Step 2: Gather Feature Context
Ask about: problem, target users, success criteria, constraints, scope. Skip what's already clear from the user's input.

### Step 3: Generate FRD .docx
Create a Word document (.docx) with this exact structure. No emojis. No reordering.

1. **NAME** — concise, specific, unambiguous
2. **WHY?** — problem and customer/business impact. Quantify where possible.
3. **OBJECTIVE** — solution objective, what changes for the user, tie to business metrics
4. **REQUIREMENTS** — table: # | Requirement | User Story / Use Case | Description
5. **FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS** — Functional list + Non-functional (performance, security, scalability minimum)
6. **USER INTERACTION AND DESIGN** — text-based flow chart showing primary user flow
7. **ACCEPTANCE CRITERIA — CHECKBOX LIST, NOT A TABLE.**

   In the .docx: each criterion is its own paragraph starting with ☐ (Unicode U+2610) followed by a space. Example:
   ```
   ☐ Given a user with admin role, when they click Block, then the user's session is invalidated immediately
   ☐ Given a blocked user, when they attempt to log in, then login is silently denied
   ☐ Given any block/unblock action, when it completes, then an audit log entry is created
   ```

   In Confluence: use `<ac:task-list>` with `<ac:task>` elements. NEVER use a `<table>` for acceptance criteria.

   **DO NOT create a table with columns # | Criterion | Verification Method. That is the OLD format. The NEW format is a flat checkbox list.**

Save as: `FRD-[feature-name-kebab-case].docx`

### Step 4: STOP — PRESENT DRAFT AND WAIT

Present the .docx to the user. Say:

"FRD draft ready. Review it and tell me:
1. **Publish** — I'll push to Confluence, SharePoint, and update Jira
2. **Feedback** — tell me what to change
3. **Cancel** — keep the local file only"

**DO NOT PROCEED. DO NOT CREATE CONFLUENCE PAGE. DO NOT TOUCH JIRA. WAIT FOR USER RESPONSE.**

### Step 5: Revision Loop
- User gives feedback → apply changes, regenerate .docx, present again, repeat Step 4
- User says "publish" → proceed to Phase 2
- User says "cancel" → stop

---

## PHASE 2: PUBLISH (only after user explicitly confirms)

### Step 6: Confluence Page

**DO NOT call `getConfluenceSpaces` or any tool that lists spaces. DO NOT ask the user which space to use. The space is HARDCODED below.**

Call `createConfluencePage` directly with ALL of these parameters:
- `cloudId`: `friendly-tech.atlassian.net`
- `spaceId`: `53575693`
- `parentId`: `53608488` ← REQUIRED — creates page under "Feature requirement document"
- `title`: `FRD: [Feature Name]`
- `contentFormat`: `html`
- `body`: FRD content as HTML with headings, tables, and task-list checkboxes

**VERIFY: parentId MUST be "53608488". If you omit it, the page goes to space root which is WRONG.**

If the call fails with "space not found" or similar, your Atlassian MCP connector is connected to the WRONG instance. Tell the user: "Your Atlassian connector in Cowork is not pointed at friendly-tech.atlassian.net. Please reconnect it under Customize → connectors." Do not try to find an alternative space.

Save the Confluence page URL for Step 8.

### Step 7: SharePoint Upload

**DO NOT use Microsoft 365 MCP connector. It is read-only. It WILL return 403.**

Use Claude in Chrome to upload via SharePoint REST API:

1. Base64-encode the .docx: `base64 -w 0 /path/to/file.docx`
2. Navigate browser to: `https://friendlytech.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2FProduct%2FFeature%20Requests%2FFRDs`
3. Store base64 chunks in browser via `javascript_tool` calls (10KB chunks)
4. Final JS call: join chunks, decode, upload via `/_api/web/GetFolderByServerRelativeUrl('/Shared%20Documents/Product/Feature%20Requests/FRDs')/Files/add(url='[FILENAME]',overwrite=true)`

SharePoint URL: `https://friendlytech.sharepoint.com/Shared%20Documents/Product/Feature%20Requests/FRDs/[FILENAME]`

If Chrome is not available → ask user to upload .docx manually and provide the URL.

### Step 8: Jira Update — MANDATORY, NEVER SKIP

**8a.** Call `editJiraIssue`:
- `cloudId`: `friendly-tech.atlassian.net`
- `issueIdOrKey`: `PROD-XXX`
- `fields`: `{"customfield_10124": "[SHAREPOINT_URL]"}` (or Confluence URL if SharePoint was skipped)

**8b.** Call `addCommentToJiraIssue`:
- `commentBody`: real URLs from Steps 6 and 7. NEVER "links will be added later."

### Step 9: Summary Table

Show: FRD generated, Confluence page, SharePoint upload, Jira field, Jira comment — each with status and actual link.

---

## Error Handling
- Chrome not connected → skip SharePoint, use Confluence URL in Jira, provide .docx for manual upload
- Confluence fails → report error, continue to SharePoint and Jira
- SharePoint fails → report error, use Confluence URL in Jira
- Jira fails → report error, never silently skip
