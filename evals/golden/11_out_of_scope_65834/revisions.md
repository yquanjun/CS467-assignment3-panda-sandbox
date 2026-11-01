# Revisions of pandas issue 65834 body (raw, oldest first)


## 2026-06-09T15:28:35Z

### Installation check

- [x] I have read the [installation guide](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-pandas).


### Platform

Linux-3.10.0-1160.21.1.el7.x86_64-x86_64-with-glibc2.17

### Installation Method

pip install

### pandas Version

3.0.3

### Python Version

3.14.3

### Installation Logs

<details>

Collecting pandas
  Using cached pandas-3.0.3.tar.gz (4.7 MB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'error'
  error: subprocess-exited-with-error

  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [16 lines of output]
      + meson setup /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52 /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo -Dbuildtype=release -Db_ndebug=if-release -Db_vscrt=md --vsenv --native-file=/scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo/meson-python-native-file.ini
      The Meson build system
      Version: 1.11.1
      Source dir: /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52
      Build dir: /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo
      Build type: native build
      Project name: pandas
      Project version: 3.0.3
      C compiler for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/gcc (gcc 12.5.0 "gcc (Spack GCC) 12.5.0")
      C linker for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/gcc ld.bfd 2.27-44
      C++ compiler for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/g++ (gcc 12.5.0 "g++ (Spack GCC) 12.5.0")
      C++ linker for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/g++ ld.bfd 2.27-44

      ../meson.build:2:0: ERROR: Compiler cython cannot compile programs.

      A full log can be found at /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo/meson-logs/meson-log.txt
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> pandas

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
</details>

The referenced meson-log.txt file does not exist.

Cython version is 3.2.5

## 2026-06-09T15:29:17Z

### Installation check

- [x] I have read the [installation guide](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-pandas).


### Platform

Linux-3.10.0-1160.21.1.el7.x86_64-x86_64-with-glibc2.17

### Installation Method

pip install

### pandas Version

3.0.3

### Python Version

3.14.3

### Installation Logs

<details>
```
Collecting pandas
  Using cached pandas-3.0.3.tar.gz (4.7 MB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'error'
  error: subprocess-exited-with-error

  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [16 lines of output]
      + meson setup /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52 /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo -Dbuildtype=release -Db_ndebug=if-release -Db_vscrt=md --vsenv --native-file=/scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo/meson-python-native-file.ini
      The Meson build system
      Version: 1.11.1
      Source dir: /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52
      Build dir: /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo
      Build type: native build
      Project name: pandas
      Project version: 3.0.3
      C compiler for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/gcc (gcc 12.5.0 "gcc (Spack GCC) 12.5.0")
      C linker for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/gcc ld.bfd 2.27-44
      C++ compiler for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/g++ (gcc 12.5.0 "g++ (Spack GCC) 12.5.0")
      C++ linker for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/g++ ld.bfd 2.27-44

      ../meson.build:2:0: ERROR: Compiler cython cannot compile programs.

      A full log can be found at /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo/meson-logs/meson-log.txt
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> pandas

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
```
</details>

The referenced meson-log.txt file does not exist.

Cython version is 3.2.5

## 2026-06-09T15:30:13Z

### Installation check

- [x] I have read the [installation guide](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-pandas).


### Platform

Linux-3.10.0-1160.21.1.el7.x86_64-x86_64-with-glibc2.17

### Installation Method

pip install

### pandas Version

3.0.3

### Python Version

3.14.3

### Installation Logs

The referenced meson-log.txt file does not exist.

Cython version is 3.2.5

<details>
Collecting pandas
  Using cached pandas-3.0.3.tar.gz (4.7 MB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'error'
  error: subprocess-exited-with-error

  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [16 lines of output]
      + meson setup /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52 /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo -Dbuildtype=release -Db_ndebug=if-release -Db_vscrt=md --vsenv --native-file=/scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo/meson-python-native-file.ini
      The Meson build system
      Version: 1.11.1
      Source dir: /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52
      Build dir: /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo
      Build type: native build
      Project name: pandas
      Project version: 3.0.3
      C compiler for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/gcc (gcc 12.5.0 "gcc (Spack GCC) 12.5.0")
      C linker for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/gcc ld.bfd 2.27-44
      C++ compiler for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/g++ (gcc 12.5.0 "g++ (Spack GCC) 12.5.0")
      C++ linker for the host machine: /gpfs/fs001/cbica/software/centos7/spack/opt/spack/linux-ivybridge/gcc-12.5.0-xhapucmtizog3twjgiqz2lccrn25pqnv/bin/g++ ld.bfd 2.27-44

      ../meson.build:2:0: ERROR: Compiler cython cannot compile programs.

      A full log can be found at /scratch/chind/tmp.5txEgCZvpK/pip-install-y68gdhpf/pandas_bba0f97c1e614303a753979451e44f52/.mesonpy-01je90xo/meson-logs/meson-log.txt
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> pandas

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
</details>


