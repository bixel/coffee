# Coffee user management

This project is based on the initial work of @ibab's python-coffee.
You can manage the budget and consume of a group of coffee users.
Users can update their consumption on a simple web-interface, which fits nicely
into some low-budget tablet.

## Dev-Setup

**tl;dr:** Read and copy paste the following code snippet to get the
development server running. You will need
- python3.7 (`brew install python3`)
- docker (`brew cask install docker`)
- node (`brew install node`)
- ldap client (usually available on osx anyway)

before you
```
source start-dev.sh
```
and login with `testuser:foobar` on [localhost:5000](http://localhost:5000).

hit
```
fg
```
and `CTRL-C` two times to stop all processes.

### python requirements

Consider creating a [virtual environment with
pipenv](https://github.com/pypa/pipenv) and install all dependencies:
```
poetry install
```
Activate the environment after that via
```
poetry shell
```
The main service is provided with the flask app within `coffee.py`.
Run the coffee-app by running
```
COFFEE_DEBUG=True FLASK_ENV=development FLASK_APP=coffe.py flask run
```

### database and ldap

Before logging in and playing around you need to start a mongodb instance.
I like to use docker for that and keep the development database within the
virtual environment:
```
mkdir -p $(pipenv --venv)/database/
```
Once the db-directory is available, run the docker container named
`python-coffee`. If you already created this container before, you might need
to delete it first:
```
docker rm coffee-db
```
```
docker run -d --name coffee-db -v $(pipenv --venv)/database/:/data/db -p 27017:27017 mongo
```
This command will mount the local directory `$PWD/database/` in which the
database files will be available throughout different docker sessions.
(Once created via `docker run`, the container can be stopped or started with
`docker stop/start coffee-db`.)

I suggest docker to run a local ldap server to test authentication. If you
already started this container before, you might need to delete it first.
```
docker rm coffee-ldap
```

...before you can create a new container via
```
docker run --name coffee-ldap -d -p 389:389 -e SLAPD_PASSWORD=password -e SLAPD_DOMAIN=coffee.ldap dinkel/openldap
```

If this is set up, you can add some dummy users with password "foobar"
```
ldapadd -x -D cn=admin,dc=coffee,dc=ldap -w password -f ./ldap_test_data.ldif
```

Thanks to user @dinkel for contributing the openldap image.


### react.js webapp

We finally need to install all js-requirements for the webapp
```
npm install
```

The app will be build continuously with
```
npm start
```
Furthermore, all webapp-files will be served by npm at
[localhost:8888](http://localhost:8888).

In debug mode (`COFFEE_DEBUG=True`), you can log in with any user (default
location is [localhost:5000](http://localhost:5000)), the user record will be
created lazily and everyone is admin (be careful).

Afterwards, go to http://localhost:5000/app/?jsdev=true if you want to
develop javascript stuff and the `webpack-dev-server` is running (aka `npm
start`). The `jsdev=true` enables javascript auto-reloading by using
[webpack-dev-sever](https://webpack.github.io/docs/webpack-dev-server.html).
