set -e
if [ $(id -u) -ne 0 ]
    then echo "docker needs sudo priviledges. Please run $0 as root"
    exit
else
    docker start coffee-db || docker run -d --name coffee-db -p 27017:27017 mongo
    docker start coffee-ldap || docker run --name coffee-ldap -d -p 389:389 -e SLAPD_PASSWORD=password -e SLAPD_DOMAIN=coffee.ldap dinkel/openldap
    ldapadd -x -D cn=admin,dc=coffee,dc=ldap -c -w password -f ./testing/ldap_test_data.ldif || true
    npm start &
    export SECRET_KEY=SECRET
    COFFEE_DEBUG=True FLASK_ENV=development FLASK_APP=coffee.py flask run &
fi
