from rivr.http.media_type import MediaType, Parameter


def test_parse_media_type():
    media_type = MediaType.parse('text/plain')
    assert media_type.type == 'text'
    assert media_type.subtype == 'plain'
    assert len(media_type.parameters) == 0

    media_type = MediaType.parse('text/plain; charset=utf-8; other="quoted string"')
    assert media_type.type == 'text'
    assert media_type.subtype == 'plain'
    assert media_type.parameters == [
        Parameter('charset', 'utf-8'),
        Parameter('other', 'quoted string'),
    ]


def test_str():
    media_type = MediaType('text', 'plain')
    assert str(media_type) == 'text/plain'

    media_type = MediaType(
        'text',
        'plain',
        [
            Parameter('charset', 'utf-8'),
            Parameter('other', 'string'),
        ],
    )

    assert str(media_type) == 'text/plain; charset=utf-8; other=string'


def test_contains():
    media_type = MediaType(
        'text',
        'plain',
        [
            Parameter('charset', 'utf-8'),
        ],
    )

    assert 'charset' in media_type
    assert 'unknown' not in media_type


def test_get():
    media_type = MediaType(
        'text',
        'plain',
        [
            Parameter('charset', 'utf-8'),
        ],
    )

    assert media_type['charset'] == 'utf-8'
