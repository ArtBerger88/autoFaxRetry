# Auto‑Fax‑Retry
Python based service thatsends a pdf to a fax number and, if the send fails, automatically retrys up to a configured amount of times.

## Features
-Auto Retry faxes up to a certain # (x) of times
-No Per day Max attempts cap
-No email or two part sending method, plain fax API only.
-Logs attempts
-Notification upon successful send

## Project structure
src/
config.py – configuration helpers
fax_api.py – wrapper for the fax provider
retry_engine.py – retry logic
main.py – example invocation
docs/ – design notes, architecture, roadmap, ect.
LICENSE
README.md