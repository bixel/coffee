import random
import pendulum
import datetime

from flask import flash

from database import Consumption, Service, Achievement, AchievementDescriptions
from config import COFFEE_PRICES


def get_kwargs_for_key(key):
    try:
        description = AchievementDescriptions.objects(key=key).first()
        return {
            'title': description.title,
            'description': random.choice(description.descriptions),
            'validUntil': pendulum.now().add(days=description.validDays)
            }
    except IndexError as e:
        flash(f'Warning: the description pool for \'{key}\' is empty. ({e}).')
        return {
            'title': 'Achievement',
            'description': 'Great! You\'ve got an achievement but the devs were'
                'too lazy to think of a funny description...',
            }
    except AttributeError as e:
        flash(f'Warning: no description pool for \'{key}\' available. Please'
              ' add some descriptions in the database')
        return {
            'title': 'Achievement',
            'description': 'Either you have a new achievement or there was a bug',
            }


@Consumption.achievement_function
def FirstCoffeeOfTheDay(consumption):
    key = 'first_coffee_of_the_day'
    # define some motivational descriptions
    # first, get the date of the last coffee
    last_day = Consumption.objects.order_by('-date').first().date.date()
    if consumption.date.date() > last_day:
        new = Achievement(**get_kwargs_for_key(key), key=key)
        consumption.user.achievements.append(new)
        consumption.user.save()


@Consumption.achievement_function
def SymmetricCoffee(consumption):
    key = 'symmetric_coffee'
    # first get all of todays coffees for current user
    coffees = Consumption.objects(user=consumption.user, date__gte=pendulum.today)
    p1, p2 = [p[0] for p in COFFEE_PRICES]
    todays_coffees = [c.price_per_unit for c in coffees] + [consumption.price_per_unit]
    if todays_coffees == [p1, p2, p1, p1, p2, p1]:
        new = Achievement(**get_kwargs_for_key(key), key=key)
        consumption.user.achievements.append(new)
        consumption.user.save()


@Consumption.achievement_function
def Minimalist(consumption):
    key = 'minimalist'
    n_consumptions_total = len(Consumption.objects(user=consumption.user))

    if n_consumptions_total < 5:
        return

    today = consumption.date
    p1, p2 = [p[0] for p in COFFEE_PRICES]

    last_consumption_date = Consumption.objects(
            user=consumption.user
        ).order_by('-date').first().date

    if not last_consumption_date.weekday() == 4:
        return

    if last_consumption_date.date() == today.date():
        return

    shift = 1 if n_consumptions_total==5 else 0
    if (Consumption.objects(user=consumption.user).order_by('-date')[4-shift].date.date() == \
        Consumption.objects(user=consumption.user).order_by('-date')[5-shift].date.date()):
        return

    complete_week_deltas = [
        datetime.timedelta(i) for i in range(0,5,1)
    ]

    consumptions_to_check = Consumption.objects(
            user=consumption.user
        ).order_by('-date')[0:5]
    for consumption_to_check, delta in zip(
        consumptions_to_check, complete_week_deltas):
        if consumption_to_check.date.date() != (last_consumption_date - delta).date():
            return

        if consumption_to_check.price_per_unit != p1:
            return

    new = Achievement(**get_kwargs_for_key(key), key=key)
    consumption.user.achievements.append(new)
    consumption.user.save()


@Consumption.achievement_function
def professional_stalker(consumption):
    target_user = User.objects.get(username='admin')
    todays_target_consumptions = (Consumption
            .objects(user=target_user, date__gte=pendulum.today())
            .order_by('-date'))
    todays_user_consumptions = (Consumption
            .objects(user=consumption.user, date__gte=pendulum.today())
            .order_by('-date'))
