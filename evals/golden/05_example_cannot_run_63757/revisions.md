# Revisions of pandas issue 63757 body (raw, oldest first)


## 2026-01-19T16:20:16Z

### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
### Bug summary

Depending on the csv format, matplot lib can't understand the date format and prints string instead of dates. This prevent plt from properly handling overlapping x points.

### Code for reproduction


    import pandas as pd
    data = pd.read_csv(outfile, parse_dates=["timestamp"])
    print(data)
    plt.figure(figsize=(10, 6))
    plt.plot(
        data["timestamp"], data["mean_ms"], label="Mean Latency (ms)", color="blue"
    )
    plt.plot(
        data["timestamp"], data["median_ms"], label="Median Latency (ms)", color="green"
    )

    plt.xlabel("Time")
    plt.ylabel("Latency (ms)")
    plt.yscale("log")  # <-- Logarithmic Y-axis
    plt.title(f"Filesystem Latency Over Time: {name_label}")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)  # optional, improves log-scale grid
    plt.tight_layout()
    out_png = f"latency_trend_{name_label}.png"
    plt.savefig(out_png)
    plt.close()
    print(f"Plot updated -> {out_png}")


### Actual outcome

Assume two csv, one leading to a broken state:

timestamp,count,min_ms,max_ms,median_ms,q10_ms,q90_ms,mean_ms
2026-01-18T09:54:55.992045,3,125.598282,177.849797,134.512944,127.3812144,169.1824264,145.98700766666664
2026-01-18T09:55:06.003724,3,127.66462,177.592098,136.003603,129.3324166,169.274399,147.08677366666666
2026-01-18T09:55:16.414701,3,127.038487,174.363733,131.508812,127.932552,165.7927488,144.30367733333333
2026-01-18T09:55:25.994860,3,124.867563,178.87952,136.773244,127.2486992,170.45826480000002,146.840109
2026-01-18T09:55:36.418578,3,125.242661,179.326366,134.553067,127.1047422,170.3717062,146.37403133333333
2026-01-18T10:18:05.425304,3,127.058796,180.138256,134.612707,128.5695782,171.0331462,147.26991966666668
2026-01-19T16:08:00.017532,3,126.138651,147.071413,136.932927,128.2975062,145.0437158,136.71433033333332
2026-01-19T16:08:13.082541,3,127.325453,145.948022,136.355741,129.13151059999998,144.0295658,136.54307200000002
2026-01-19T16:08:22.997793,3,131.911903,147.166113,137.220907,132.9737038,145.1770718,138.76630766666668
2026-01-19T16:09:55,3,129.603559,147.074926,135.932547,130.8693566,144.8464502,137.53701066666667


Note the last line. this leads matplotlib to generate a graph like so:
<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/b534ab81-be6d-4d22-8cb4-e7fb83e65f52" />

### Expected outcome

An other one not triggering the bug:

timestamp,count,min_ms,max_ms,median_ms,q10_ms,q90_ms,mean_ms
2026-01-18T09:54:55.992045,3,125.598282,177.849797,134.512944,127.3812144,169.1824264,145.98700766666664
2026-01-18T09:55:06.003724,3,127.66462,177.592098,136.003603,129.3324166,169.274399,147.08677366666666
2026-01-18T09:55:16.414701,3,127.038487,174.363733,131.508812,127.932552,165.7927488,144.30367733333333
2026-01-18T09:55:25.994860,3,124.867563,178.87952,136.773244,127.2486992,170.45826480000002,146.840109
2026-01-18T09:55:36.418578,3,125.242661,179.326366,134.553067,127.1047422,170.3717062,146.37403133333333
2026-01-18T10:18:05.425304,3,127.058796,180.138256,134.612707,128.5695782,171.0331462,147.26991966666668
2026-01-19T16:08:00.017532,3,126.138651,147.071413,136.932927,128.2975062,145.0437158,136.71433033333332
2026-01-19T16:08:13.082541,3,127.325453,145.948022,136.355741,129.13151059999998,144.0295658,136.54307200000002
2026-01-19T16:08:22.997793,3,131.911903,147.166113,137.220907,132.9737038,145.1770718,138.76630766666668
2026-01-19T16:09:55.0,3,129.603559,147.074926,135.932547,130.8693566,144.8464502,137.53701066666667
2026-01-19T16:12:13.636429,3,128.80892,148.316719,138.636018,130.7743396,146.3805788,138.587219
2026-01-19T16:12:23.561082,3,131.215027,148.959601,136.480908,132.2682032,146.46386239999998,138.88517866666666


Instead of the valid:
<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/62aa45c4-1416-43b1-8ffe-c28e1fd9c369" />

### Additional information

_No response_

### Operating system

_No response_

### Matplotlib Version

3.10.0

### Installation

