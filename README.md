# flake8-vedro
Flake8 based linter for [Vedro](https://vedro.io/) framework

All validation rules description is in progress, but you can find them [here](/flake8_vedro/errors/errors.py).

## Installation

```bash
pip install flake8-vedro
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
