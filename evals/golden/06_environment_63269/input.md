### Pandas version checks

- [x] I have checked that this issue has not already been reported.

- [x] I have confirmed this bug exists on the [latest version](https://pandas.pydata.org/docs/whatsnew/index.html) of pandas.

- [x] I have confirmed this bug exists on the [main branch](https://pandas.pydata.org/docs/dev/getting_started/install.html#installing-the-development-version-of-pandas) of pandas.


### Reproducible Example

```python
andas/compat/_optional.py", line 135, in import_optional_dependency
    module = importlib.import_module(name)
  File "/home/x/anaconda3/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "/home/x/anaconda3/lib/python3.12/site-packages/numexpr/__init__.py", line 24, in <module>
    from numexpr.interpreter import MAX_THREADS, use_vml, __BLOCK_SIZE1__
AttributeError: _ARRAY_API not found

A module that was compiled using NumPy 1.x cannot be run in
NumPy 2.2.6 as it may crash. To support both 1.x and 2.x
versions of NumPy, modules must be compiled with NumPy 2.0.
Some module may need to rebuild instead e.g. with 'pybind11>=2.12'.

If you are a user of the module, the easiest solution will be to
downgrade to 'numpy<2' or try to upgrade the affected module.
We expect that some modules will need time to support NumPy 2.
```

### Issue Description

this is the **Only** lib that didn't supprot numpy 2.0 until 2025

### Expected Behavior

support numpy 2.0

### Installed Versions

<details>

Replace this line with the output of pd.show_versions()

</details>
Name: pandas
Version: 2.3.3
