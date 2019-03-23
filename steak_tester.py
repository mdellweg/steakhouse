import logging
import sys

from steakhouse.models import database, Steak, SteakSpice

logger = logging.getLogger(__name__)


def main():
    logger.info('Enter main')
    with database.atomic():
        steak = Steak.create(recipe='sleep', parameters=r'{"duration" : 2}')
    with database.atomic():
        steak = Steak.create(recipe='sleep', parameters=r'{"duration" : 3}')
        SteakSpice.create(steak=steak, spice='Pepper')
    with database.atomic():
        steak = Steak.create(recipe='sleep', parameters=r'{"duration" : 4}')
        SteakSpice.create(steak=steak, spice='Salt')
    with database.atomic():
        steak = Steak.create(recipe='sleep', parameters=r'{"duration" : 5}')
        SteakSpice.create(steak=steak, spice='Pepper')
        SteakSpice.create(steak=steak, spice='Salt')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
