#encoding: utf8
from paqroles.permission import Permission


class Order(object):
    def __init__(self, id, user):
        self.id = id
        self.user = user


class User(object):
    def __init__(self, id):
        self.id = id


def test_assembling():
    assert Permission('shop').mask == 'shop'
    assert Permission('shop')('OrderView').mask == 'shop.OrderView'
    assert Permission('shop')('OrderView')('create').mask == 'shop.OrderView.create'

    filter = lambda: True # dummy function just for example

    assert Permission('shop')('OrderView')('edit')(filter).filters == [filter]


def test_allows_package_against_same_package():
    p = Permission('shop')
    assert p.allows('shop.OrderView.create') is True
    assert p.allows('shop.OrderView') is True
    assert p.allows('shop') is True


def test_allows_package_against_other_package():
    p = Permission('shop')
    assert p.allows('somepackage.SomeView.create') is None
    assert p.allows('somepackage.SomeView') is None
    assert p.allows('somepackage') is None


def test_allows_view():
    p = Permission('shop.OrderView')
    assert p.allows('shop.OrderView.create') is True
    assert p.allows('shop.OrderView') is True
    assert p.allows('shop') is None


def test_allows_action():
    p = Permission('shop.OrderView.create')
    assert p.allows('shop.OrderView.create') is True
    assert p.allows('shop.OrderView') is None
    assert p.allows('shop') is None


def test_allows_inverse_package_against_same_package():
    p = ~Permission('shop')
    assert p.allows('shop.OrderView.create') is False
    assert p.allows('shop.OrderView') is False
    assert p.allows('shop') is False


def test_allows_inverse_package_against_other_package():
    p = ~Permission('shop')
    assert p.allows('somepackage.SomeView.create') is None
    assert p.allows('somepackage.SomeView') is None
    assert p.allows('somepackage') is None


def test_allows_inverse_view():
    p = ~Permission('shop.OrderView')
    assert p.allows('shop.OrderView.create') is False
    assert p.allows('shop.OrderView') is False
    assert p.allows('shop') is None


def test_allows_inverse_action():
    p = ~Permission('shop.OrderView.create')
    assert p.allows('shop.OrderView.create') is False
    assert p.allows('shop.OrderView') is None
    assert p.allows('shop') is None


def test_filters_own_account():
    user1 = User(id=1)
    user2 = User(id=2)

    is_self = lambda user, model: user.id == model.id

    p = Permission('application.UserView.delete')(is_self)
    assert p.allows('application.UserView.delete', user1, user1)
    assert p.allows('application.UserView.delete', user2, user2)
    assert not p.allows('application.UserView.delete', user1, user2)
    assert not p.allows('application.UserView.delete', user2, user1)


def test_filters_own_orders():
    user1 = User(id=1)
    user2 = User(id=2)

    order_of_user1 = Order(id=1, user=user1)
    order_of_user2 = Order(id=2, user=user2)

    is_own = lambda user, model: user.id == model.user.id

    p = Permission('shop.OrderView.delete')(is_own)
    assert p.allows('shop.OrderView.delete', user1, order_of_user1)
    assert p.allows('shop.OrderView.delete', user2, order_of_user2)
    assert not p.allows('shop.OrderView.delete', user1, order_of_user2)
    assert not p.allows('shop.OrderView.delete', user2, order_of_user1)


def test_filters_special_permission():
    user1 = User(id=1)
    user2 = User(id=2)
    user1.shopping_allowed = True
    user2.shopping_allowed = False

    shopping_allowed = lambda user: user.shopping_allowed

    p = Permission('shop')(shopping_allowed)
    assert p.allows('shop', user1)
    assert p.allows('shop.OrderView', user1)
    assert p.allows('shop.OrderView.create', user1)
    assert p.allows('shop.OrderView.delete', user1)
    assert not p.allows('shop', user2)
    assert not p.allows('shop.OrderView', user2)
    assert not p.allows('shop.OrderView.create', user2)
    assert not p.allows('shop.OrderView.delete', user2)


def test_overlapping_masks():
    p = Permission('application')
    assert not p.allows('app')

    p = Permission('app')
    assert not p.allows('application')


def test_xxx():
    has_access_to_blacklist = lambda user, model=None: user['has_access_to_blacklist']

    p = Permission('blacklist')(has_access_to_blacklist)
    assert p.allows('blacklist.index_manage', user={'has_access_to_blacklist': True})