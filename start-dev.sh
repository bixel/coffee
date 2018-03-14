if [ ! -d "$PWD/env/" ]; then
    python3 -m venv env
    mkdir -p $PWD/env/database/
fi

source $PWD/env/bin/activate
pip install -r requirements.txt
docker start coffee-db || docker run -d --name coffee-db -v $PWD/env/database/:/data/db -p 27017:27017 mongo
docker start coffee-ldap || docker run --name coffee-ldap -d -p 389:389 -e SLAPD_PASSWORD=password -e SLAPD_DOMAIN=coffee.ldap dinkel/openldap
ldapadd -x -D cn=admin,dc=coffee,dc=ldap -w password -f ./ldap_test_data.ldif
npm install
npm start &
COFFEE_DEBUG=True python coffee.py &
