# IAM Lab (Okta)

A workforce identity lab built on a free Okta Integrator (developer) org. It
models a small company's identity program: role-based access through groups,
automated joiner-mover-leaver (JML) lifecycle, MFA enforcement, and access
reviews.

Everything here runs on the free Okta developer tier. No cost.

## What it models

| Area | Implementation |
|---|---|
| Directory | Users in departments: Engineering, Sales, Contractors, IT |
| RBAC | Access granted by group membership, never directly to a user |
| Group rules | Department attribute drives group assignment automatically |
| App access | An OIDC app assigned to groups, not individuals |
| Authentication | Sign-on policy: MFA required, stronger factor for Contractors |
| Password policy | Length, history, lockout thresholds |
| JML automation | Python scripts for onboard / move / offboard against the Okta API |
| Access review | Script that exports "who has access to what" for a quarterly review |

## Setup

1. Sign up at developer.okta.com (free). You get an org URL like `dev-12345.okta.com`.
2. Create an API token: Security > API > Tokens > Create Token. Copy it.
3. Configure Terraform:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # add org name + base url + api token
terraform init
terraform apply
```

This creates the groups, group rules, users, OIDC app, and policies.

## JML automation

```bash
cd scripts
export OKTA_ORG_URL="https://dev-12345.okta.com"
export OKTA_API_TOKEN="..."
python3 -m pip install -r requirements.txt

python3 jml.py onboard  --first Ada --last Lovelace --dept Engineering --email ada@example.com
python3 jml.py move     --email ada@example.com --new-dept Sales
python3 jml.py offboard --email ada@example.com
python3 access_review.py > ../docs/access-review-$(date +%Y%m%d).csv
```

- **onboard**: creates the user, sets the department attribute, lets the group
  rule place them, activates the account
- **move**: changes the department attribute, forces group-rule re-evaluation,
  logs the access that was added and removed
- **offboard**: deactivates the user, clears sessions, removes group memberships,
  leaves an audit record

## What to capture for your portfolio

Fill in [`docs/RUNBOOK.md`](docs/RUNBOOK.md) as you go: screenshots of the group
rules, a before/after of a mover's app access, the access-review CSV, and the
Okta system log entries showing the lifecycle events. That evidence is what makes
this a portfolio project instead of a tutorial.

## Design docs

- [`docs/rbac-model.md`](docs/rbac-model.md) — the group and access model, and why
- [`docs/jml-flows.md`](docs/jml-flows.md) — joiner/mover/leaver step by step
- [`docs/mfa-policy.md`](docs/mfa-policy.md) — the authentication policy rationale

## Honesty note

This is a lab on a developer org, not production experience. Describe it that way.
The real talking point is that you can explain and implement least-privilege
group design, lifecycle automation, and access reviews, backed by your actual
access-administration work at Innovate Springfield.
