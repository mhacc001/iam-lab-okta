#!/usr/bin/env python3
"""Joiner-Mover-Leaver automation against the Okta API.

Access is driven entirely by the `department` profile attribute plus the group
rules created in Terraform. These commands set that attribute and the account
state, then report which groups (and therefore which apps) changed.

Env:
  OKTA_ORG_URL    e.g. https://dev-12345.okta.com
  OKTA_API_TOKEN  API token
"""
import argparse
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import json

ORG = os.environ.get("OKTA_ORG_URL", "").rstrip("/")
TOKEN = os.environ.get("OKTA_API_TOKEN", "")

if not ORG or not TOKEN:
    sys.exit("set OKTA_ORG_URL and OKTA_API_TOKEN")


def api(method, path, body=None):
    url = f"{ORG}/api/v1{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"SSWS {TOKEN}")
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code} {e.read().decode()}")


def find_user(email):
    res = api("GET", f"/users/{urllib.parse.quote(email)}")
    return res


def groups_for(user_id):
    return {g["profile"]["name"] for g in api("GET", f"/users/{user_id}/groups")}


def apps_for(user_id):
    # Apps the user is assigned to (directly or through a group). appLinks only
    # lists dashboard tiles, which are empty for users who have not signed in yet.
    flt = urllib.parse.quote(f'user.id eq "{user_id}"')
    return {a["label"] for a in api("GET", f"/apps?filter={flt}")}


def wait_for_rules():
    # group rules evaluate asynchronously
    time.sleep(8)


def onboard(args):
    body = {
        "profile": {
            "firstName": args.first,
            "lastName": args.last,
            "email": args.email,
            "login": args.email,
            "department": args.dept,
        }
    }
    user = api("POST", "/users?activate=true", body)
    uid = user["id"]
    print(f"[joiner] created {args.email} id={uid} department={args.dept}")
    wait_for_rules()
    print(f"[joiner] groups now: {sorted(groups_for(uid))}")
    print(f"[joiner] app access: {sorted(apps_for(uid))}")


def move(args):
    user = find_user(args.email)
    uid = user["id"]
    before_g = groups_for(uid)
    before_a = apps_for(uid)
    old_dept = user["profile"].get("department")
    api("POST", f"/users/{uid}", {"profile": {"department": args.new_dept}})
    print(f"[mover] {args.email}: {old_dept} -> {args.new_dept}")
    wait_for_rules()
    after_g = groups_for(uid)
    after_a = apps_for(uid)
    print(f"[mover] groups added:   {sorted(after_g - before_g)}")
    print(f"[mover] groups removed: {sorted(before_g - after_g)}")
    print(f"[mover] apps added:     {sorted(after_a - before_a)}")
    print(f"[mover] apps removed:   {sorted(before_a - after_a)}")


def offboard(args):
    user = find_user(args.email)
    uid = user["id"]
    had_g = groups_for(uid)
    had_a = apps_for(uid)
    # Okta keeps group memberships on a deactivated user. Clearing the
    # department first makes the group rules drop every rule-managed group
    # (and the apps that come with them) before the account is deactivated.
    api("POST", f"/users/{uid}", {"profile": {"department": None}})
    wait_for_rules()
    api("POST", f"/users/{uid}/lifecycle/deactivate", None)
    # clear any live sessions
    try:
        api("DELETE", f"/users/{uid}/sessions", None)
    except SystemExit:
        pass
    left_g = groups_for(uid)
    left_a = apps_for(uid)
    print(f"[leaver] department cleared, then deactivated {args.email}")
    print(f"[leaver] groups removed:    {sorted(had_g - left_g)}")
    print(f"[leaver] apps revoked:      {sorted(had_a - left_a)}")
    print(f"[leaver] groups remaining:  {sorted(left_g)}  (Everyone is built in and cannot be removed)")
    print(f"[leaver] apps remaining:    {sorted(left_a)}")
    print(f"[leaver] audit: user retained in DEPROVISIONED state for review")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("onboard")
    j.add_argument("--first", required=True)
    j.add_argument("--last", required=True)
    j.add_argument("--dept", required=True)
    j.add_argument("--email", required=True)
    j.set_defaults(func=onboard)

    m = sub.add_parser("move")
    m.add_argument("--email", required=True)
    m.add_argument("--new-dept", required=True, dest="new_dept")
    m.set_defaults(func=move)

    o = sub.add_parser("offboard")
    o.add_argument("--email", required=True)
    o.set_defaults(func=offboard)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
