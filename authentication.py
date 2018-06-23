from ldap3 import (
        Server, Connection, ANONYMOUS, AUTO_BIND_TLS_BEFORE_BIND, ALL,
        AUTO_BIND_NO_TLS,
        )
from ldap3.core.exceptions import LDAPBindError
from ldap3.extend.standard.whoAmI import WhoAmI
import config
from database import User
from flask_login import login_user
from flask import flash


if config.LDAP_TLS:
    auto_bind = AUTO_BIND_TLS_BEFORE_BIND
else:
    auto_bind = AUTO_BIND_NO_TLS


def get_user_dn(username_or_email):
    server = Server(config.LDAP_HOST, port=config.LDAP_PORT, get_info=ALL)

    # either do a bind + search for the DN...
    if config.LDAP_SEARCH_BIND and config.LDAP_SEARCH_PASSWORD:
        connection = Connection(
                server, config.LDAP_SEARCH_BIND, config.LDAP_SEARCH_PASSWORD,
                auto_bind=auto_bind,
                )
    # warn the user if the configuration is unclear
    elif any((config.LDAP_SEARCH_BIND, config.LDAP_SEARCH_PASSWORD)):
        raise ValueError('Configuration unclear. Please provide either both, '
                'LDAP_SEARCH_BIND and LDAP_SEARCH_PASSWORD or none of these')
    # ... or do an anonymous bind to search for the user dn
    else:
        connection = Connection(
                server, auto_bind=auto_bind, authentication=ANONYMOUS,
                )

    connection.search(
            config.LDAP_SEARCH_BASE,
            '(|(uid={0})(mail={0}))'.format(username_or_email)
            )
    return connection.entries[0].entry_dn


def ldap_authenticate(dn, username_or_email, password):
    try:
        ldap_server = Server(
                config.LDAP_HOST, port=config.LDAP_PORT, get_info=ALL,
                )
        ldap_conn = Connection(ldap_server, dn, password, auto_bind=auto_bind)
        if ldap_conn.search(
                dn, '(uid=*)'.format(username_or_email), search_scope='BASE',
                attributes=['mail', 'cn', 'uid'],
                ):
            return ldap_conn.entries
    except LDAPBindError as e:
        if config.DEBUG:
            print(e)
        return None
    except Exception as e:
        raise e


def ldap_login(username, password, remember=False):
    if config.DEBUG and not config.USE_LDAP:
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

    if username == 'guest':
        return False

    user_dn = get_user_dn(username)
    data = ldap_authenticate(user_dn, username, password)
    if data:
        username = data[0]['uid'][0]
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            user = User(username=username)
        user.name = str(data[0]['cn'])
        if data[0]['mail']:
            user.email = str(data[0]['mail'])
        else:
            print('A user has no mail entry in LDAP!')
        user.active = True
        user.save()
        login_user(user, remember=remember)
        return True
    else:
        return False


def user_login(username, password, remember=False):
    return ldap_login(username, password, remember=remember)
