from ldap3 import Server, Connection
from config import (LDAP_HOST,
                    LDAP_PORT,
                    LDAP_SEARCH_BASE,
                    DEBUG,
                    USE_LDAP,
                    TESTING)
from database import User
from flask_login import login_user


def ldap_authenticate(username, password):
    # the guest user is special
    assert(username != 'guest')
    try:
        ldap_server = Server(LDAP_HOST, port=LDAP_PORT)
        base_dn = LDAP_SEARCH_BASE
        ldap_conn = Connection(ldap_server,
                               "uid={},{}".format(username, base_dn),
                               password,
                               auto_bind=True)
        if ldap_conn.search(base_dn,
                            '(&(objectclass=person)(uid={}))'.format(username),
                            attributes=['mail', 'cn']):
            return ldap_conn.entries
    except:
        pass

    return None


def ldap_login(username, password, remember=False):
    if DEBUG and not USE_LDAP:
        try:
            user = User.objects.get(username=username)
            user.admin = True
        except:
            user = User(username=username, name=username, admin=True,
                        active=True, email='dev@coffee.dev').save()
            warning = 'User did not exist, admin user created.'
            flash(warning)
        login_user(user, remember=remember)
        return True

    data = ldap_authenticate(username, password)
    if data:
        try:
            user = User.objects.get(username=username)
        except:
            user = User(username=username)
        user.name = str(data[0]['cn'])
        try:
            user.email = str(data[0]['mail'])
        except KeyError:
            print('A user has no mail entry in LDAP!')
        user.active = True
        user.save()
        login_user(user, remember=remember)
        return True
    else:
        return False


def user_login(username, password, remember=False):
    return ldap_login(username, password, remember=remember)
