from orwynn.bootscript.errors import NoScriptsForCallTimeError, ScriptsAlreadyCalledError
from orwynn.worker import Worker
from orwynn.bootscript._Bootscript import Bootscript
from orwynn.bootscript._CallTime import CallTime


_IsCallPerformed = bool
# Represents bootscripts sorted by their call time and followed by
# a flag signified whether the call was already performed
_ScriptsState = tuple[list[Bootscript], _IsCallPerformed]
_CallState = dict[CallTime, _ScriptsState]


class BootscriptWorker(Worker):
    """
    Calls different defined bootscripts.
    """
    def __init__(self, bootscripts: list[Bootscript]) -> None:
        super().__init__()
        self.__bootscripts: list[Bootscript] = bootscripts
        self.__call_state: _CallState = self.__initialize_call_state()

    def __initialize_call_state(
        self
    ) -> _CallState:
        state: _CallState = {}

        for bs in self.__bootscripts:
            state.setdefault(bs.call_time, ([], False))
            state[bs.call_time][0].append(bs)

        return state

    def call_by_time(
        self,
        call_time: CallTime
    ) -> None:
        try:
            scripts_state: _ScriptsState = \
                self.__call_state[call_time]
        except KeyError as err:
            raise NoScriptsForCallTimeError(
                f"cannot find any scripts for call time {call_time}"
            ) from err
        else:
            if scripts_state[1] is True:
                raise ScriptsAlreadyCalledError(
                    f"scripts for time {call_time} were already called"
                )
            else:
                for script in scripts_state[0]:
                    self.__call_script(script)
                scripts_state = (scripts_state[0], True)

    def __call_script(
        self,
        script: Bootscript
    ) -> None:
        # How to use DI?
        pass
