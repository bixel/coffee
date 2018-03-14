import random
import pendulum

from database import Consumption, Service, Achievement, AchievementDescriptions
from config import COFFEE_PRICES


@Consumption.achievement_function
def FirstCoffeeOfTheDay(consumption):
    # define some motivational descriptions
    description_pool = (AchievementDescriptions
            .objects(key='first_coffee_of_the_day').first().descriptions)
    # first, get the date of the last coffee
    last_day = Consumption.objects.order_by('-date').first().date.date()
    if consumption.date.date() > last_day:
        new = Achievement(description=random.choice(description_pool),
                          key='first_coffee_of_the_day')
        consumption.user.achievements.append(new)
        consumption.user.save()


@Consumption.achievement_function
def SymmetricCoffee(consumption):
    description_pool = (AchievementDescriptions
            .objects(key='symmetric_coffee').first().descriptions)
    # first get all of todays coffees for current user
    coffees = Consumption.objects(user=consumption.user, date__gte=pendulum.today)
    p1, p2 = [p[0] for p in COFFEE_PRICES]
    todays_coffees = [c.price_per_unit for c in coffees] + [consumption.price_per_unit]
    if todays_coffees == [p1, p2, p1, p1, p2, p1]:
        new = Achievement(description=random.choice(description_pool),
                          key='symmetric_coffee')
        consumption.user.achievements.append(new)
        consumption.user.save()
