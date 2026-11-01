### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

print("pandas", pd.__version__)
print("matplotlib", matplotlib.__version__)

df = pd.DataFrame({
    "a": [1, 2, 3, 4],
    "b": [1, 2, 3, 4],
    "c": [1, 1, 1, 1],
    })

# This plot works
df.plot(
   kind='bar',
   stacked=True,
   subplots=[
       ['b', 'c'],
       ['a'],
       ],
   sharex=True,
   )
plt.show()

# This produces ``IndexError: list index out of range``
df.plot(
   kind='bar',
   stacked=True,
   subplots=[
       ['a'],
       ['b', 'c'],
       ],
   sharex=True,
   )
plt.show()

# Create the desired output the manual way:
fig, ax = plt.subplots(2, sharex=True)
df[["a"]].plot.bar(ax=ax[0], stacked=True)
df[["b", "c"]].plot.bar(ax=ax[1], stacked=True)
plt.suptitle(f"pd {pd.__version__}, mpl {matplotlib.__version__}: Desired output with stacked=True")
plt.show()
```

### Issue Description

This is one part of splitting pandas issue 67040 into separate issues.

When using barplots with ``stacked=True`` and automated subplot arrangement, I found that certain orders of the subplots worked, while others cause an ``IndexError``.

The plot with 
```python
subplots=[
       ['a'],
       ['b', 'c'],
       ],
```
produces the following exception:

```
Traceback (most recent call last):
  File "**\pandas_bar_subplots.py", line 43, in <module>
    df.plot(
    ~~~~~~~^
       kind='bar',
       ^^^^^^^^^^^
    ...<5 lines>...
       sharex=True,
       ^^^^^^^^^^^^
       )
       ^
  File "C:\Users\**\miniconda3\envs\work11\Lib\site-packages\pandas\plotting\_core.py", line 1185, in __call__
    return plot_backend.plot(data, kind=kind, **kwargs)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\**\miniconda3\envs\work11\Lib\site-packages\pandas\plotting\_matplotlib\__init__.py", line 71, in plot
    plot_obj.generate()
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Users\**\miniconda3\envs\work11\Lib\site-packages\pandas\plotting\_matplotlib\core.py", line 518, in generate
    self._make_plot(fig)
    ~~~~~~~~~~~~~~~^^^^^
  File "C:\Users\**\miniconda3\envs\work11\Lib\site-packages\pandas\plotting\_matplotlib\core.py", line 1982, in _make_plot
    pos_prior, neg_prior = _stacked_subplots_offsets[offset_index]
                           ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
IndexError: list index out of range
```

### Expected Behavior

Desired result (except for the colors):

<img width="725" height="556" alt="Image" src="https://github.com/user-attachments/assets/4ddbf018-df23-4fd9-b7ac-5f6d0921589b" />

### Installed Versions

<details>

INSTALLED VERSIONS
------------------
commit                : e68db09ecf6427d1b62e565bacf17f2e525a3032
python                : 3.13.15
python-bits           : 64
OS                    : Windows
OS-release            : 11
Version               : 10.0.26200
machine               : AMD64
processor             : Intel64 Family 6 Model 158 Stepping 10, GenuineIntel
byteorder             : little
LC_ALL                : None
LANG                  : en
LOCALE                : de_DE.cp1252

pandas                : 3.0.5
numpy                 : 2.5.2
dateutil              : 2.9.0.post0
pip                   : 26.2.1
Cython                : None
sphinx                : None
IPython               : 9.16.1
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : 4.15.0
bottleneck            : None
fastparquet           : None
fsspec                : None
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : 3.1.6
lxml.etree            : 6.1.1
matplotlib            : 3.11.1
numba                 : 0.67.0
numexpr               : None
odfpy                 : None
openpyxl              : 3.1.5
psycopg2              : None
pymysql               : None
pyarrow               : None
pyiceberg             : None
pyreadstat            : None
pytest                : None
python-calamine       : None
pytz                  : None
pyxlsb                : None
s3fs                  : None
scipy                 : 1.16.3
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
