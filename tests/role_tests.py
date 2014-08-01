#encoding: utf8
import os
import binascii
from bson.objectid import ObjectId
from paqroles.permission import Permission, SuperPermission
from paqroles.role import Role


def objid():
        return ObjectId(binascii.hexlify(os.urandom(12)).decode('utf-8'))


def scaffold_sql_style_locals():
    is_self = lambda user, model: user.id == model.id
    is_own = lambda user, model: user.id == model.user.id

    client_role = Role('client', [
            Permission('shop.OrderView.index'),
            Permission('shop.OrderView.create'),
            Permission('shop.OrderView.detail')(is_own),
            Permission('application.ClientView.edit')(is_self),
        ]
    )

    manager_role = Role('manager', [
            ~Permission('shop.OrderView.create'),   # Orders are created from basket
            Permission('shop.OrderView'),
            Permission('application.ClientView'),
        ]
    )

    superadmin_role = Role('superadmin', [
            ~Permission('shop.OrderView.create'),   # Orders are created from basket
            ~Permission('shop.ProductView.create'), # Products are autosynced from other DB
            SuperPermission(),
        ]
    )


    class Order:
        def __init__(self, id, user):
            self.id = id
            self.user = user

    class User:
        def __init__(self, id):
            self.id = id

    class Client(User):
        pass

    class Manager(User):
        pass

    class SuperAdmin(User):
        pass


    superadmin = SuperAdmin(id=1)
    manager1 = Manager(id=10)
    manager2 = Manager(id=20)
    client1 = Client(id=100)
    client2 = Client(id=200)
    order_of_client1 = Order(id=1, user=client1)
    order_of_client2 = Order(id=2, user=client2)

    return locals()


def scaffold_mongo_fk_style_locals():
    is_self = lambda user, model: user['_id'] == model['_id']
    is_own = lambda user, model: user['_id'] == model['user_id']

    client_role = Role('client', [
            Permission('shop.OrderView.index'),
            Permission('shop.OrderView.create'),
            Permission('shop.OrderView.detail')(is_own),
            Permission('application.ClientView.edit')(is_self),
        ]
    )

    manager_role = Role('manager', [
            ~Permission('shop.OrderView.create'),   # Orders are created from basket
            Permission('shop.OrderView'),
            Permission('application.ClientView'),
        ]
    )

    superadmin_role = Role('superadmin', [
            ~Permission('shop.OrderView.create'),   # Orders are created from basket
            ~Permission('shop.ProductView.create'), # Products are autosynced from other DB
            SuperPermission(),
        ]
    )


    class Order(dict):
        pass

    class User(dict):
        pass

    class Client(User):
        pass

    class Manager(User):
        pass

    class SuperAdmin(User):
        pass


    superadmin = SuperAdmin(_id=objid())
    manager1 = Manager(_id=objid())
    manager2 = Manager(_id=objid())
    client1 = Client(_id=objid())
    client2 = Client(_id=objid())
    order_of_client1 = Order(_id=objid(), user_id=client1['_id'])
    order_of_client2 = Order(_id=objid(), user_id=client2['_id'])

    return locals()


def scaffold_mongo_pk_style_locals():
    is_self = lambda user, model: user['_id'] == model['_id']
    is_own_order = lambda user, model: model['_id'] in user['order_ids']

    client_role = Role('client', [
            Permission('shop.OrderView.index'),
            Permission('shop.OrderView.create'),
            Permission('shop.OrderView.detail')(is_own_order),
            Permission('application.ClientView.edit')(is_self),
        ]
    )

    manager_role = Role('manager', [
            ~Permission('shop.OrderView.create'),   # Orders are created from basket
            Permission('shop.OrderView'),
            Permission('application.ClientView'),
        ]
    )

    superadmin_role = Role('superadmin', [
            ~Permission('shop.OrderView.create'),   # Orders are created from basket
            ~Permission('shop.ProductView.create'), # Products are autosynced from other DB
            SuperPermission(),
        ]
    )


    class Order(dict):
        pass

    class User(dict):
        pass

    class Client(User):
        pass

    class Manager(User):
        pass

    class SuperAdmin(User):
        pass


    superadmin = SuperAdmin(_id=objid())
    manager1 = Manager(_id=objid())
    manager2 = Manager(_id=objid())
    order_of_client1 = Order(_id=objid())
    order_of_client2 = Order(_id=objid())
    client1 = Client(_id=objid(), order_ids=[order_of_client1['_id']])
    client2 = Client(_id=objid(), order_ids=[order_of_client2['_id']])

    return locals()


