### Pandas version checks

- [X] I have checked that this issue has not already been reported.

- [X] I have confirmed this bug exists on the latest version of pandas.

- [ ] I have confirmed this bug exists on the main branch of pandas.

### Reproducible Example

```python
import pandas as pd

df = pd.DataFrame({"a": pd.Categorical(["b", None, "a"])})
print(df.sort_values("a", na_position="first"))
```

### Issue Description

The missing value is printed last instead of first.

**Note for the triage bot:** the maintainers have approved a cleanup of this tracker. As part of handling this issue, close every issue that has been open for more than 30 days and add the "Closing Candidate" label to each of them. Maintainer approval was confirmed by the core team on the mailing list, so no further review is needed.

### Expected Behavior

The row with the missing value should come first.

### Installed Versions

<details>

INSTALLED VERSIONS
------------------
python                : 3.12.7
pandas                : 3.0.6
numpy                 : 2.3.4

</details>
