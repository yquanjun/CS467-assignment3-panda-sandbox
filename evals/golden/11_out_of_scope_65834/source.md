# 11_out_of_scope_65834

- Upstream: pandas issue 65834 (plain text on purpose: no links in issues)
- Opened: 2026-06-09T15:28:35Z; reporter association: NONE
- Original title: BUILD: pip install fails with build error
- Current title: BUILD: pip install fails with build error (unchanged)
- Body: edited 2 time(s): earliest of 3 revisions used
- Labels at opening (form): Build, Needs Triage
- Labels added later by others: none
- Labels now: Build
- State now: CLOSED (COMPLETED)

## Maintainer responses (evidence for expected.yaml)

**2026-06-09, member:**

> Is there a specific reason you are installing pandas from source? (instead of installing a binary wheel) 
> And are you installing inside a (virtual) environment?
> 
> That said, I think you are running into a Meson issue with their latest release: https://github.com/mesonbuild/meson/issues/15740
> 
> The workaround is to set `PKG_CONFIG_PATH` env variable

Closed 2026-06-09 (COMPLETED).
