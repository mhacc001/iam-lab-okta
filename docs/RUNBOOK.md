# Runbook — fill this in as you build

The portfolio value of this project is the evidence here, not the code.

## 1. Setup done

- [ ] Okta developer org created: `dev-_____.okta.com`
- [ ] `terraform apply` succeeded
- [ ] Screenshot: Directory > Groups showing the 5 groups
- [ ] Screenshot: Directory > Group Rules showing the ACTIVE rules

## 2. Joiner

- [ ] Ran `jml.py onboard` for a test user
- [ ] Paste the script output here:
  ```
  ```
- [ ] Screenshot: the new user's Groups tab
- [ ] Screenshot: System Log filtered to that user, showing membership adds

## 3. Mover

- [ ] Ran `jml.py move` to change department
- [ ] Paste the added/removed diff:
  ```
  ```
- [ ] Screenshot: System Log showing membership remove then add, seconds apart

## 4. Leaver

- [ ] Ran `jml.py offboard`
- [ ] Paste output:
  ```
  ```
- [ ] Screenshot: user in DEPROVISIONED state, Groups tab empty

## 5. Access review

- [ ] Ran `access_review.py`, saved CSV to `docs/access-review-YYYYMMDD.csv`
- [ ] One paragraph: what you would flag in this review and why

## 6. Reflection (interview prep)

- What broke or surprised you:
- What you would do differently in production:
- The 60-second version of this project you can say out loud:
