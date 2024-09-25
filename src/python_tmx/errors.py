from lxml.etree import _Element


class MissingAttributeError(Exception):
    def __init__(self, attribute: str, element: _Element) -> None:
        super().__init__(f"Element {element.tag} is missing attribute {attribute}")


class MissingTextError(Exception):
    def __init__(self, element: _Element) -> None:
        super().__init__(f"Element <{element.tag}> is missing text data")


class MissingChildrenError(Exception):
    def __init__(self, element: _Element) -> None:
        super().__init__(f"Element <{element.tag}> is missing children")


class ExtraTextError(Exception):
    def __init__(self, element: _Element) -> None:
        super().__init__(
            f"Element <{element.tag}> has extra text data:\n'{element.text}'"
        )


class ExtraChildrenError(Exception):
    def __init__(self, element: _Element, extra: _Element) -> None:
        super().__init__(f"Found extra <{extra.tag}> tag: inside <{element.tag}>\n")


class UnknownTagError(Exception):
    def __init__(self, tag: str) -> None:
        super().__init__(f"Unknown tag '{tag}' found")
