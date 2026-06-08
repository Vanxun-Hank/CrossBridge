"""One-button deploy console (port 8090).

A tiny internal page at ``/deploy/`` that lets a teammate trigger a deploy from the
browser — no SSH, no server key. Clicking the button runs the fixed
``deploy/server-update.sh`` on the server and streams its log back live.

Protected in production by the site's existing nginx HTTP Basic Auth + the cloud
firewall IP allowlist. The endpoint runs ONE fixed script with no parameters (no
command injection surface). Demo-grade: tighten sudo + add per-user auth/audit
before any real use.
"""
