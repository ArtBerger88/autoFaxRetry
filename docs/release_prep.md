# Release Prep (v1.0.0)

## Scope
This document defines the final checks and exact command sequence for releasing v1.0.0.

## Preconditions
- Working tree is clean or only includes intended release changes.
- Full test suite passes.
- `README.md`, `CHANGELOG.md`, and `docs/operations_runbook.md` are up to date.

## Verification checklist
- Run tests:
  - `c:/Users/artyz/ProjectFile/Auto-fax-retry/autoFaxRetry/.venv/Scripts/python.exe -m pytest -q`
- Confirm expected exit codes:
  - `python -m src.main --config config/settings.json`
- Confirm logging output is JSON and rotation files appear after size growth.
- Confirm scheduled execution settings in Windows Task Scheduler are documented and valid.

## Tagging procedure
Run from repository root.

```powershell
git status
git add README.md CHANGELOG.md docs/operations_runbook.md docs/release_prep.md docs/roadmap.md src tests
git commit -m "release: prepare v1.0.0"
git tag -a v1.0.0 -m "Auto-Fax-Retry v1.0.0"
git show v1.0.0
```

## Publish procedure
```powershell
git push origin <branch-name>
git push origin v1.0.0
```

## Suggested release notes
- Production-ready fax retry worker using Phaxio.
- Structured rotating logs for operational visibility.
- CLI overrides and deterministic exit codes for scheduler integration.
- Expanded unit test coverage across API wrapper and CLI paths.
