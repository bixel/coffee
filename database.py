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
from math import exp
import pendulum
from flask import flash
from config import TZ, ENABLE_ACHIEVEMENTS


class AchievementDocument(Document):
    """ Wrapper class to attach achievements to documents.
    On every save, each function which has been decorated as an achievement
    will be called. This way, possible achievements can be evaluated.
    """
    @classmethod
    def achievement_function(cls, f):
        cls.achievement_functions = getattr(cls, 'achievement_functions', []) + [f]
        return f

    def save(self, *args, **kwargs):
        if ENABLE_ACHIEVEMENTS and type(self).objects.count() > 0:
            # most (all?) achievements only work if there are any instances
            # in the database
            for f in getattr(self, 'achievement_functions', []):
                f(self)
        return super().save(*args, **kwargs)

    meta = {
            'abstract': True,
            }


class Achievement(EmbeddedDocument):
    title = StringField()
    description = StringField()
    key = StringField()
    date = DateTimeField(default=pendulum.now)
    validUntil = DateTimeField(default=lambda: pendulum.now().add(days=7))


class AchievementDescriptions(Document):
    key = StringField()
    title = StringField()
    validDays = IntField()
    descriptions = ListField(StringField())


class Transaction(AchievementDocument):
    date = DateTimeField(default=pendulum.now)
    description = StringField(null=True)
    diff = IntField()
    user = ReferenceField('User', null=True)

    def __str__(self):
        return self.description

    @staticmethod
    def aggregateDaily(objectSelector):
        groupStage = {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$date',
                            }
                        },
                    'total': {
                        '$sum': '$diff',
                        },
                    }
                }
        sortStage = {
                '$sort': {
                    '_id': 1,
                    },
                }
        return objectSelector.aggregate(groupStage, sortStage)

    @staticmethod
    def dailyTransactions():
        return list(Transaction.aggregateDaily(Transaction.objects))

    @staticmethod
    def dailyExpenses():
        return list(Transaction.aggregateDaily(Transaction.objects(user=None)))


class Consumption(AchievementDocument):
    date = DateTimeField(default=pendulum.now)
    units = IntField(default=1)
    price_per_unit = IntField()
    user = ReferenceField('User')

    def __str__(self):
        return '{}\'s consumtion of {} units, {} each'.format(
            self.user.name,
            self.units,
            self.price_per_unit,
        )

    @staticmethod
    def dailyConsumptions():
        groupStage = {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$date'
                            },
                        },
                    'total': {
                        '$sum': {
                            '$multiply': ['$units', '$price_per_unit'],
                            }
                        }
                    }
                }
        sortStage = {
                '$sort': {
                    '_id': 1
                    }
                }
        return list(Consumption.objects.aggregate(groupStage, sortStage))


class Service(AchievementDocument):
    date = DateTimeField()
    service_count = IntField(default=1)
    user = ReferenceField('User')
    master = BooleanField(default=True)
    cleaned = BooleanField(default=False)
    cleaning_program = BooleanField(default=False)
    decalcify_program = BooleanField(default=False)

    @staticmethod
    def current():
        return (Service
                .objects(date__lte=pendulum.now(TZ), master=True)
                .order_by('-date')
                .first()
                )

    @staticmethod
    def upcoming():
        return list(Service.objects.aggregate(
            {
                '$match': {
                    'date': {
                        '$gte': pendulum.now(TZ),
                        },
                    'master': {
                        '$eq': True,
                        },
                    },
                },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'date': '$date',
                            'format': '%Y%V',
                            }
                        },
                    'user': {
                        '$first': '$user'
                        }
                    }
                },
            {
                '$sort': {
                    '_id': 1,
                    },
                }
            ))


class User(Document):
    username = StringField(required=True, unique=True)
    name = StringField()
    email = StringField()
    active = BooleanField(default=True)
    vip = BooleanField(default=False)
    admin = BooleanField(default=False)
    achievements = ListField(EmbeddedDocumentField(Achievement))

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
        return self.backref(
            {'$sum': '$diff'},
            Transaction
        )

    @property
    def consume(self):
        return self.backref(
            {'$sum': {'$multiply': ['$units', '$price_per_unit']}},
            Consumption
        )

    def consumption_list(self):
        match = {'$match': {'user': self.id}}
        # id will be an integer representing YYYYmmdd
        group_id = {
                '$dateToString': {
                    'date': '$date',
                    'format': '%Y%m%d',
                    }
                }
        consume_pipeline = [
            match,
            {
                '$group': {
                    '_id': group_id,
                    'diff': {
                        '$sum': {'$multiply': [-1, '$units', '$price_per_unit']},
                    },
                },
            },
        ]
        transaction_pipeline = [
            match,
            {'$group': {
            '_id': group_id,
            'diff': {
                '$sum': '$diff'
            }}},
        ]
        cs = list(Consumption.objects.aggregate(*consume_pipeline))
        ts = list(Transaction.objects.aggregate(*transaction_pipeline))
        sorted_result = sorted(cs + ts, key=lambda t: t['_id'])
        return [{'amount': t['diff'],
                 'date': pendulum.from_format(t['_id'], 'YYYYMMDD').to_date_string()}
                 for t in sorted_result]

    def backref(self, field, Reference, default=0):
        """ Apply aggregations on Documents referencing the User document.
        """
        pipeline = [
            {
                '$group': {
                    '_id': '$user',
                    'f': field,
                },
            },
        ]
        result = list(Reference.objects(user=self).aggregate(*pipeline))
        if len(result):
            return result[0]['f']
        else:
            return default

    @property
    def last_service(self):
        """ Return the latest service object, where the given user did the
            master service.
        """
        return (Service.objects(user=self.id, master=True, cleaned=True)
                .order_by('-date').first())

    @property
    def score(self):
        if self.vip:
            return 100

        services = 0
        consumptions = 1
        latestService = Service.objects.order_by('-date').first()
        latest = latestService.date if latestService else pendulum.now()
        for s in Service.objects(user=self):
            timediff = latest - s.date
            services += s.service_count * exp(-timediff.days / 365)
        for c in Consumption.objects(user=self):
            timediff = latest - c.date
            units = c.units or 0
            consumptions += units * exp(-timediff.days / 365)
        return services**3 / consumptions

    def delete(self, *args, **kwargs):
        assert(self.username != 'DELETED_USERS')
        try:
            guest_user = User.objects.get(username='DELETED_USERS')
        except:
            flash('No `DELETED_USERS` user found. Skipping Delete.')
            return
        Transaction.objects(user=self).update(user=guest_user)
        Consumption.objects(user=self).update(user=guest_user)
        Service.objects(user=self).update(user=guest_user)
        super().delete(*args, **kwargs)

    def get_uids():
        return [(str(u.id), u.name) for u in User.objects.order_by('name')]

    def __str__(self):
        return 'User `{}`'.format(self.username)
