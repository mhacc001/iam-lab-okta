#!/usr/bin/env python3
"""Export a who-has-access-to-what report for a quarterly access review.

Prints CSV: user_email, user_status, group, app.
Redirect to a file and attach it to the review record.

Env: OKTA_ORG_URL, OKTA_API_TOKEN
"""
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

ORG = os.environ.get("OKTA_ORG_URL", "").rstrip("/")
TOKEN = os.environ.get("OKTA_API_TOKEN", "")
if not ORG or not TOKEN:
    sys.exit("set OKTA_ORG_URL and OKTA_API_TOKEN")


def api(path):
    results = []
    url = f"{ORG}/api/v1{path}"
    while url:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"SSWS {TOKEN}")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req) as r:
                results.extend(json.loads(r.read()))
                link = r.headers.get("link", "")
        except urllib.error.HTTPError as e:
            sys.exit(f"{path} -> {e.code} {e.read().decode()}")
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1:part.find(">")]
    return results


def main():
    w = csv.writer(sys.stdout)
    w.writerow(["user_email", "user_status", "group", "app"])
    for u in api("/users?limit=200"):
        uid = u["id"]
        email = u["profile"].get("email", "")
        status = u["status"]
        groups = [g["profile"]["name"] for g in api(f"/users/{uid}/groups")]
        flt = urllib.parse.quote(f'user.id eq "{uid}"')
        apps = [a["label"] for a in api(f"/apps?filter={flt}")]
        if not groups and not apps:
            w.writerow([email, status, "", ""])
        for g in groups:
            w.writerow([email, status, g, ""])
        for a in apps:
            w.writerow([email, status, "", a])


if __name__ == "__main__":
    main()
