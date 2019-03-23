import datetime
import logging
import sys
from peewee import (
    JOIN,
)

from steakhouse.models import (
    Grill,
    GrillSpice,
    Steak,
    SteakGrill,
    STATUS_BURNED,
    STATUS_MEDIUM,
)


logger = logging.getLogger(__name__)


def scrub_grill(grill):
    subquery = SteakGrill.select(SteakGrill.steak).where(SteakGrill.grill == grill)
    Steak.update(finished=datetime.datetime.now(), status=STATUS_BURNED).where(Steak.status == STATUS_MEDIUM).where(Steak.id.in_(subquery)).execute()
    GrillSpice.delete().where(GrillSpice.grill == grill).execute()


def main():
    grill = Grill.get()
    scrub_grill(grill)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
