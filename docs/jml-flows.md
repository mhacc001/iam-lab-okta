# Joiner / Mover / Leaver Flows

## Joiner

1. HR system (here: `jml.py onboard`) creates the Okta user with `department` set.
2. `auto-all-staff` rule adds them to All Staff -> Internal Portal, password
   policy, MFA policy apply.
3. `auto-<dept>` rule adds them to their department group -> department apps
   apply.
4. Activation email sent. User enrolls MFA on first sign-in (policy = REQUIRED).

Evidence to capture: Okta System Log events `user.lifecycle.create`,
`user.account.update_profile`, `group.user_membership.add`.

## Mover

1. `jml.py move --new-dept` changes the `department` attribute.
2. Old `auto-<dept>` rule no longer matches -> user removed from old group ->
   old department apps removed.
3. New `auto-<dept>` rule matches -> new group -> new apps.
4. All Staff membership is unaffected (still ACTIVE), so baseline access is
   continuous.

The script prints the exact added/removed groups and apps. That diff is the
access-change record.

Evidence to capture: the script output, plus System Log
`group.user_membership.add` and `.remove` within seconds of the profile update.

## Leaver

1. `jml.py offboard` deactivates the user.
2. Deactivation removes all group memberships and app assignments in one step.
3. Active sessions are explicitly deleted so existing tokens cannot be reused.
4. User is left in DEPROVISIONED state, not deleted, so the access history
   survives for audit. A separate retention job deletes after N days.

Evidence to capture: System Log `user.lifecycle.deactivate`,
`user.session.end`, and a final access-review export showing the user with no
group or app rows.

## Gaps a real program would close that this lab does not

- No HR system of record driving it (this is manual via the CLI)
- No SoD (segregation of duties) checks on the mover path
- No manager attestation step in the access review
- No privileged-access just-in-time elevation
