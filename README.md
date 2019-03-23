steakhouse
==========

A reliable job queue for steaks (tasks that might take longer, but must not be forgotten).

Concepts
--------

This project aims to provide a steak grill that gives guarantees about the state of its steaks, backed by database constraints.
Steaks are prepared on a grill, while blocking certain spices.
When the grill dies while preparing a steak, a scraper can still update the steaks state to burned and return the blocked spices.
