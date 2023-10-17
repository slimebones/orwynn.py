from typing import Any


class RestrictedDeletionError(Exception):
    """
    When deletion of object is restricted due to dependency, e.g. in
    one-to-many relations: you cannot delete parent if it has any children in
    relationship - they would end up orphaned which is often restricted by
    Sql NOT NULL constraint for foreign key.
    """

class AlreadyAttachedError(Exception):
    """
    When someone tries to attach an object in relationship that already exist
    there.
    """
    def __init__(
        self,
        *,
        attachment_name: str,
        attachment_value: str,
        target_name: str,
        target_value: str,
    ) -> None:
        message: str = \
            f"{attachment_name}={attachment_value} already attached" \
            f" to {target_name}={target_value}"
        super().__init__(message)


class NonManageableSHDError(Exception):
    """
    Non-manageable SHD cannot perform some operation.
    """
    def __init__(
        self,
        *,
        operation_name: str,
    ):
        message: str = \
            f"cannot perform operation={operation_name} in a non-manageable" \
            " session"
        super().__init__(message)


class ManageableSHDError(Exception):
    """
    Manageable SHD cannot perform some operation.
    """
    def __init__(
        self,
        *,
        operation_name: str,
    ):
        message: str = \
            f"cannot perform operation={operation_name} in a manageable" \
            " session"
        super().__init__(message)


class EmptyExecutionQueueError(Exception):
    """
    Execution queue is empty.
    """
    def __init__(
        self,
    ):
        message: str = "execution queue is empty"
        super().__init__(message)


class SqlToUpstreamUnmatchError(Exception):
    """
    SQL cannot be None if an upstream SHD is not set.
    """
    def __init__(
        self,
    ):
        message: str = \
            "cannot set SQL to None since the upstream shd is None too"
        super().__init__(message)


class UnexpectedAmountError(Exception):
    """
    Not expected amount of instances are returned.
    """
    def __init__(
        self,
        *,
        title: str,
        expected_amount: int,
        fact_amount: int,
    ):
        message: str = \
            f"{title} amount expected={expected_amount}," \
            f" got fact={fact_amount}"
        super().__init__(message)


class ExistingUnitError(Exception):
    """
    Unit already exists in database.
    """
    def __init__(
        self,
        *,
        title: str,
        value: Any,
    ):
        message: str = f"{title}={value} already exists in database"
        super().__init__(message)
