# flake8-vedro
Flake8 based linter for [Vedro](https://vedro.io/) framework

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
is_context_assert_optional = true     # VDR400
```

## Rules

### Scenario Rules
1. [VDR001. Decorator @vedro.only should not be presented](./flake8_vedro/rules/VDR101.md)
2. [VDR002. Scenario should be inherited from class vedro.Scenario](./flake8_vedro/rules/VDR102.md)
3. [VDR103. Scenario should be located in the folder "scenarios/”](./flake8_vedro/rules/VDR103.md)
4. [VDR104. Scenario should have a subject](./flake8_vedro/rules/VDR104.md)
5. [VDR105. Scenario subject should not be empty](./flake8_vedro/rules/VDR105.md)
6. [VDR106. Scenario should have only one subject](./flake8_vedro/rules/VDR106.md)
7. [VDR107. Subject is not parameterized*](./flake8_vedro/rules/VDR107.md)
8. [VDR108. Calling functions in parametrization](./flake8_vedro/rules/VDR108.md)
9. [VDR109. Limit the amount of parameters in a parametrized scenario](./flake8_vedro/rules/VDR109.md)


###  Scenario Steps Rules
1. [VDR300. Step name should start with..](./flake8_vedro/rules/VDR300.md)
2. [VDR301. Steps name should be in right order](./flake8_vedro/rules/VDR301.md)
3. [VDR302. Interface should not be used in given or asserted steps](./flake8_vedro/rules/VDR302.md)
4. [VDR303. Scenario should have a "when" step](./flake8_vedro/rules/VDR303.md)
5. [VDR304. Scenario should have only one "when" step](./flake8_vedro/rules/VDR304.md)
6. [VDR305. Scenario should have a "then" step](./flake8_vedro/rules/VDR305.md)
7. [VDR306. Scenario should have only one "then" step](./flake8_vedro/rules/VDR306.md)
8. [VDR307. Step should have an assertion](./flake8_vedro/rules/VDR307.md)
9. [VDR308. Step should have specific assertions](./flake8_vedro/rules/VDR308.md)
10. [VDR309. Step should not have comparison without assert](./flake8_vedro/rules/VDR309.md)
11. [VDR310. Some steps should not have an assertion](./flake8_vedro/rules/VDR310.md)
12. [VDR311. Scope variables should not be redefined](./flake8_vedro/rules/VDR311.md)
13. [VDR312. Scope variables should not be partially redefined](./flake8_vedro/rules/VDR312.md)


###  Contexts Rules
14. [VDR400. Contexts should have specific assertions](./flake8_vedro/rules/VDR400md)