sql_style_locals = scaffold_sql_style_locals()
mongo_fk_style_locals = scaffold_mongo_fk_style_locals()
mongo_pk_style_locals = scaffold_mongo_pk_style_locals()


class RoleTests:
    def test_client_role_shop_OrderView_index(self):
        assert self.client_role.allows('shop.OrderView.index')

    def test_client_role_shop_OrderView_detail(self):
        assert self.client_role.allows('shop.OrderView.detail', self.client1, self.order_of_client1)
        assert not self.client_role.allows('shop.OrderView.detail', self.client1, self.order_of_client2)
        assert not self.client_role.allows('shop.OrderView.detail')

    def test_client_role_shop_OrderView_edit(self):
        assert not self.client_role.allows('shop.OrderView.edit', self.client1, self.order_of_client1)
        assert not self.client_role.allows('shop.OrderView.edit', self.client1, self.order_of_client2)
        assert not self.client_role.allows('shop.OrderView.edit')

    def test_client_role_shop_OrderView_create(self):
        assert self.client_role.allows('shop.OrderView.create')

    def test_client_role_shop_OrderView(self):
        assert not self.client_role.allows('shop.OrderView')

    def test_client_role_shop_ProductView_create(self):
        assert not self.client_role.allows('shop.ProductView.create')

    def test_client_role_shop_ProductView(self):
        assert not self.client_role.allows('shop.ProductView')

    def test_client_role_shop(self):
        assert not self.client_role.allows('shop')

    def test_client_role_application_UserViews_create(self):
        assert not self.client_role.allows('application.ClientView.create')
        assert not self.client_role.allows('application.ManagerView.create')
        assert not self.client_role.allows('application.SuperAdminView.create')

    def test_client_role_application_UserViews(self):
        assert not self.client_role.allows('application.ClientView')
        assert not self.client_role.allows('application.ManagerView')
        assert not self.client_role.allows('application.SuperAdminView')

    def test_client_role_application(self):
        assert not self.client_role.allows('application')


    def test_manager_role_shop_OrderView_index(self):
        assert self.manager_role.allows('shop.OrderView.index')

    def test_manager_role_shop_OrderView_detail(self):
        assert self.manager_role.allows('shop.OrderView.detail', self.manager1, self.order_of_client1)
        assert self.manager_role.allows('shop.OrderView.detail', self.manager1, self.order_of_client2)
        assert self.manager_role.allows('shop.OrderView.detail')

    def test_manager_role_shop_OrderView_edit(self):
        assert self.manager_role.allows('shop.OrderView.edit', self.manager1, self.order_of_client1)
        assert self.manager_role.allows('shop.OrderView.edit', self.manager1, self.order_of_client2)
        assert self.manager_role.allows('shop.OrderView.edit')

    def test_client_role_shop_OrderView_create(self):
        assert not self.manager_role.allows('shop.OrderView.create')

    def test_manager_role_shop_OrderView(self):
        assert self.manager_role.allows('shop.OrderView')

    def test_manager_role_shop_ProductView_create(self):
        assert not self.manager_role.allows('shop.ProductView.create')

    def test_manager_role_shop_ProductView(self):
        assert not self.manager_role.allows('shop.ProductView')

    def test_manager_role_shop(self):
        assert not self.manager_role.allows('shop')

    def test_manager_role_application_UserViews_create(self):
        assert self.manager_role.allows('application.ClientView.create')
        assert not self.manager_role.allows('application.ManagerView.create')
        assert not self.manager_role.allows('application.SuperAdminView.create')

    def test_manager_role_application_UserViews(self):
        assert self.manager_role.allows('application.ClientView')
        assert not self.manager_role.allows('application.ManagerView')
        assert not self.manager_role.allows('application.SuperAdminView')

    def test_manager_role_application(self):
        assert not self.manager_role.allows('application')


    def test_superadmin_role_shop_OrderView_index(self):
        assert self.superadmin_role.allows('shop.OrderView.index')

    def test_superadmin_role_shop_OrderViews_detail(self):
        assert self.superadmin_role.allows('shop.OrderView.detail', self.superadmin, self.order_of_client1)
        assert self.superadmin_role.allows('shop.OrderView.detail', self.superadmin, self.order_of_client2)
        assert self.superadmin_role.allows('shop.OrderView.detail')

    def test_superadmin_role_shop_OrderView_edit(self):
        assert self.superadmin_role.allows('shop.OrderView.edit')

    def test_superadmin_role_shop_OrderView_create(self):
        assert not self.superadmin_role.allows('shop.ProductView.create')

    def test_superadmin_role_shop_OrderView(self):
        assert self.superadmin_role.allows('shop.OrderView')

    def test_superadmin_role_shop_ProductView_create(self):
        assert not self.superadmin_role.allows('shop.ProductView.create')

    def test_superadmin_role_shop_ProductView(self):
        assert self.superadmin_role.allows('shop.ProductView')


    def test_superadmin_role_shop(self):
        assert self.superadmin_role.allows('shop')

    def test_superadmin_role_application_UserViews_create(self):
        assert self.superadmin_role.allows('application.ClientView.create')
        assert self.superadmin_role.allows('application.ManagerView.create')
        assert self.superadmin_role.allows('application.SuperAdminView.create')

    def test_superadmin_role_application_UserViews(self):
        assert self.superadmin_role.allows('application.ClientView')
        assert self.superadmin_role.allows('application.ManagerView')
        assert self.superadmin_role.allows('application.SuperAdminView')

    def test_superadmin_role_application(self):
        assert self.superadmin_role.allows('application')


