from peewee import (SqliteDatabase,
                    CharField,
                    BooleanField,
                    Model,
                    IntegerField,
                    ForeignKeyField,
                    DateField,
                    DeferredRelation,
                    )

import os

DBPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      'coffee.db')

db = SqliteDatabase(DBPATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    name = CharField(null=True)
    email = CharField(default='')
    active = BooleanField(default=True)
    vip = BooleanField(default=False)
    admin = BooleanField(default=False)

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active

    def __str__(self):
        return 'User `{}`'.format(self.username)


class Transaction(BaseModel):
    date = DateField()
    user = ForeignKeyField(User, null=True)
    discription = CharField()
    diff = IntegerField()


class Budget(BaseModel):
    amount = IntegerField()
    transaction = ForeignKeyField(Transaction)


class Service(BaseModel):
    start_date = DateField()
    end_date = DateField()
    user = ForeignKeyField(User)
    service_count = IntegerField()


class Consumption(BaseModel):
    date = DateField()
    units = IntegerField()
    price_per_unit = IntegerField()