pip
```

### Issue Description

-

### Expected Behavior

Correct parsing.

### Installed Versions

<details>
INSTALLED VERSIONS
------------------
commit                : 0691c5cf90477d3503834d983f69350f250a6ff7
python                : 3.12.1
python-bits           : 64
OS                    : Linux
OS-release            : 4.18.0-553.22.1.el8_10.x86_64
Version               : #1 SMP Wed Sep 11 18:02:00 EDT 2024
machine               : x86_64
processor             : x86_64
byteorder             : little
LC_ALL                : None
LANG                  : en_US.UTF-8
LOCALE                : en_US.UTF-8

pandas                : 2.2.3
numpy                 : 2.2.6
pytz                  : 2025.2
dateutil              : 2.8.2
pip                   : 25.2
Cython                : 0.29.36
sphinx                : None
IPython               : 8.32.0
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : 4.13.4
blosc                 : None
bottleneck            : None
dataframe-api-compat  : None
fastparquet           : None
fsspec                : 2023.10.0
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : 3.1.5
lxml.etree            : 5.4.0
matplotlib            : 3.10.0
numba                 : None
numexpr               : 2.10.2
odfpy                 : None
openpyxl              : None
pandas_gbq            : None
psycopg2              : None
pymysql               : None
pyarrow               : 19.0.0
pyreadstat            : None
pytest                : None
python-calamine       : None
pyxlsb                : None
s3fs                  : None
scipy                 : 1.13.1
sqlalchemy            : 2.0.41
tables                : None
tabulate              : 0.9.0
xarray                : 2025.1.2
xlrd                  : None
xlsxwriter            : None
zstandard             : None
tzdata                : 2025.2
qtpy                  : None
pyqt5                 : None

</details>


## 2026-01-19T16:20:33Z

### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
### Bug summary

Depending on the csv format, matplot lib can't understand the date format and prints string instead of dates. This prevent plt from properly handling overlapping x points.

### Code for reproduction


    import pandas as pd
    data = pd.read_csv(outfile, parse_dates=["timestamp"])
    print(data)
    plt.figure(figsize=(10, 6))
    plt.plot(
        data["timestamp"], data["mean_ms"], label="Mean Latency (ms)", color="blue"
    )
    plt.plot(
        data["timestamp"], data["median_ms"], label="Median Latency (ms)", color="green"
    )

    plt.xlabel("Time")
    plt.ylabel("Latency (ms)")
    plt.yscale("log")  # <-- Logarithmic Y-axis
    plt.title(f"Filesystem Latency Over Time: {name_label}")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)  # optional, improves log-scale grid
    plt.tight_layout()
    out_png = f"latency_trend_{name_label}.png"
    plt.savefig(out_png)
    plt.close()
    print(f"Plot updated -> {out_png}")


### Actual outcome

Assume two csv, one leading to a broken state:

timestamp,count,min_ms,max_ms,median_ms,q10_ms,q90_ms,mean_ms
2026-01-18T09:54:55.992045,3,125.598282,177.849797,134.512944,127.3812144,169.1824264,145.98700766666664
2026-01-18T09:55:06.003724,3,127.66462,177.592098,136.003603,129.3324166,169.274399,147.08677366666666
2026-01-18T09:55:16.414701,3,127.038487,174.363733,131.508812,127.932552,165.7927488,144.30367733333333
2026-01-18T09:55:25.994860,3,124.867563,178.87952,136.773244,127.2486992,170.45826480000002,146.840109
2026-01-18T09:55:36.418578,3,125.242661,179.326366,134.553067,127.1047422,170.3717062,146.37403133333333
2026-01-18T10:18:05.425304,3,127.058796,180.138256,134.612707,128.5695782,171.0331462,147.26991966666668
2026-01-19T16:08:00.017532,3,126.138651,147.071413,136.932927,128.2975062,145.0437158,136.71433033333332
2026-01-19T16:08:13.082541,3,127.325453,145.948022,136.355741,129.13151059999998,144.0295658,136.54307200000002
2026-01-19T16:08:22.997793,3,131.911903,147.166113,137.220907,132.9737038,145.1770718,138.76630766666668
2026-01-19T16:09:55,3,129.603559,147.074926,135.932547,130.8693566,144.8464502,137.53701066666667


Note the last line. this leads matplotlib to generate a graph like so:
<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/b534ab81-be6d-4d22-8cb4-e7fb83e65f52" />

### Expected outcome

An other one not triggering the bug:

timestamp,count,min_ms,max_ms,median_ms,q10_ms,q90_ms,mean_ms
2026-01-18T09:54:55.992045,3,125.598282,177.849797,134.512944,127.3812144,169.1824264,145.98700766666664
2026-01-18T09:55:06.003724,3,127.66462,177.592098,136.003603,129.3324166,169.274399,147.08677366666666
2026-01-18T09:55:16.414701,3,127.038487,174.363733,131.508812,127.932552,165.7927488,144.30367733333333
2026-01-18T09:55:25.994860,3,124.867563,178.87952,136.773244,127.2486992,170.45826480000002,146.840109
2026-01-18T09:55:36.418578,3,125.242661,179.326366,134.553067,127.1047422,170.3717062,146.37403133333333
2026-01-18T10:18:05.425304,3,127.058796,180.138256,134.612707,128.5695782,171.0331462,147.26991966666668
2026-01-19T16:08:00.017532,3,126.138651,147.071413,136.932927,128.2975062,145.0437158,136.71433033333332
2026-01-19T16:08:13.082541,3,127.325453,145.948022,136.355741,129.13151059999998,144.0295658,136.54307200000002
2026-01-19T16:08:22.997793,3,131.911903,147.166113,137.220907,132.9737038,145.1770718,138.76630766666668
2026-01-19T16:09:55.0,3,129.603559,147.074926,135.932547,130.8693566,144.8464502,137.53701066666667
2026-01-19T16:12:13.636429,3,128.80892,148.316719,138.636018,130.7743396,146.3805788,138.587219
2026-01-19T16:12:23.561082,3,131.215027,148.959601,136.480908,132.2682032,146.46386239999998,138.88517866666666


Instead of the valid:
<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/62aa45c4-1416-43b1-8ffe-c28e1fd9c369" />

### Additional information

_No response_

### Operating system

_No response_

### Matplotlib Version

3.10.0

### Installation

pip
```

