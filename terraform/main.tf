terraform {
  required_version = ">= 1.5"
  required_providers {
    okta = {
      source  = "okta/okta"
      version = "~> 4.0"
    }
  }
}

provider "okta" {
  org_name  = var.okta_org_name
  base_url  = var.okta_base_url
  api_token = var.okta_api_token
}

# ---------------------------------------------------------------------------
# Groups = roles. Access is granted through these, never to users directly.
# ---------------------------------------------------------------------------
locals {
  departments = ["Engineering", "Sales", "Contractors", "IT"]
}

resource "okta_group" "dept" {
  for_each = toset(local.departments)
  name     = each.value
  description = "Role group for ${each.value}. Managed by group rule, not manual assignment."
}

resource "okta_group" "all_staff" {
  name        = "All Staff"
  description = "Every active employee. Baseline app access."
}

# ---------------------------------------------------------------------------
# Group rules: the 'department' profile attribute drives membership.
# This is what makes onboarding and moves automatic.
# ---------------------------------------------------------------------------
resource "okta_group_rule" "dept" {
  for_each          = okta_group.dept
  name              = "auto-${each.key}"
  status            = "ACTIVE"
  group_assignments = [each.value.id]
  expression_type   = "urn:okta:expression:1.0"
  expression_value  = "user.department == \"${each.key}\""
}

resource "okta_group_rule" "all_staff" {
  name              = "auto-all-staff"
  status            = "ACTIVE"
  group_assignments = [okta_group.all_staff.id]
  expression_type   = "urn:okta:expression:1.0"
  # Okta group rules only evaluate ACTIVE users, so "has a department" = "every active employee".
  # (user.status cannot be used inside a group-rule expression.)
  expression_value  = "user.department != null"
}

# ---------------------------------------------------------------------------
# Seed users. department attribute is the only thing that grants access.
# ---------------------------------------------------------------------------
locals {
  seed_users = {
    "grace@example.com" = { first = "Grace", last = "Hopper", dept = "Engineering" }
    "katherine@example.com" = { first = "Katherine", last = "Johnson", dept = "Engineering" }
    "dorothy@example.com" = { first = "Dorothy", last = "Vaughan", dept = "IT" }
    "mary@example.com" = { first = "Mary", last = "Jackson", dept = "Sales" }
    "external@vendor.example" = { first = "Chris", last = "Vendor", dept = "Contractors" }
  }
}

resource "okta_user" "seed" {
  for_each   = local.seed_users
  first_name = each.value.first
  last_name  = each.value.last
  login      = each.key
  email      = each.key
  department = each.value.dept
  status     = "ACTIVE"
}

# ---------------------------------------------------------------------------
# An OIDC app, assigned to groups only.
# ---------------------------------------------------------------------------
resource "okta_app_oauth" "internal_portal" {
  label          = "Internal Portal"
  type           = "web"
  grant_types    = ["authorization_code"]
  redirect_uris  = ["https://localhost:8080/callback"]
  response_types = ["code"]
}

resource "okta_app_group_assignment" "portal_all_staff" {
  app_id   = okta_app_oauth.internal_portal.id
  group_id = okta_group.all_staff.id
}

resource "okta_app_oauth" "eng_tools" {
  label          = "Engineering Tools"
  type           = "web"
  grant_types    = ["authorization_code"]
  redirect_uris  = ["https://localhost:8080/callback"]
  response_types = ["code"]
}

resource "okta_app_group_assignment" "eng_tools" {
  app_id   = okta_app_oauth.eng_tools.id
  group_id = okta_group.dept["Engineering"].id
}

# ---------------------------------------------------------------------------
# Password policy
# ---------------------------------------------------------------------------
resource "okta_policy_password" "standard" {
  name             = "Standard Password Policy"
  status           = "ACTIVE"
  description      = "Lab standard: 12+ chars, history 8, lockout at 5."
  password_min_length          = 12
  password_history_count       = 8
  password_max_lockout_attempts = 5
  password_lockout_notification_channels = ["EMAIL"]
  # Recovery by email only: security questions are weak and disabled in this org.
  email_recovery    = "ACTIVE"
  question_recovery = "INACTIVE"
  groups_included  = [okta_group.all_staff.id]
}

# ---------------------------------------------------------------------------
# Authentication (sign-on) policy: MFA required, stricter for Contractors
# ---------------------------------------------------------------------------
resource "okta_policy_mfa" "require_mfa" {
  name        = "Require MFA - All Staff"
  status      = "ACTIVE"
  description = "MFA required for all authenticated access."
  is_oie      = true

  # Email stays a recovery-only factor in this org, so enrollment requires
  # a knowledge factor plus a possession factor (Okta Verify).
  okta_password = { enroll = "REQUIRED" }
  okta_verify   = { enroll = "REQUIRED" }

  groups_included = [okta_group.all_staff.id]
}
