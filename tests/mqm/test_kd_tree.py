import mqm


def test_init():
    initialized = mqm.kdTree(None, None, None, None)
    assert initialized is not None
