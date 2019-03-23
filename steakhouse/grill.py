import datetime
import json
import logging
import sys
import time
from peewee import (
    fn,
    IntegrityError,
    JOIN,
    Select,
    Value,
)

from steakhouse.models import (
    STATUS_BURNED,
    STATUS_WELLDONE,
    STATUS_MEDIUM,
    STATUS_RAW,
    database,
    Grill,
    GrillSpice,
    Steak,
    SteakGrill,
    SteakSpice,
)


logger = logging.getLogger(__name__)


class GrillMaster:
    def __init__(self, recipes):
        self.recipes = recipes.copy()
        self.recipe_names = list(self.recipes.keys())
        self.grill = Grill.create()
        logger.info("Starting new grill {} with recipes {}".format(self.grill.id, self.recipe_names))

    def _find_next_steak(self):
        # Seems like queries cannot be reused...
        ## Prepare query to search for the next available steak
        # Create subquery that counts the number of grills (max 1) to hold a spice
        subquery = SteakSpice.select(SteakSpice.spice.alias('spice'), fn.COUNT(GrillSpice.id.distinct()).alias('in_use'))
        subquery = subquery.join(GrillSpice, JOIN.LEFT_OUTER, on=(SteakSpice.spice==GrillSpice.spice))
        subquery = subquery.group_by(SteakSpice.spice)

        # Select all raw steaks without a grill and attach a flag whether any spices are in use
        query = Steak.select(Steak.id.alias('steak_id'), fn.COALESCE(fn.SUM(subquery.c.in_use), 0).alias('spice_in_use'))
        query = query.join(SteakGrill, JOIN.LEFT_OUTER)
        query = query.switch(Steak).join(SteakSpice, JOIN.LEFT_OUTER)
        query = query.join(subquery, JOIN.LEFT_OUTER, on=subquery.c.spice == SteakSpice.spice).group_by(Steak.id)
        query = query.where(Steak.status == STATUS_RAW).where(SteakGrill.grill == None)
        query = query.where(Steak.recipe.in_(self.recipe_names))

        # Select the steaks with no spices in use
        steak_query = Steak.select().join(query, JOIN.INNER, on=(Steak.id == query.c.steak_id)).where(query.c.spice_in_use == 0)

        # Return oldest steak
        return steak_query.order_by(Steak.created).first()


    def _fetch_steak(self):
        # Find next available steak
        steak = self._find_next_steak()
        if not steak:
            return None
        # Try to grab it and it's spices
        try:
            with database.atomic():
                SteakGrill.create(steak=steak, grill=self.grill)
                GrillSpice.insert_from(
                    steak.steakspice_set.select(Value(self.grill.id.hex), SteakSpice.spice),
                    fields=[GrillSpice.grill, GrillSpice.spice],
                ).execute()
        except IntegrityError:
            return None
        # Now we are in charge
        logger.info("New steak on the grill: {}:{}".format(steak.id, steak.recipe))
        return steak


    def _roast_steak(self, steak):
        try:
            recipe = RECIPES[steak.recipe]
            parameters = json.loads(steak.parameters or "{}")
        except KeyError as e:
            steak.status = STATUS_BURNED
            steak.finished = datetime.datetime.now()
            steak.result = str(e)
            steak.save()
            return
        steak.status = STATUS_MEDIUM
        steak.started = datetime.datetime.now()
        steak.save()
        try:
            result = recipe(**parameters)
            steak.result = json.dumps(result)
        except Exception as e:
            steak.status = STATUS_BURNED
            steak.finished = datetime.datetime.now()
            steak.result = str(e)
            steak.save()
            return
        steak.status = STATUS_WELLDONE
        steak.finished = datetime.datetime.now()
        steak.save()


    def _return_spices(self, steak):
        GrillSpice.delete().where(GrillSpice.grill == self.grill).where(GrillSpice.spice.in_(steak.steakspice_set.select(SteakSpice.spice))).execute()


    def __call__(self):
        logger.info('Start grilling')
        shutdown = False
        while not shutdown:
            steak = self._fetch_steak()
            if steak:
                self._roast_steak(steak)
                self._return_spices(steak)
                continue
            time.sleep(1)


if __name__ == '__main__':

    def sleep_task(duration=1):
        logger.info('Starting sleep {}'.format(duration))
        time.sleep(duration)
        logger.info('Finishing sleep {}'.format(duration))


    RECIPES = {
        'sleep': sleep_task,
    }


    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    grill_master = GrillMaster(RECIPES)
    grill_master()
