# vocabulary-storage

App vocabulary-storage allow:

  - Register in app
  - Add words in storage one by one
  - Upload words from local file all at once
  - See your vocabulary
  - edit or/and delete words from vocabulary
  - Send your words in your e-mail
  - Test your vocabulary in different ways
  - look at others' vocabulary
  - add words to your vocabulary from other's
### Tech

vocabulary-storage uses a number of open source projects to work properly:

* Python3
* Flask
* SQLite
* Jinja2
* wtforms
* werkzeug
* sqlalchemy

### Installation



Install the dependencies and devDependencies and start the server.

```sh
$ cd vocabulary-storage
$ pip install -r requirements.txt
$ flask db init
$ flask db migrate
$ flask db upgrade
$ export FLASK_APP=vocabulary_storage.py
$ flask run
```

For production environment...

```sh
$ python3 -m venv venv
$ source venv/bin/activate
```

Verify the deployment by navigating to your server address in your preferred browser.

```sh
127.0.0.1:5000
```

### Todos

 - action **Follow**
 - rank words by their accuracy

License
----

GPL
