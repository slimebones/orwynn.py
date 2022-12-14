from orwynn.base.error.error import Error


class FinalizedDIContainerError(Error):
    """If some evil force is trying to add objects to a finalized container.
    """
    pass
