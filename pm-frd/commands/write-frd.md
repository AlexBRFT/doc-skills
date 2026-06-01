---
description: Create a Feature Requirement Document (.docx), review and refine it, then publish to Confluence, SharePoint, and Jira on confirmation
argument-hint: "<feature name or problem statement> [--jira PROD-XXX]"
---

# /write-frd -- Feature Requirement Document + Publish Pipeline

## CRITICAL RULES — READ FIRST

1. **STOP AFTER GENERATING THE DRAFT.** Present the .docx to the user and WAIT. Do NOT proceed to Confluence, SharePoint, or Jira until the user explicitly says "publish", "go", "confirmed", or "ship it".
2. **NEVER ask for Confluence space, parent page, or SharePoint folder.** They are hardcoded below.
3. **ALWAYS pass `parentId: 53608488` when creating Confluence pages.** Without it the page lands at space root, which is WRONG.
4. **NEVER use Microsoft 365 MCP for SharePoint upload.** It is read-only (403). Use Claude in Chrome instead.
5. **NEVER skip the Jira step.** Always update customfield_10124 and add a comment with real URLs.
6. **Jira comment is LAST.** Only add the comment AFTER Confluence and SharePoint, with ACTUAL URLs — never placeholders.

## Hardcoded Configuration

These values are FIXED. Use them directly in API calls. Never ask the user for them.

```
CONFLUENCE_CLOUD_ID    = friendly-tech.atlassian.net
CONFLUENCE_SPACE_ID    = 53575693
CONFLUENCE_PARENT_ID   = 53608488
SHAREPOINT_SITE        = friendlytech.sharepoint.com
SHAREPOINT_FOLDER      = /Shared Documents/Product/Feature Requests/FRDs
SHAREPOINT_FOLDER_URL  = https://friendlytech.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2FProduct%2FFeature%20Requests%2FFRDs
JIRA_FRD_FIELD         = customfield_10124
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

Save as: `FRD-[feature-name-kebab-case].docx`

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

### Step 7: Upload to SharePoint

**DO NOT use the Microsoft 365 MCP connector. It is read-only and will return 403.**
**USE Claude in Chrome browser automation instead.**

If Claude in Chrome is not connected, ask the user to connect it. If the user declines, ask them to manually upload the .docx to SharePoint and provide the URL.

**7a. Prepare chunks:**
```bash
base64 -w 0 /path/to/FRD.docx > /tmp/frd_b64.txt
split -b 10000 /tmp/frd_b64.txt /tmp/frd_chunk_
```

**7b. Navigate browser to SharePoint:**
Navigate to: `https://friendlytech.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2FProduct%2FFeature%20Requests%2FFRDs`

**7c. Store chunks in browser:**
For each chunk file, execute a `javascript_tool` call:
```javascript
window.__c=window.__c||[];window.__c.push("[CHUNK_CONTENT]");window.__c.length
```

**7d. Upload:**
```javascript
(async()=>{
  try{
    const d=await(await fetch("https://friendlytech.sharepoint.com/_api/contextinfo",
      {method:"POST",headers:{"Accept":"application/json;odata=verbose"}})).json();
    const t=d.d.GetContextWebInformation.FormDigestValue;
    const b=atob(window.__c.join(""));
    const a=new Uint8Array(b.length);
    for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);
    const u=await fetch(
      "https://friendlytech.sharepoint.com/_api/web/GetFolderByServerRelativeUrl('/Shared%20Documents/Product/Feature%20Requests/FRDs')/Files/add(url='[FILENAME]',overwrite=true)",
      {method:"POST",headers:{"Accept":"application/json;odata=verbose",
        "X-RequestDigest":t,"Content-Type":"application/octet-stream"},body:a.buffer});
    if(!u.ok)return"Fail:"+u.status;
    const j=await u.json();
    delete window.__c;
    return"OK:"+j.d.ServerRelativeUrl
  }catch(e){return"Err:"+e.message}
})()
```

The SharePoint file URL is: `https://friendlytech.sharepoint.com/Shared%20Documents/Product/Feature%20Requests/FRDs/[FILENAME]`

Save this URL. You need it for Step 8.

If Chrome is not available or upload fails, ask user to manually upload the .docx. Still continue to Step 8.

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
