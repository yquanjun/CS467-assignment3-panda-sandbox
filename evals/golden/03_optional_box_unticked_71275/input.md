### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [ ] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.

### Reproducible Example

```python
import os
import tempfile

import pandas as pd

N = 60_000
PAD = "x" * 20

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "rows.xml")
    with open(path, "w") as f:
        f.write("<data>\n")
        for i in range(N):
            f.write(f"<row><a>v{i}{PAD}</a><a>w{i}{PAD}</a></row>\n")
        f.write("</data>\n")
    print("file size:", os.path.getsize(path), "bytes,", N, "rows")

    for parser in ["lxml", "etree"]:
        df = pd.read_xml(
            path,
            parser=parser,
            iterparse={"row": ["a", "a"]},
            names=["a1", "a2"],
        )
        expected = pd.DataFrame(
            {
                "a1": [f"v{i}{PAD}" for i in range(N)],
                "a2": [f"w{i}{PAD}" for i in range(N)],
            }
        )
        bad = (df["a1"] != expected["a1"]) | (df["a2"] != expected["a2"])
        print(f"parser={parser}: {int(bad.sum())} of {N} rows wrong (expected 0)")
        for idx in bad[bad].index[:2]:
            print(
                f"  row {idx}: got {df.loc[idx].to_dict()}, "
                f"expected {expected.loc[idx].to_dict()}"
            )
```

### Issue Description

When the `iterparse` list repeats a child name, as in `iterparse={"row": ["a", "a"]}`, `read_xml` on a file of a few MB returns some rows where the first value is NaN and the real first value sits in the second column, and other rows where the second value is NaN. There is no warning. Tiny documents read correctly, and a names list without repeats reads the same file correctly.

Output on 3.0.6:

```
file size: 4657795 bytes, 60000 rows
parser=lxml: 100 of 60000 rows wrong (expected 0)
  row 445: got {'a1': 'v445xxxxxxxxxxxxxxxxxxxx', 'a2': nan}, expected {'a1': 'v445xxxxxxxxxxxxxxxxxxxx', 'a2': 'w445xxxxxxxxxxxxxxxxxxxx'}
  row 1322: got {'a1': 'v1322xxxxxxxxxxxxxxxxxxxx', 'a2': nan}, expected {'a1': 'v1322xxxxxxxxxxxxxxxxxxxx', 'a2': 'w1322xxxxxxxxxxxxxxxxxxxx'}
parser=etree: 217 of 60000 rows wrong (expected 0)
  row 224: got {'a1': nan, 'a2': 'v224xxxxxxxxxxxxxxxxxxxx'}, expected {'a1': 'v224xxxxxxxxxxxxxxxxxxxx', 'a2': 'w224xxxxxxxxxxxxxxxxxxxx'}
  row 445: got {'a1': 'v445xxxxxxxxxxxxxxxxxxxx', 'a2': nan}, expected {'a1': 'v445xxxxxxxxxxxxxxxxxxxx', 'a2': 'w445xxxxxxxxxxxxxxxxxxxx'}
```

The number of wrong rows changes with the row width, since it depends on where the parser's buffer boundaries fall.

The cause is the repeated-names branch of `_iterparse_nodes` in `pandas/io/xml.py` (lines 354-369 at 03e5d938ad, added in pandas issue 51355 for 2.0.0). It runs on both the `"start"` and `"end"` events and stores `elem.text` under the first name that is not in the row yet. Both lxml and the stdlib `iterparse` can emit `"start"` before the element's text has been read when that text lies past the current buffer, so `elem.text` is `None` at that point. The `None` claims the first name, and the real text that arrives on `"end"` is then stored under the next name. The branch without repeats (370-375) overwrites on `"end"`, which is why it is not affected. `test_repeat_names` and `test_repeat_elements` only use small in-buffer documents.

A fix would read element text only on `"end"` events (attributes can stay on `"start"`), plus a test with a document larger than the parser buffer.

I ran this on pandas 3.0.6. I have not run it on a main build, but the code cited above is unchanged on main at 03e5d938ad.

### Expected Behavior

Every row reads back as `a1 = "v<i>..."` and `a2 = "w<i>..."`, with 0 wrong rows for both parsers, the same as the xpath path and the non-repeating `iterparse` path give.

### Installed Versions

<details>

```

INSTALLED VERSIONS
------------------
commit                : 2905718b126579d2cf0fe5bae05bd75facb67d77
python                : 3.12.3
python-bits           : 64
OS                    : Linux
OS-release            : 7.1.5-76070105-generic
Version               : #202607241434~1787955023~24.04~38a419f SMP PREEMPT_DYNAMIC Fri A
machine               : x86_64
processor             : x86_64
byteorder             : little
LC_ALL                : None
LANG                  : en_US.UTF-8
LOCALE                : en_US.UTF-8

pandas                : 3.0.6
numpy                 : 2.5.4
dateutil              : 2.9.0.post0
pip                   : None
Cython                : None
sphinx                : None
IPython               : None
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : None
bottleneck            : None
fastparquet           : None
fsspec                : None
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : 3.1.6
lxml.etree            : 6.1.3
matplotlib            : None
numba                 : None
numexpr               : 2.14.2
odfpy                 : None
openpyxl              : None
psycopg2              : None
pymysql               : None
pyarrow               : 26.0.0
pyiceberg             : None
pyreadstat            : None
pytest                : None
python-calamine       : None
pytz                  : None
pyxlsb                : None
s3fs                  : None
scipy                 : None
sqlalchemy            : 2.1.5
tables                : 3.11.1
tabulate              : None
xarray                : None
xlrd                  : None
xlsxwriter            : None
zstandard             : None
qtpy                  : None
pyqt5                 : None
```

</details>

I'm happy to open a PR with the fix and a test.
