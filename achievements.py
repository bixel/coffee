import random
import pendulum

from database import Consumption, Service, Achievement, AchievementDescriptions
from config import COFFEE_PRICES


def get_description_for_key(key):
    description_pool = (AchievementDescriptions
            .objects(key=key).first().descriptions)
    try:
        return random.choice(description_pool)
    except IndexError as e:
        print(f'Warning: the description pool for \'{key}\' is empty. ({e}).')
        return 'You got an achievement'
    except:
        raise


@Consumption.achievement_function
def FirstCoffeeOfTheDay(consumption):
    key = 'first_coffee_of_the_day'
    # define some motivational descriptions
    # first, get the date of the last coffee
    last_day = Consumption.objects.order_by('-date').first().date.date()
    if consumption.date.date() > last_day:
        new = Achievement(description=get_description_for_key(key), key=key)
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
        new = Achievement(description=get_description_for_key(key), key=key)
        consumption.user.achievements.append(new)
        consumption.user.save()
