import mqm


def test_initialize():
    initialized = mqm.GeoProcessor('')
    assert initialized is not None

