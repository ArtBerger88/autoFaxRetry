# Release Prep and Post-Release Notes

## Scope
This document defines final release checks and post-release documentation upkeep tasks.

## Preconditions
- Working tree is clean or only includes intended release changes.
- Full test suite passes.
- `README.md`, `CHANGELOG.md`, and `docs/operations_runbook.md` are up to date.

## Verification checklist
- Run tests:
  - `python -m pytest -q`
- Confirm expected exit codes:
  - `python -m src.main --config config/settings.json`
- Confirm logging output is JSON and rotation files appear after size growth.
- Confirm scheduled execution settings in Windows Task Scheduler are documented and valid.

## Tagging procedure
Run from repository root.

```powershell
git status
git add README.md CHANGELOG.md docs/operations_runbook.md docs/release_prep.md docs/roadmap.md src tests
git commit -m "release: prepare <version>"
git tag -a <version> -m "Auto-Fax-Retry <version>"
git show <version>
```

## Publish procedure
```powershell
git push origin <branch-name>
git push origin <version>
```

## Suggested release notes
- Production-ready fax retry worker using Sinch Fax API.
- Structured rotating logs for operational visibility.
- CLI overrides and deterministic exit codes for scheduler integration.
- Expanded unit test coverage across API wrapper and CLI paths.

## Post-release documentation checklist
- Update `CHANGELOG.md` with new runtime controls and diagnostics.
- Update `docs/operations_runbook.md` with current tuning recommendations.
- Update `docs/architecture.md` to reflect module/data-flow changes.
- Update `docs/roadmap.md` with completed post-release hardening items.
