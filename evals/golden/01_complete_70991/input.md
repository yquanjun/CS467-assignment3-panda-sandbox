### Pandas version checks

- [x] I have checked that this issue has not already been reported.
- [x] I have confirmed this bug exists on the latest version of pandas.
- [x] I have confirmed this bug exists on the main branch of pandas.

### Reproducible Example

```python
import pandas as pd

data = ["a\x0bb", "a\x1cb", "a b"]
ser = pd.Series(data, dtype="str")
obj = pd.Series(data, dtype=object)

print(ser.str.contains(r"\s").tolist())
# [False, False, True]
print(obj.str.contains(r"\s").tolist())
# [True, True, True]

print(ser.str.count(r"\s").tolist())
# [0, 0, 1]
print(obj.str.count(r"\s").tolist())
# [1, 1, 1]
```

### Issue Description

For the pyarrow-backed string dtypes, regex methods run through RE2, where `\s` is only `[\t\n\f\r ]`. Python's `re`, used for `object` dtype and the python string storage, also treats `\x0b` and `\x1c`-`\x1f` as whitespace, along with Unicode spaces like `\x85`, `\xa0` and `　`. So `\s` and `\S` give different results depending on the dtype

The non-ASCII cases are handled by pandas issue 70773, which falls back to Python's `re` when the data isn't all ASCII. The ASCII control characters above still take the pyarrow path. Scanning the data for them on every `\s` call would roughly double the cost of `contains` on plain ASCII data, so the fix likely needs either that tradeoff or rewriting `\s` to an explicit class before handing the pattern to RE2. Raised in review of pandas issue 70773

### Expected Behavior

`ser.str.contains(r"\s")` returns `[True, True, True]`, matching `object` dtype

### Installed Versions

pandas 3.2.0.dev0+131.g48f2692dd9 (nightly), pyarrow 26.0.0.dev363
