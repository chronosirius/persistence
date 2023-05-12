"""Added methods for the `interactions.Client` instance for ease of use."""

def persistent_component(self, tag: str):
    """
    The persistent component decorator for the Client object.

    Parameters:
        tag (str): The tag to identify your component.
    """

    def inner(coro):
        return self.persistence.component(tag)(coro)

    return inner


def persistent_modal(self, tag: str):
    """
    The persistent modal decorator for the Client object.

    Parameters:
        tag (str): The tag to identify your modal.
        use_kwargs (bool): Whether to return key word arguments mapped with the custom_ids of the individual text inputs. Not recommended.
                (defaults to False)
    """

    def inner(coro):
        return self.persistence.modal(tag)(coro)

    return inner
