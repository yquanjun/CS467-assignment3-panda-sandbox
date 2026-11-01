### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [ ] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
freq = pd.offsets.CustomBusinessDay(holidays=["2020-01-10"])  # Problem
s1 = pd.Series(data=1, index=pd.date_range(start="2020-01-01", periods=5, freq=freq), name="S1")
s2 = pd.Series(data=1, index=pd.date_range(start=s1.index[3], periods=5, freq=freq), name="S2")
s3 = pd.Series(data=1, index=pd.date_range(start=s2.index[3], periods=5, freq=freq), name="S3")
pd.concat([s1, s3, s2], axis=1).index.freq  # Should not be none.
```

### Issue Description

Consider this
```python
# freq = "D"  # No problem
# freq = "B"  # No problem
freq = pd.offsets.CustomBusinessDay(holidays=["2020-01-10"])  # Problem
s1 = pd.Series(data=1, index=pd.date_range(start="2020-01-01", periods=5, freq=freq), name="S1")
s2 = pd.Series(data=1, index=pd.date_range(start=s1.index[3], periods=5, freq=freq), name="S2")
s3 = pd.Series(data=1, index=pd.date_range(start=s2.index[3], periods=5, freq=freq), name="S3")
pd.concat([s1, s2, s3], axis=1)
```
```
             S1   S2   S3
2020-01-01  1.0  NaN  NaN
2020-01-02  1.0  NaN  NaN
2020-01-03  1.0  NaN  NaN
2020-01-06  1.0  1.0  NaN
2020-01-07  1.0  1.0  NaN
2020-01-08  NaN  1.0  NaN
2020-01-09  NaN  1.0  1.0
2020-01-13  NaN  1.0  1.0
2020-01-14  NaN  NaN  1.0
2020-01-15  NaN  NaN  1.0
2020-01-16  NaN  NaN  1.0
```

We find that
```python
pd.concat([s1, s2, s3], axis=1).index
```
```
DatetimeIndex(['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-06',
               '2020-01-07', '2020-01-08', '2020-01-09', '2020-01-13',
               '2020-01-14', '2020-01-15', '2020-01-16'],
              dtype='datetime64[ns]', freq='C')
```
and
```python
pd.concat([s1, s3, s2], axis=1).index
```
```
DatetimeIndex(['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-06',
               '2020-01-07', '2020-01-08', '2020-01-09', '2020-01-13',
               '2020-01-14', '2020-01-15', '2020-01-16'],
              dtype='datetime64[ns]', freq=None)
```

Notice that `freq=None` when the order is `1, 3, 2`.

Tested using pandas 3.0.1 on Python 3.14.2.

### Expected Behavior

The order items in `pd.concat` should not matter for the resulting `.index`.

### Installed Versions

<details>

Replace this line with the output of pd.show_versions()

</details>
