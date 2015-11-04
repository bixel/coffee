from peewee import (SqliteDatabase,
                    CharField,
                    BooleanField,
                    Model,
                    IntegerField,
                    ForeignKeyField,
                    DateField)

import os

DBPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      'coffee.db')

db = SqliteDatabase(DBPATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    email = CharField()
    active = BooleanField(default=False)
    vip = BooleanField(default=False)
    admin = BooleanField(default=False)


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
