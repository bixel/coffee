# Coffee user management

This project is based on the initial work of @ibab's python-coffee.
You can manage the budget and consume of a group of coffee users.
Users can update their consumption on a simple web-interface, which fits nicely
into some low-budget tablet.

## Dev-Setup
Consider creating a [virtual environment with
python-venv](https://docs.python.org/3/library/venv.html).
The main service is provided with the flask app within `coffee.py`.
You can install all requirements and run the server via
```
pip install -r requirements.txt
COFFEE_DEBUG=True COFFEE_LDAP=False python coffee.py
```

The webapp for "Kaffeeliste 2.0" will be built with
```
npm install
npm start
```

In debug mode, you can log in with any user (default location is
[localhost:5000](http://localhost:5000)), the use record will be created lazily
and everyone is admin.

Afterwards, go to http://localhost:5000/app/?jsdev=true if you want to
develop javascript stuff and the `webpack-dev-server` is running (aka `npm
start`). The `jsdev=true` enables javascript auto-reloading by using
[webpack-dev-sever](https://webpack.github.io/docs/webpack-dev-server.html).

## Docker
There is also a Dockerfile which uses miniconda and installs everything needed
to serve the coffee app.
Since a simple SQLite database is used to store the app data, you need
to mount a volume and set the `COFFEE_DB` environment variable to some
SQLite file in that volume to persistify the data.