### Installed Versions

<details>
INSTALLED VERSIONS
------------------
commit                : 0691c5cf90477d3503834d983f69350f250a6ff7
python                : 3.12.1
python-bits           : 64
OS                    : Linux
OS-release            : 4.18.0-553.22.1.el8_10.x86_64
Version               : #1 SMP Wed Sep 11 18:02:00 EDT 2024
machine               : x86_64
processor             : x86_64
byteorder             : little
LC_ALL                : None
LANG                  : en_US.UTF-8
LOCALE                : en_US.UTF-8

pandas                : 2.2.3
numpy                 : 2.2.6
pytz                  : 2025.2
dateutil              : 2.8.2
pip                   : 25.2
Cython                : 0.29.36
sphinx                : None
IPython               : 8.32.0
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : 4.13.4
blosc                 : None
bottleneck            : None
dataframe-api-compat  : None
fastparquet           : None
fsspec                : 2023.10.0
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : 3.1.5
lxml.etree            : 5.4.0
matplotlib            : 3.10.0
numba                 : None
numexpr               : 2.10.2
odfpy                 : None
openpyxl              : None
pandas_gbq            : None
psycopg2              : None
pymysql               : None
pyarrow               : 19.0.0
pyreadstat            : None
pytest                : None
python-calamine       : None
pyxlsb                : None
s3fs                  : None
scipy                 : 1.13.1
sqlalchemy            : 2.0.41
tables                : None
tabulate              : 0.9.0
xarray                : 2025.1.2
xlrd                  : None
xlsxwriter            : None
zstandard             : None
tzdata                : 2025.2
qtpy                  : None
pyqt5                 : None

</details>


## 2026-01-19T16:21:10Z

### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

Depending on the csv format, matplot lib can't understand the date format and prints string instead of dates. This prevent plt from properly handling overlapping x points.

```python
    import pandas as pd
    data = pd.read_csv(outfile, parse_dates=["timestamp"])
    print(data)
    plt.figure(figsize=(10, 6))
    plt.plot(
        data["timestamp"], data["mean_ms"], label="Mean Latency (ms)", color="blue"
    )
    plt.plot(
        data["timestamp"], data["median_ms"], label="Median Latency (ms)", color="green"
    )

    plt.xlabel("Time")
    plt.ylabel("Latency (ms)")
    plt.yscale("log")  # <-- Logarithmic Y-axis
    plt.title(f"Filesystem Latency Over Time: {name_label}")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)  # optional, improves log-scale grid
    plt.tight_layout()
    out_png = f"latency_trend_{name_label}.png"
    plt.savefig(out_png)
    plt.close()
    print(f"Plot updated -> {out_png}")
```

### Actual outcome

