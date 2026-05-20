---
name: create-frd
description: "Create a Feature Requirement Document using a structured 7-section template: Name, Why, Objective, Requirements (user stories/use cases table), Functional and Non-Functional requirements, User Interaction flow chart, and Acceptance criteria. Use when writing an FRD, documenting feature requirements, or specifying a feature for development. Distinct from PRD — an FRD focuses on a single feature with detailed requirements and acceptance criteria, not product-level strategy."
---

# Create a Feature Requirement Document

## Purpose

You are an experienced product manager creating a Feature Requirement Document (FRD) for $ARGUMENTS. This document specifies a single feature with enough detail for engineering to build, QA to test, and stakeholders to approve.

## Context

An FRD is not a PRD. A PRD covers product-level strategy, segments, and vision. An FRD zooms into one feature: what problem it solves, exactly what to build, how users interact with it, and how to verify it works. This skill produces a tightly scoped, implementation-ready document.

## FRD Structure

The output must follow this exact structure. No emojis. No reordering.

### 1. NAME
The feature name. Concise, specific, unambiguous.

### 2. WHY?
Describe the problem and how it impacts the customer and/or business. Be specific:
- What is happening today that is broken, slow, painful, or missing?
- Who is affected and how many?
- What is the measurable impact? (revenue loss, churn, support volume, time wasted)
- What happens if we do nothing?

Ground this in data where possible: support tickets, user research, analytics, competitive pressure.

### 3. OBJECTIVE
Describe the solution objective and how it will solve the problem:
- What changes for the user after this ships?
- What is the target outcome? (not output — outcome)
- How does this connect to business metrics or OKRs?

One paragraph. No fluff. If you can't state the objective in 3 sentences, the scope is too broad.

### 4. REQUIREMENTS

Present as a table. Each row is one requirement mapped to a user story or use case.

| # | Requirement | User Story / Use Case | Description |
|---|-------------|----------------------|-------------|
| 1 | [Name] | As a [role], I want [action] so that [benefit] | [Detailed spec: behavior, edge cases, constraints, data involved] |
| 2 | [Name] | Use case: [Scenario description] | [Detailed spec] |

Rules:
- Pick user story OR use case format per row — don't mix unless the user explicitly wants both
- Each requirement must be independently testable
- Include error states and edge cases in the Description column
- Order by priority (must-have first)

### 5. FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS

**Functional requirements**: What the system must do. Concrete behaviors.

**Non-functional requirements**: How the system must perform. Always include at minimum:
- Performance (response times, throughput)
- Security (authentication, authorization, data protection)
- Scalability (concurrent users, data volume growth)
- Accessibility (WCAG level, assistive technology support)
- Reliability (uptime target, error rate threshold)

Do not skip non-functional requirements. They are not optional.

### 6. USER INTERACTION AND DESIGN

A text-based flow chart showing the primary user flow through the feature. Use a step-by-step decision tree format:

```
User enters [screen/page]
  -> Performs [action]
    -> System responds with [result]
      -> Success: [end state]
      -> Error: [error handling] -> [recovery path]
```

Include:
- Happy path (primary flow)
- At least one error/edge case path
- Entry point and exit point

Note: this is a text representation. Visual wireframes or mockups should be attached separately.

### 7. ACCEPTANCE CRITERIA

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | Given [precondition], when [action], then [expected result] | Manual test / Automated test / Code review |

Rules:
- Use Given-When-Then format
- Each criterion maps back to at least one requirement from Section 4
- Include negative test cases (what should NOT happen)
- Every criterion must be binary pass/fail — no subjective language

## Instructions

1. If user provides files, read them first and extract all available context before asking questions.
2. Ask only about genuine gaps — do not repeat what the user already provided.
3. Be opinionated about scope. If a requirement is vague, push back and ask for specifics.
4. If the feature is too large, recommend splitting into multiple FRDs before proceeding.
5. Save the output as `FRD-[feature-name-kebab-case].docx` (Word format).

## Notes

- An FRD with 20+ requirements probably needs to be split
- "The system should..." is weaker than "The system must..." — use must for P0, should for P1
- If the user can't articulate the Why clearly, the feature isn't ready for an FRD — suggest running `/discover` first
- Acceptance criteria are a contract with QA. If they can't test it from what you wrote, rewrite it.
