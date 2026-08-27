# Authentication Policy Rationale

## Baseline: MFA required for All Staff

- Password + at least one strong factor (Okta Verify push or email OTP in the
  lab; in production you would drop email as a factor).
- Enrollment is REQUIRED, not OPTIONAL, so a user cannot sit unprotected.
- Rationale: credential theft (phishing, reuse, stuffing) is the most common
  initial access vector. MFA is the single highest-leverage control against it.

## Stricter for Contractors

Contractors get a separate, tighter policy:
- Phishing-resistant factor only (FIDO2/WebAuthn) where possible
- Shorter session lifetime, re-auth on every new app
- No "remember this device"

Rationale: third parties are outside your device management and monitoring, and
contractor accounts are a repeated source of breaches. Higher assurance, less
convenience, is the right trade for that population.

## Password policy

- 12 character minimum
- History of 8 (cannot reuse recent passwords)
- Lockout after 5 failed attempts, email notification on lockout

Rationale: length beats complexity rules for resistance to guessing, history
stops rotation gaming, lockout slows online brute force without being so
aggressive it becomes a self-inflicted denial of service.

## What production would add

- Device trust / managed-device signal in the policy
- Risk-based step-up (impossible travel, new device, anomalous behavior)
- Number matching / passkeys to kill MFA-fatigue push bombing
