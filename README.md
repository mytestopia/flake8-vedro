# flake8-vedro
Flake8 based linter for [Vedro](https://vedro.io/) framework

All validation rules description is in progress, but you can find them [here](/flake8_vedro/errors/errors.py).

## Installation

```bash
pip inslall git+https://github.com/mytestopia/flake8-vedro@v1.0.0
```

## Configuration
Flake8-vedro is flake8 plugin, so the configuration is the same as [flake8 configuration](https://flake8.pycqa.org/en/latest/user/configuration.html).

You can ignore rules via
- file `setup.cfg`: parameter `ignore`
```editorconfig
[flake8]
ignore = VDR101
```
- comment in code `#noqa: VDR101`

Some rules in linter should be configurated:
```editorconfig
[flake8]
scenario_params_max_count = 8  # VDR109
allowed_to_redefine_list = page,page2  # VDR311
```
