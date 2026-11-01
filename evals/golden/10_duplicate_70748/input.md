### Pandas version checks

- [x] I have checked that this issue has not already been reported.
- [x] I have confirmed this bug exists on the latest version of pandas (3.0.1).
- [x] I have confirmed this bug exists on the main branch of pandas (the relevant code in `pandas/core/methods/describe.py` is unchanged on main).

### Reproducible Example

```python
import pandas as pd
import pint_pandas  # registers the "pint[...]" ExtensionDtype

s = pd.Series([1.0, 2.0, 3.0], dtype="pint[m]")
s.describe()
```

```
pint.errors.DimensionalityError: Cannot convert from 'meter' to 'dimensionless'

The above exception was the direct cause of the following exception:
...
  File ".../pandas/core/methods/describe.py", line 267, in describe_numeric_1d
    return Series(d, index=stat_index, name=series.name, dtype=dtype)
  ...
  File ".../pandas/core/arrays/numeric.py", line 164, in _coerce_to_data_and_mask
    values = np.asarray(values)
ValueError: setting an array element with a sequence.
```

`DataFrame.describe()` fails the same way for any frame with a pint column.

### Issue Description

`describe_numeric_1d` collects `[count, mean, std, min, *quantiles, max]` and then forces the result dtype. Every non-Arrow `ExtensionDtype` gets `Float64Dtype()` (added for pandas issue 48340 / pandas issue 48778):

```python
if isinstance(series.dtype, ExtensionDtype):
    if isinstance(series.dtype, ArrowDtype):
        ...
    else:
        dtype = Float64Dtype()
```

That fits the masked numeric dtypes (`Int64`, `Float32`, …). It doesn't fit third-party numeric EAs whose reductions return non-float scalars. For pint-pandas, `mean`, `std`, `min` and so on return `pint.Quantity` objects, and `count` is a plain int. pint refuses to convert a Quantity with units to a bare float, so `describe()` raises. Stripping the units to make the cast succeed would silently lose information.

pandas already has a carve-out for the same situation: Arrow timedeltas use `dtype=None` and so get object output (pandas issue 53001).

### Expected Behavior

`describe()` should return a result instead of raising. For example, with `dtype=None` in `describe_numeric_1d` the result would be:

```
count            3
mean     2.0 meter
std      1.0 meter
min      1.0 meter
25%      1.5 meter
50%      2.0 meter
75%      2.5 meter
max      3.0 meter
dtype: object
```

Possible fixes:

1. Use `Float64Dtype()` only for `BaseMaskedDtype`, and `dtype=None` (inference, so object here) for other extension dtypes.
2. Try `Float64Dtype()` and fall back to `dtype=None` if the cast fails.
3. Let the dtype choose: add an `ExtensionDtype` hook for the describe result dtype, defaulting to option 1's behaviour.

I'm happy to open a PR for option 1 (or whichever approach is preferred).

### Installed Versions

<details>

```
INSTALLED VERSIONS
------------------
commit                : e04b26f375035e5106cb913e47b6db612f4ebb11
python                : 3.13.5
python-bits           : 64
OS                    : Windows
OS-release            : 10
Version               : 10.0.19045
machine               : AMD64
byteorder             : little
LOCALE                : English_United Kingdom.1252

pandas                : 3.0.1
numpy                 : 2.4.2
dateutil              : 2.9.0.post0
pyarrow               : 23.0.1
pint                  : 0.25.2
pint-pandas           : 0.8.1.dev1+gfc51c5a3e
```

</details>
