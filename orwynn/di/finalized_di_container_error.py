from orwynn.base.error._Error import Error


class FinalizedDIContainerError(Error):
    """If some evil force is trying to add objects to a finalized container.
    """
    pass
