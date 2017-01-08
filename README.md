# Coffee user management

This project is based on the initial work of @ibab's python-coffee.
You can manage the budget and consume of a group of coffee users.
Users can update their consumption on a simple web-interface, which fits nicely
into some low-budget tablet.

Development:

```
pip install -r requirements.txt
COFFEE_DEBUG=True COFFEE_LDAP=False python coffee.py
```

```
npm install
npm start
```

Go to `http://localhost:5000/app/?jsdev=true` if you want to develop javascript
stuff and the `webpack-dev-server` is running (aka `npm start`).
