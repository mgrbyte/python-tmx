class MissingAttributeError(Exception):
    def __init__(self, attribute: str, element: str) -> None:
        super().__init__(f"Element {element} is missing attribute {attribute}")


class MissingTextError(Exception):
    def __init__(self, element: str) -> None:
        super().__init__(f"Element <{element}> is missing text data")


class MissingChildrenError(Exception):
    def __init__(self, element: str) -> None:
        super().__init__(f"Element <{element}> is missing children")


class ExtraTextError(Exception):
    def __init__(self, element: str) -> None:
        super().__init__(f"Element <{element}> has extra text data")


class ExtraChildrenError(Exception):
    def __init__(self, element: str) -> None:
        super().__init__(f"Element <{element}> has extra children")


class UnknownTagError(Exception):
    def __init__(self, tag: str) -> None:
        super().__init__(f"Unknown tag '{tag}' found")
