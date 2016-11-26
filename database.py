from peewee import (SqliteDatabase,
                    CharField,
                    BooleanField,
                    Model,
                    IntegerField,
                    ForeignKeyField,
                    DateField,
                    DeferredRelation,
                    fn,
                    JOIN,
                    )

import os
import datetime

FILENAME = os.environ.get('DBFILE') or 'coffee.db'
DBPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      FILENAME)

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

    @property
    def balance(self):
        return self.payments - self.consume

    @property
    def payments(self):
        return (User
                .select(User.id==self.id, fn.SUM(Transaction.diff).alias('_payments'))
                .join(Transaction, JOIN.LEFT_OUTER)
                .get()
                ._payments) or 0

    @property
    def consume(self):
        return (User
                .select(User.id==self.id, fn.SUM(Consumption.units * Consumption.price_per_unit).alias('_consume'))
                .join(Consumption, JOIN.LEFT_OUTER)
                .get()
                ._consume) or 0

    def get_uids():
        users = User.select().order_by(User.username)
        return map(lambda u: (u.id, u.name), users)

    def __str__(self):
        return 'User `{}`'.format(self.username)


class Transaction(BaseModel):
    date = DateField(default=datetime.datetime.now)
    user = ForeignKeyField(User, null=True)
    description = CharField()
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
    date = DateField(default=datetime.datetime.now)
    units = IntegerField(default=1)
    price_per_unit = IntegerField()
    user = ForeignKeyField(User)
