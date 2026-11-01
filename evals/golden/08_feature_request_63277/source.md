# 08_feature_request_63277

- Upstream: pandas issue 63277 (plain text on purpose: no links in issues)
- Opened: 2025-12-05T18:09:48Z; reporter association: NONE
- Original title: BUG: `pd.col` Not Supported in `.loc` for Series
- Current title: ENH: Support `pd.col` in `.loc` for Series (renamed)
- Body: edited 1 time(s): earliest of 2 revisions used
- Labels at opening (form): Bug, Needs Triage
- Labels added later by others: 2025-12-05 Enhancement; 2025-12-05 Needs Discussion; 2025-12-05 expressions
- Labels now: Enhancement, Needs Discussion, expressions
- State now: OPEN

## Maintainer responses (evidence for expected.yaml)

**2025-12-05, member:**

> I do not think I necessarily agree with the expectation. A DataFrame has columns, a Series does not, and from a very abstract perspective, it seems odd to perform column selection on a Series. But I do see there is value in using expressions in `Series.loc`.
> 
> Two other things to note: Polars also does not support this, and I think the implementation would not be very straightforward (but I haven't taken an in-depth look).
> 
> In any case, there was never any intention in pandas 3.0 for this to work, relabeling this as an enhancement request.
> 
> cc MarcoGorelli

**2025-12-05, member:**

> Another option would be `pd.self()`

**2025-12-05, member:**

> Can you elaborate on why the -1?

**2025-12-09, member:**

> My gut reaction is that pd.col() with no arguments looks nice