Assume two csv, one leading to a broken state:
```
timestamp,count,min_ms,max_ms,median_ms,q10_ms,q90_ms,mean_ms
2026-01-18T09:54:55.992045,3,125.598282,177.849797,134.512944,127.3812144,169.1824264,145.98700766666664
2026-01-18T09:55:06.003724,3,127.66462,177.592098,136.003603,129.3324166,169.274399,147.08677366666666
2026-01-18T09:55:16.414701,3,127.038487,174.363733,131.508812,127.932552,165.7927488,144.30367733333333
2026-01-18T09:55:25.994860,3,124.867563,178.87952,136.773244,127.2486992,170.45826480000002,146.840109
2026-01-18T09:55:36.418578,3,125.242661,179.326366,134.553067,127.1047422,170.3717062,146.37403133333333
2026-01-18T10:18:05.425304,3,127.058796,180.138256,134.612707,128.5695782,171.0331462,147.26991966666668
2026-01-19T16:08:00.017532,3,126.138651,147.071413,136.932927,128.2975062,145.0437158,136.71433033333332
2026-01-19T16:08:13.082541,3,127.325453,145.948022,136.355741,129.13151059999998,144.0295658,136.54307200000002
2026-01-19T16:08:22.997793,3,131.911903,147.166113,137.220907,132.9737038,145.1770718,138.76630766666668
2026-01-19T16:09:55,3,129.603559,147.074926,135.932547,130.8693566,144.8464502,137.53701066666667
```

Note the last line. this leads matplotlib to generate a graph like so:
<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/b534ab81-be6d-4d22-8cb4-e7fb83e65f52" />

### Expected outcome

An other one not triggering the bug:
```
timestamp,count,min_ms,max_ms,median_ms,q10_ms,q90_ms,mean_ms
2026-01-18T09:54:55.992045,3,125.598282,177.849797,134.512944,127.3812144,169.1824264,145.98700766666664
2026-01-18T09:55:06.003724,3,127.66462,177.592098,136.003603,129.3324166,169.274399,147.08677366666666
2026-01-18T09:55:16.414701,3,127.038487,174.363733,131.508812,127.932552,165.7927488,144.30367733333333
2026-01-18T09:55:25.994860,3,124.867563,178.87952,136.773244,127.2486992,170.45826480000002,146.840109
2026-01-18T09:55:36.418578,3,125.242661,179.326366,134.553067,127.1047422,170.3717062,146.37403133333333
2026-01-18T10:18:05.425304,3,127.058796,180.138256,134.612707,128.5695782,171.0331462,147.26991966666668
2026-01-19T16:08:00.017532,3,126.138651,147.071413,136.932927,128.2975062,145.0437158,136.71433033333332
2026-01-19T16:08:13.082541,3,127.325453,145.948022,136.355741,129.13151059999998,144.0295658,136.54307200000002
2026-01-19T16:08:22.997793,3,131.911903,147.166113,137.220907,132.9737038,145.1770718,138.76630766666668
2026-01-19T16:09:55.0,3,129.603559,147.074926,135.932547,130.8693566,144.8464502,137.53701066666667
2026-01-19T16:12:13.636429,3,128.80892,148.316719,138.636018,130.7743396,146.3805788,138.587219
2026-01-19T16:12:23.561082,3,131.215027,148.959601,136.480908,132.2682032,146.46386239999998,138.88517866666666
```

Instead of the valid:
<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/62aa45c4-1416-43b1-8ffe-c28e1fd9c369" />

### Additional information

_No response_

### Operating system

_No response_

### Matplotlib Version

3.10.0

### Installation

pip
```

### Installed Versions

<details>
INSTALLED VERSIONS
------------------
commit                : 0691c5cf90477d3503834d983f69350f250a6ff7
python                : 3.12.1
python-bits           : 64
OS                    : Linux
OS-release            : 4.18.0-553.22.1.el8_10.x86_64
Version               : #1 SMP Wed Sep 11 18:02:00 EDT 2024
machine               : x86_64
processor             : x86_64
byteorder             : little
LC_ALL                : None
LANG                  : en_US.UTF-8
LOCALE                : en_US.UTF-8

pandas                : 2.2.3
numpy                 : 2.2.6
pytz                  : 2025.2
dateutil              : 2.8.2
pip                   : 25.2
Cython                : 0.29.36
sphinx                : None
IPython               : 8.32.0
adbc-driver-postgresql: None
adbc-driver-sqlite    : None
bs4                   : 4.13.4
blosc                 : None
bottleneck            : None
dataframe-api-compat  : None
fastparquet           : None
fsspec                : 2023.10.0
html5lib              : None
hypothesis            : None
gcsfs                 : None
jinja2                : 3.1.5
lxml.etree            : 5.4.0
matplotlib            : 3.10.0
numba                 : None
numexpr               : 2.10.2
odfpy                 : None
openpyxl              : None
pandas_gbq            : None
psycopg2              : None
pymysql               : None
pyarrow               : 19.0.0
pyreadstat            : None
pytest                : None
python-calamine       : None
pyxlsb                : None
s3fs                  : None
scipy                 : 1.13.1
sqlalchemy            : 2.0.41
tables                : None
tabulate              : 0.9.0
xarray                : 2025.1.2
xlrd                  : None
xlsxwriter            : None
zstandard             : None
tzdata                : 2025.2
qtpy                  : None
pyqt5                 : None

</details>