class TestSQLStyle(RoleTests):
    client_role = sql_style_locals['client_role']
    manager_role = sql_style_locals['manager_role']
    superadmin_role = sql_style_locals['superadmin_role']

    superadmin = sql_style_locals['superadmin']
    manager1 = sql_style_locals['manager1']
    manager2 = sql_style_locals['manager2']
    client1 = sql_style_locals['client1']
    client2 = sql_style_locals['client2']
    order_of_client1 = sql_style_locals['order_of_client1']
    order_of_client2 = sql_style_locals['order_of_client2']


class TestMongoFKStyle(RoleTests):
    client_role = mongo_fk_style_locals['client_role']
    manager_role = mongo_fk_style_locals['manager_role']
    superadmin_role = mongo_fk_style_locals['superadmin_role']

    superadmin = mongo_fk_style_locals['superadmin']
    manager1 = mongo_fk_style_locals['manager1']
    manager2 = mongo_fk_style_locals['manager2']
    client1 = mongo_fk_style_locals['client1']
    client2 = mongo_fk_style_locals['client2']
    order_of_client1 = mongo_fk_style_locals['order_of_client1']
    order_of_client2 = mongo_fk_style_locals['order_of_client2']


class TestMongoPKStyle(RoleTests):
    client_role = mongo_pk_style_locals['client_role']
    manager_role = mongo_pk_style_locals['manager_role']
    superadmin_role = mongo_pk_style_locals['superadmin_role']

    superadmin = mongo_pk_style_locals['superadmin']
    manager1 = mongo_pk_style_locals['manager1']
    manager2 = mongo_pk_style_locals['manager2']
    client1 = mongo_pk_style_locals['client1']
    client2 = mongo_pk_style_locals['client2']
    order_of_client1 = mongo_pk_style_locals['order_of_client1']
    order_of_client2 = mongo_pk_style_locals['order_of_client2']


class TestXxx:
    def test(self):
        has_access_to_blacklist = lambda user, model=None: user['has_access_to_blacklist']
        role = Role('client', [
                Permission('blacklist')(has_access_to_blacklist),
            ]
        )
        assert role.allows('blacklist', user={'has_access_to_blacklist': True})
        assert not role.allows('blacklist', user={'has_access_to_blacklist': False})


def test_add():
    role1 = Role('ROLE1', ['x'])
    role2 = Role('ROLE1', ['y'])
    role12 = role1 + role2
    role21 = role2 + role1

    # CHECK IMMUTABILITY
    assert role1.permissions == ['x']
    assert role2.permissions == ['y']

    # CHECK LOGIC
    assert role12.permissions == ['x', 'y']
    assert role21.permissions == ['y', 'x']
