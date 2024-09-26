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
    def __init__(self, element: str, text: str) -> None:
        super().__init__(f"Element <{element}> has extra text data:\n'{text}'")


class ExtraChildrenError(Exception):
    def __init__(self, element: str, extra: str) -> None:
        super().__init__(f"Found extra <{extra}> tag: inside <{element}>\n")


class UnknownTagError(Exception):
    def __init__(self, tag: str) -> None:
        super().__init__(f"Unknown tag '{tag}' found")


class MissingSegmentError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Tuv object cannot have an empty segment", *args)


class IncorrectRootError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Root tag is not <tmx>", *args)
