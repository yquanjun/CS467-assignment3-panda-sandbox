# 07_usage_question_63271

- Upstream: pandas issue 63271 (plain text on purpose: no links in issues)
- Opened: 2025-12-05T09:31:31Z; reporter association: NONE
- Original title: BUG: Unexpected behavious in .loc method when looking for "None" values
- Current title: BUG: Unexpected behaviour in .loc method when looking for "None" values (renamed)
- Body: never edited: current body used
- Labels at opening (form): Bug, Needs Triage
- Labels added later by others: 2025-12-05 PDEP missing values; 2025-12-05 API Design
- Labels now: API Design, PDEP missing values
- State now: OPEN

## Maintainer responses (evidence for expected.yaml)

**2025-12-05, member:**

> Thanks for the report. pandas treats `None` as an NA value in object dtype, and its behavior is similar to that of NaN - `None == [any value]` gives False (including `None`). Use `isna()` instead: `df1.loc[df1["C"].isna()]`.
> 
> I do think special casing `None` like this is something we should eventually get away from, but I'm not sure if it would be a part of the missing values PDEP. cc jorisvandenbossche

**2025-12-05, member:**

> That's indeed something we should consider while (or after) moving to NA-based dtypes. 
> 
> I assume we will keep supporting `None` for user input to be coerced to NA, like `pd.Series([1, 2, None])` (although this can also certainly be discussed), but then the question is how the value behaves in such other places ..

**2025-12-05, member:**

> My ideal path would be to only have `pd.NA` as a dtype-independent NA value and treat all others as the object they are: `None` exactly as the Python object it is and `np.nan` is a float. This would only be well after nullable dtypes are the default.
> 
> While I understand this would be a lot of churn, pandas current handling of `None` can be very hard to work around for users who actually want `None` in their data and to use it like the Python `None`.

**2025-12-11, member:**

> pandas treats `None` as an NA value in object dtype columns. Given this, to not have the behavior you demonstrated would be inconsistent. If you do not desire this behavior, you need to avoid putting `None` values into object dtype.
> 
> As mentioned above, I desire to move away from this, but that is years off.
