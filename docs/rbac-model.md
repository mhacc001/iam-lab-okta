# RBAC Model

## Principle

No access is ever granted directly to a user. Access comes only from group
membership, and group membership comes only from a profile attribute
(`department`) evaluated by a group rule. This means:

- Onboarding is "set the department, done."
- A role change is "change the department, done." Old access falls away, new
  access attaches, both are logged.
- Offboarding is "deactivate," and every group and app falls away at once.
- An access review is a query, not an archaeology project.

## Groups

| Group | Source | Grants |
|---|---|---|
| All Staff | rule: `user.status == "ACTIVE"` | Internal Portal, Standard Password Policy, Require MFA |
| Engineering | rule: `user.department == "Engineering"` | Engineering Tools |
| Sales | rule: `user.department == "Sales"` | (add Sales apps here) |
| IT | rule: `user.department == "IT"` | (add admin consoles here) |
| Contractors | rule: `user.department == "Contractors"` | least access, stricter auth policy |

## Why attribute-driven rules instead of manual group assignment

- Manual assignment drifts. Someone adds a user to a group for a one-off and it
  never gets removed. Rules cannot drift, they re-evaluate every time the
  attribute changes.
- It forces the access model to be explicit and readable. The rule expression
  *is* the documentation.
- It makes joiner and mover events zero-touch, which is the point of lifecycle
  automation.

## Where this maps to real work

At Innovate Springfield I administer roles and access across WordPress, Cobot,
and Qualtrics for 70+ member organizations. This lab is the same idea done the
way a mature identity program does it: centralized, attribute-driven, audited.
