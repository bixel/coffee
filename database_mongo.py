from mongoengine import (connect,
                         Document,
                         EmbeddedDocument,
                         StringField,
                         BooleanField,
                         DateTimeField,
                         ReferenceField,
                         IntField,
                         ListField,
                         EmbeddedDocumentField,
                         )

from datetime import datetime

connect('coffeedb')


class Transaction(Document):
    date = DateTimeField(default=datetime.now)
    description = StringField(null=True)
    diff = IntField()
    user = ReferenceField('User', null=True)

    def __str__(self):
        return self.description


class Consumption(Document):
    date = DateTimeField(default=datetime.now)
    units = IntField(default=1)
    price_per_unit = IntField()
    user = ReferenceField('User')

    def __str__(self):
        return '{}\'s consumtion of {} units, {} each'.format(
            self.user.name,
            self.units,
            self.price_per_unit,
        )


class Service(Document):
    date = DateTimeField()
    service_count = IntField(default=1)
    user = ReferenceField('User')


class User(Document):
    username = StringField(required=True, unique=True)
    name = StringField()
    email = StringField()
    active = BooleanField(default=True)
    vip = BooleanField(default=False)
    admin = BooleanField(default=False)

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active

    @property
    def balance(self):
        return self.payments - self.consume

    @property
    def payments(self):
        return 0

    @property
    def consume(self):

        return 0

    @property
    def score(self):
        return 0

    def get_uids():
        return [('1', 'dev')]

    def __str__(self):
        return 'User `{}`'.format(self.username)
