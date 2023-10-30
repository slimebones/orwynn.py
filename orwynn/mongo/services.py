from typing import Any

from antievil import NotFoundError

from orwynn.base import Service
from orwynn.mongo.search import MongoStateFlagSearch
from orwynn.mongo.stateflag import MongoStateFlag
from orwynn.mongo.utils import MongoUtils
from orwynn.utils.func import FuncSpec


class MongoStateFlagService(Service):
    def get(
        self,
        search: MongoStateFlagSearch
    ) -> list[MongoStateFlag]:
        query: dict[str, Any] = {}

        if search.ids:
            query["id"] = {
                "$in": search.ids
            }
        if search.keys:
            query["key"] = {
                "$in": search.keys
            }
        if search.values:
            query["value"] = {
                "$in": search.values
            }

        return MongoUtils.process_query(
            query,
            search,
            MongoStateFlag
        )

    def get_first_or_set_default(
        self,
        key: str,
        default_value: bool
    ) -> MongoStateFlag:
        """
        Returns first flag found for given search or a new flag initialized
        with default value.
        """
        try:
            return self.get(MongoStateFlagSearch(
                keys=[key]
            ))[0]
        except NotFoundError:
            return self.set(
                key,
                default_value
            )

    def set(
        self,
        key: str,
        value: bool
    ) -> MongoStateFlag:
        """
        Sets new value for a key.

        If the key does not exist, create a new state flag with given value.
        """
        flag: MongoStateFlag

        try:
            flag = self.get(MongoStateFlagSearch(
                keys=[key]
            ))[0]
        except NotFoundError:
            flag = MongoStateFlag(key=key, value=value).create()
        else:
            flag = flag.update(set={"value": value})

        return flag

    def decide(
        self,
        *,
        key: str,
        on_true: FuncSpec | None = None,
        on_false: FuncSpec | None = None,
        finally_set_to: bool,
        default_flag_on_not_found: bool
    ) -> Any:
        """
        Takes an action based on flag retrieved value.

        Args:
            key:
                Key of the flag to search for.
            finally_set_to:
                To which value the flag should be set after the operation is
                done.
            default_flag_on_not_found:
                Which value is to set for the unexistent by key flag.
            on_true(optional):
                Function to be called if the flag is True. Nothing is called
                by default.
            on_false(optional):
                Function to be called if the flag is False. Nothing is called
                by default.

        Returns:
            Chosen function output. None if no function is used.
        """
        result: Any = None
        flag: MongoStateFlag = self.get_first_or_set_default(
            key, default_flag_on_not_found
        )

        if flag.value is True and on_true is not None:
            result = on_true.call()
        if flag.value is False and on_false is not None:
            result = on_false.call()

        flag.update(
            set={
                "value": finally_set_to
            }
        )

        return result
