### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
import pandas as pd

df1 = pd.DataFrame(data={"A": [0, 1, 2, 3, 4],
			 "B": ["a", "b", "c", "d", "e"],
			 "C": ["some text", None, None, "some text", None]})

print(df1.loc[df1["A"] == 3])

print(df1.loc[df1["C"] == None]) # Return an empty DataFrame...

print(df1.at[2, "C"] == None) # While comparing individually the values returns True...
```

### Issue Description

The .loc method does not seem to behave consistently when working with "None" value.

### Expected Behavior

I would expect pandas to return all the rows from df1 where the value of C column is None.

### Installed Versions

<details>

INSTALLED VERSIONS
------------------
commit                : 9c8bc3e55188c8aff37207a74f1dd144980b8874
python                : 3.14.0
python-bits           : 64
OS                    : Windows
OS-release            : 10
Version               : 10.0.19045
machine               : AMD64
processor             : Intel64 Family 6 Model 186 Stepping 2, GenuineIntel
byteorder             : little
LC_ALL                : None
LANG                  : None
LOCALE                : fr_FR.cp1252
pandas                : 2.3.3
numpy                 : 2.3.4
pytz                  : 2025.2
dateutil              : 2.9.0.post0
pip                   : 25.2
Cython                : None
sphinx                : None
IPython               : 9.6.0
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : 4.14.2
blosc                 : None
bottleneck            : None
dataframe-api-compat  : None
fastparquet           : None
fsspec                : None
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : 3.1.6
lxml.etree            : 6.0.2
matplotlib            : 3.10.7
numba                 : None
numexpr               : None
odfpy                 : None
openpyxl              : None
pandas_gbq            : None
psycopg2              : None
pymysql               : None
pyarrow               : None
pyreadstat            : None
pytest                : None
python-calamine       : None
pyxlsb                : None
s3fs                  : None
scipy                 : 1.16.2
sqlalchemy            : 2.0.44
tables                : None
tabulate              : None
xarray                : None
xlrd                  : None
xlsxwriter            : 3.2.9
zstandard             : None
tzdata                : 2025.2
qtpy                  : None
pyqt5                 : None

</details>
