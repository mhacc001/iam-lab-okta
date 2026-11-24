# Okta Workforce IAM Lab: Attribute-Driven RBAC and JML Automation

A workforce identity program for a small company, written as code for Okta. Terraform builds the directory model, group rules, apps and policies. Python scripts run the joiner-mover-leaver (JML) lifecycle and export an access review against the Okta API.

**Author:** Marie Haccandy, M.S. Cybersecurity Management · [LinkedIn](https://www.linkedin.com/in/marie-christine-haccandy-24b6b21ba) · [GitHub](https://github.com/mhacc001)

## The design in one rule

**No access is ever granted directly to a user.** A user's `department` attribute places them in groups through Okta group rules, and apps are assigned only to groups. As a result:

| Lifecycle event | What an admin does | What happens |
|---|---|---|
| Joiner | Create the user with a department | Group rules add the right groups. Apps follow the groups. |
| Mover | Change the department | Old groups and apps fall away, new ones attach. The script logs the difference. |
| Leaver | Deactivate | Every group and app is removed at once. The account is kept in DEPROVISIONED state for audit. |
| Access review | Run one script | Exports who has access to what as CSV. A query, not an investigation. |

Why rules instead of manual group assignment: manual assignments drift and rarely get removed. Rules re-evaluate every time the attribute changes, so the access model stays explicit and auditable. Full rationale: [docs/rbac-model.md](docs/rbac-model.md).

## What the code builds

| Area | Implementation | File |
|---|---|---|
| Groups | Engineering, Sales, IT, Contractors, plus All Staff | [terraform/main.tf](terraform/main.tf) |
| Group rules | `user.department == "<dept>"` per department, `user.status == "ACTIVE"` for All Staff | [terraform/main.tf](terraform/main.tf) |
| Apps | Two OIDC apps (Internal Portal for All Staff, Engineering Tools for Engineering), assigned to groups only | [terraform/main.tf](terraform/main.tf) |
| Authentication | MFA enrollment required for All Staff (password, email, Okta Verify) in Terraform; a stricter Contractor policy is designed in the policy doc | [terraform/main.tf](terraform/main.tf), [docs/mfa-policy.md](docs/mfa-policy.md) |
| Password policy | 12-character minimum, history of 8, lockout after 5 attempts | [terraform/main.tf](terraform/main.tf) |
| JML automation | `onboard`, `move`, `offboard` commands that print groups and apps added or removed | [scripts/jml.py](scripts/jml.py) |
| Access review | CSV export of every user's status, groups and apps | [scripts/access_review.py](scripts/access_review.py) |

Step-by-step lifecycle flows: [docs/jml-flows.md](docs/jml-flows.md).

## Deploy it

Runs on a free Okta Integrator (developer) org.

```bash
# 1. Build the identity model
cd terraform
cp terraform.tfvars.example terraform.tfvars   # org name, base URL, API token
terraform init && terraform apply

# 2. Run the lifecycle
cd ../scripts
export OKTA_ORG_URL="https://dev-XXXXX.okta.com"
export OKTA_API_TOKEN="..."
python3 -m pip install -r requirements.txt

python3 jml.py onboard  --first Ada --last Lovelace --dept Engineering --email ada@example.com
python3 jml.py move     --email ada@example.com --new-dept Sales
python3 jml.py offboard --email ada@example.com
python3 access_review.py > access-review.csv
```

Example mover output:

```
[mover] ada@example.com: Engineering -> Sales
[mover] groups added:   ['Sales']
[mover] groups removed: ['Engineering']
[mover] apps added:     []
[mover] apps removed:   ['Engineering Tools']
```

How to verify each step in the Okta admin console: [docs/RUNBOOK.md](docs/RUNBOOK.md).

## Related work

- [identity-governance-lab](https://github.com/mhacc001/identity-governance-lab): SCIM 2.0 provisioning, access certification campaigns, separation-of-duties checks and non-human identity audits
- [it-jml-toolkit](https://github.com/mhacc001/it-jml-toolkit): the same lifecycle in PowerShell against Microsoft Entra ID through Microsoft Graph

## Tools

Okta · Terraform (okta provider) · Python · Okta Management API · OIDC · MFA policy · RBAC · joiner-mover-leaver · access review
