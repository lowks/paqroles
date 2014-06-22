from paqroles.permission import Permission
from paqroles.role import Role


role1 = Role('client', [
        Permission('package1.View1.action1'),
    ]
)

role2 = Role('manager', [
        Permission('package2.View2.action2'),
    ]
)


class UserWithSingleRole(object):
    def __init__(self, id):
        self.id = id

    def allowed(self, permission, model=None):
        return self.role.allows(permission, self, model)


class UserWithMultipleRoles(object):
    def __init__(self, id):
        self.id = id

    def allowed(self, permission, model=None):
        for role in self.roles:
            if role.allows(permission, self, model):
                return True
        return False


class UserWithSingleRole1(UserWithSingleRole):
    role = role1


class UserWithSingleRole2(UserWithSingleRole):
    role = role2


class UserWithMultipleRoles(UserWithMultipleRoles):
    roles = (role1, role2) # Order should better be from most permissive roles to more restrictive


user_with_single_role1 = UserWithSingleRole1(id=1)
user_with_single_role2 = UserWithSingleRole2(id=2)
user_with_multiple_roles = UserWithMultipleRoles(id=3)


def test_user_with_single_role1():
    assert user_with_single_role1.allowed('package1.View1.action1')
    assert not user_with_single_role1.allowed('package2.View2.action2')
    assert not user_with_single_role1.allowed('package3.View3.actio3')


def test_user_with_single_role2():
    assert not user_with_single_role2.allowed('package1.View1.action1')
    assert user_with_single_role2.allowed('package2.View2.action2')
    assert not user_with_single_role2.allowed('package3.View3.action3')


def test_user_with_multiple_roles():
    assert user_with_multiple_roles.allowed('package1.View1.action1')
    assert user_with_multiple_roles.allowed('package2.View2.action2')
    assert not user_with_multiple_roles.allowed('package3.View3.action3')