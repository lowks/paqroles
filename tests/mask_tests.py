from paqroles.mask import Mask


def test_instantiation():
    assert Mask('xyz') == 'xyz'
    assert Mask(Mask('xyz')) == 'xyz'


def test_mask_add_mask():
    assert Mask('x') + Mask('y') == 'x.y'
    assert Mask('x') + Mask('.y') == 'x.y'
    assert Mask('x.') + Mask('y') == 'x.y'
    assert Mask('x.') + Mask('.y') == 'x.y'


def test_str_add_mask():
    assert 'x' + Mask('y') == 'x.y'
    assert 'x' + Mask('.y') == 'x.y'
    assert 'x.' + Mask('y') == 'x.y'
    assert 'x.' + Mask('.y') == 'x.y'


def test_mask_add_str():
    assert Mask('x') + 'y' == 'x.y'
    assert Mask('x') + '.y' == 'x.y'
    assert Mask('x.') + 'y' == 'x.y'
    assert Mask('x.') + '.y' == 'x.y'


def test_mask_allows_str():
    assert Mask('x').allows('x')
    assert not Mask('x').allows('y')
    assert Mask('x').allows('x.x')
    assert not Mask('x.x').allows('x')
    assert not Mask('x').allows('xx')
    assert not Mask('xx').allows('x')
    assert not Mask('x.x').allows('xx')
    assert not Mask('xx').allows('x.x')


def test_mask_allows_mask():
    assert Mask('x').allows(Mask('x'))
    assert not Mask('x').allows(Mask('y'))
    assert Mask('x').allows(Mask('x.x'))
    assert not Mask('x.x').allows(Mask('x'))
    assert not Mask('x').allows(Mask('xx'))
    assert not Mask('xx').allows(Mask('x'))
    assert not Mask('x.x').allows(Mask('xx'))
    assert not Mask('xx').allows(Mask('x.x'))