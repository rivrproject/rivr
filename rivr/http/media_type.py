from typing import List, Optional, Self, Tuple


class Parameter:
    @classmethod
    def parse(cls, parameter: str) -> Self:
        name, _, value = parameter.strip().partition('=')
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return cls(name, value)

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def __str__(self) -> str:
        # FIXME support quoted string if needed
        return f'{self.name}={self.value}'

    def __eq__(self, parameter) -> bool:
        return (
            isinstance(parameter, Parameter)
            and self.name == parameter.name
            and self.value == parameter.value
        )


class MediaType:
    @classmethod
    def parse(cls, media_type: str) -> Self:
        first, _, parameters = media_type.partition(';')
        type, _, subtype = first.partition('/')
        if parameters:
            # FIXME - primitive parser, does not handle quoted string correctly
            parsed_parameters = list(map(Parameter.parse, parameters.split(';')))
            return cls(type, subtype, parsed_parameters)
        return cls(type, subtype)

    def __init__(
        self, type: str, subtype: str, parameters: Optional[List[Parameter]] = None
    ):
        self.type = type
        self.subtype = subtype
        self.parameters = parameters or []

    def __str__(self) -> str:
        result = f'{self.type}/{self.subtype}'
        if len(self.parameters) > 0:
            result += '; ' + '; '.join(map(str, self.parameters))
        return result

    def __eq__(self, media_type):
        return (
            isinstance(media_type, MediaType)
            and self.type == media_type.type
            and self.subtype == media_type.subtype
            and self.parameters == media_type.parameters
        )

    def __contains__(self, name: str) -> bool:
        """
        >>> media_type = MediaType('text', 'plain', [('charset', 'utf-8')])
        >>> 'charset' in media_type
        True
        """

        for parameter in self.parameters:
            if parameter.name == name:
                return True

        return False

    def __getitem__(self, name: str) -> Optional[str]:
        """
        >>> media_tye = MediaType('text', 'plain', [('charset', 'utf-8')])
        >>> media_type['charset']
        'utf-8'
        """

        for parameter in self.parameters:
            if parameter.name == name:
                return parameter.value

        raise KeyError(name)
