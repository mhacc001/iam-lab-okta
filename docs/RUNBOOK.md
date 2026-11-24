# Runbook: Deploy and Verify

How to stand the lab up on a free Okta Integrator org and confirm each control works. Each step names the console screen or System Log event that proves it.

## 1. Build

1. Create an API token: **Security > API > Tokens > Create Token**.
2. Fill in `terraform/terraform.tfvars` from the example file, then run `terraform init && terraform apply`.
3. Verify:
   - **Directory > Groups** shows All Staff, Engineering, Sales, IT and Contractors.
   - **Directory > Group Rules** shows `auto-all-staff` and one `auto-<dept>` rule per department, all ACTIVE.
   - **Applications** shows Internal Portal (assigned to All Staff) and Engineering Tools (assigned to Engineering). Neither has direct user assignments.

## 2. Joiner

Run `python3 jml.py onboard --first Ada --last Lovelace --dept Engineering --email ada@example.com`.

Verify:
- The user's **Groups** tab lists All Staff and Engineering.
- **Reports > System Log**, filtered to the user, shows `group.user_membership.add` events with the group rule as the actor.

## 3. Mover

Run `python3 jml.py move --email ada@example.com --new-dept Sales`.

Verify:
- The script output shows Engineering removed, Sales added and Engineering Tools revoked.
- The System Log shows `group.user_membership.remove` followed by `group.user_membership.add` within seconds, with no admin action in between.

## 4. Leaver

Run `python3 jml.py offboard --email ada@example.com`.

Verify:
- The script clears `department` first, so the group rules remove every rule-managed group. The user status is **DEPROVISIONED** and the Groups tab shows only Everyone. Okta keeps memberships on a deactivated user, so clearing the attribute is what actually removes access.
- The System Log shows `user.lifecycle.deactivate`, and the user has no active sessions.

## 5. Access review

Run `python3 access_review.py > access-review.csv`.

What to flag in a review:
- Any row with an app but no group. That means a direct assignment, which breaks the model.
- Contractors with access to anything beyond the Internal Portal.
- DEPROVISIONED users who still appear with groups or apps.

## 6. Tear down

Run `terraform destroy` to remove everything the lab created.
