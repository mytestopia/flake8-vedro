from flake8_plugin_utils import Error


class DecoratorVedroOnly(Error):
    code = 'VDR101'
    message = 'decorator @vedro.only should not be presented'


class ScenarioNotInherited(Error):
    code = 'VDR102'
    message = 'class Scenario should be inherited from class vedro.Scenario'


class ScenarioLocationInvalid(Error):
    code = 'VDR103'
    message = 'scenario should be located in the folder "scenarios/"'


# Subject errors

class SubjectNotFound(Error):
    code = 'VDR104'
    message = 'scenario should have a subject'


class SubjectEmpty(Error):
    code = 'VDR105'
    message = 'subject in scenario should not be empty'


class SubjectDuplicated(Error):
    code = 'VDR106'
    message = 'scenario should have only one subject'


# Parametrization errors

class SubjectIsNotParametrized(Error):
    code = 'VDR107'
    message = 'subject in parametrised scenario is not parameterized'


class ContextCallInParams(Error):
    code = 'VDR108'
    message = 'context call in parametrization'


class ExceedMaxParamsCount(Error):
    code = 'VDR109'
    message = 'exceeded max parameters in vedro.params: {current} > {max}'


# Step errors

class StepInvalidName(Error):
    code = 'VDR300'
    message = 'step name should start with "given_", "when_", "then_", "and_", "but_". ' \
              '"{step_name}" is given.'


class StepsWrongOrder(Error):
    code = 'VDR301'
    message = 'steps order is wrong: step "{previous_step}" should not be before "{current_step}"'


class ImportedInterfaceInWrongStep(Error):
    code = 'VDR302'
    message = 'interface should not be used in contexts (given) or asserts (then, and, but) steps - ' \
              '"{func_name}" is used.'


class StepWhenNotFound(Error):
    code = 'VDR303'
    message = 'scenario should have "when" step'


class StepWhenDuplicated(Error):
    code = 'VDR304'
    message = 'scenario should have only one "when" step'


class StepThenNotFound(Error):
    code = 'VDR305'
    message = 'scenario should have a "then" step'


class StepThenDuplicated(Error):
    code = 'VDR306'
    message = 'scenario should have only one "then" step'


class StepAssertWithoutAssert(Error):
    code = 'VDR307'
    message = 'step "{step_name}" does not have an assert'


# assert foo, assert True
class StepAssertHasUselessAssert(Error):
    code = 'VDR308'
    message = 'step "{step_name}" has useless assert'


# foo == var
class StepAssertHasComparisonWithoutAssert(Error):
    code = 'VDR309'
    message = 'step "{step_name}" has comparison without assert'


class StepHasAssert(Error):
    code = 'VDR310'
    message = 'step "{step_name}" should not have assertion'


class ScopeVarIsRedefined(Error):
    code = 'VDR311'
    message = 'scope variable "{name}" is redefined'


class ScopeVarIsPartiallyRedefined(Error):
    code = 'VDR312'
    message = 'scope variable "{name}" is partially redefined'


class ContextWithoutAssert(Error):
    code = 'VDR400'
    message = 'context "{context_name}" does not have an assert'
