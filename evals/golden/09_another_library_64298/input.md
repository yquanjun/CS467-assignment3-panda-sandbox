### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
repro.py:


#!/usr/bin/env python3
import io
import platform

import fastparquet
import pandas as pd

print(f"{pd.__version__=}")
print(f"{fastparquet.__version__=}")
print(f"{platform.python_version()=}")

data = {"a": {"c": 1.0}, "b": {"d": "george"}}
df = pd.DataFrame.from_dict(data)
print(repr(df))

parq = df.to_parquet(compression=None, index=True)
with open(f"{pd.__version__}-{fastparquet.__version__}.parquet", "wb") as outfile:
    outfile.write(parq)

df_read = pd.read_parquet(io.BytesIO(parq))
print(repr(df_read))


result:

+ uv pip install pandas==2.3.3
+ ./repro.py
pd.__version__='2.3.3'
fastparquet.__version__='2025.12.0'
platform.python_version()='3.12.12'
     a       b
c  1.0     NaN
d  NaN  george
         a       b
index             
c      1.0    None
d      NaN  george
+ uv pip install pandas==3.0.1
+ ./repro.py
pd.__version__='3.0.1'
fastparquet.__version__='2025.12.0'
platform.python_version()='3.12.12'
     a       b
c  1.0     NaN
d  NaN  george
         a       b
index             
None   1.0    None
None   NaN  george
+ uv pip uninstall pandas
+ uv pip install --pre --extra-index-url https://pypi.anaconda.org/scientific-python-nightly-wheels/simple pandas
+ ./repro.py
pd.__version__='3.1.0.dev0+212.g184d793fc5'
fastparquet.__version__='2025.12.0'
platform.python_version()='3.12.12'
     a       b
c  1.0     NaN
d  NaN  george
         a       b
index             
None   1.0    None
None   NaN  george
```

### Issue Description

I had commented on pandas issue 64007 but I now realize I have a *different* bug with fastparquet index corruption.

When I convert to and from parquet with pandas 2.3.3 , the index is preserved. If I do this with pandas 3.0.1, the index values are replaced with None.

The parquet files created are different only in the types associated with the columns. I'm not sure if it's parquet or pandas that causes this.  However, the syndrome is determined by the version of pandas that is installed when reading the file, not the version installed when writing it, see further example below. Given that the same version of parquet is installed in all tests, and parquet is able to read the index column of both files, I suspect somehow pandas is dropping that information after it's been read.

Testing readback of parquet files written by different versions:

readback.py:
```python
#!/usr/bin/env python3
import io
import platform
import glob

import fastparquet
import pandas as pd

print(f"{pd.__version__=}")
print(f"{fastparquet.__version__=}")
print(f"{platform.python_version()=}")

for fname in glob.glob("*.parquet"):
    print(fname)
    df_read = pd.read_parquet(fname)
    print(repr(df_read))
```

results:
```
+ uv pip install pandas==2.3.3
+ ./readback.py
pd.__version__='2.3.3'
fastparquet.__version__='2025.12.0'
platform.python_version()='3.12.12'
3.0.1-2025.12.0.parquet
         a       b
index             
c      1.0    None
d      NaN  george
2.3.3-2025.12.0.parquet
         a       b
index             
c      1.0    None
d      NaN  george
3.1.0.dev0+212.g184d793fc5-2025.12.0.parquet
         a       b
index             
c      1.0    None
d      NaN  george
+ uv pip install pandas==3.0.1
+ ./readback.py
pd.__version__='3.0.1'
fastparquet.__version__='2025.12.0'
platform.python_version()='3.12.12'
3.0.1-2025.12.0.parquet
         a       b
index             
None   1.0    None
None   NaN  george
2.3.3-2025.12.0.parquet
         a       b
index             
None   1.0    None
None   NaN  george
3.1.0.dev0+212.g184d793fc5-2025.12.0.parquet
         a       b
index             
None   1.0    None
None   NaN  george
+ uv pip uninstall pandas
+ uv pip install --pre --extra-index-url https://pypi.anaconda.org/scientific-python-nightly-wheels/simple pandas
+ ./readback.py
pd.__version__='3.1.0.dev0+212.g184d793fc5'
fastparquet.__version__='2025.12.0'
platform.python_version()='3.12.12'
3.0.1-2025.12.0.parquet
         a       b
index             
None   1.0    None
None   NaN  george
2.3.3-2025.12.0.parquet
         a       b
index             
None   1.0    None
None   NaN  george
3.1.0.dev0+212.g184d793fc5-2025.12.0.parquet
         a       b
index             
None   1.0    None
None   NaN  george
```

[repro.tgz](https://github.com/user-attachments/files/25527892/repro.tgz)

### Expected Behavior

I expect the index in the dataframe to be the same before and after the parquet serialization / deserialization as in pandas 2.3.3.



### Installed Versions

<details>

INSTALLED VERSIONS
------------------
commit                : 184d793fc54f16cf0899cbe9d0d4b2eca16c2368
python                : 3.12.12
python-bits           : 64
OS                    : Darwin
OS-release            : 24.6.0
Version               : Darwin Kernel Version 24.6.0: Wed Nov  5 21:30:23 PST 2025; root:xnu-11417.140.69.705.2~1/RELEASE_X86_64
machine               : x86_64
processor             : i386
byteorder             : little
LC_ALL                : en_US.UTF-8
LANG                  : en_US.UTF-8
LOCALE                : en_US.UTF-8

pandas                : 3.1.0.dev0+212.g184d793fc5
numpy                 : 2.4.2
dateutil              : 2.9.0.post0
pip                   : None
Cython                : None
sphinx                : None
IPython               : None
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : None
bottleneck            : None
fastparquet           : 2025.12.0
fsspec                : 2026.2.0
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : None
lxml.etree            : None
matplotlib            : None
numba                 : None
numexpr               : None
odfpy                 : None
openpyxl              : None
psycopg2              : None
pymysql               : None
pyarrow               : None
pyiceberg             : None
pyreadstat            : None
pytest                : None
python-calamine       : None
pytz                  : 2025.2
pyxlsb                : None
s3fs                  : None
scipy                 : None
sqlalchemy            : None
tables                : None
tabulate              : None
xarray                : None
xlrd                  : None
xlsxwriter            : None
zstandard             : None
qtpy                  : None
pyqt5                 : None


</details>
