#!/usr/bin/python

"""Consumer that simply calls SQL query for each event.

It tracks completed batches in local file.

Config::
    # source database
    src_db =

    # destination database
    dst_db =

    # query to call
    dst_query = select * from somefunc(%%(pgq.ev_data)s);
"""


import sys

import pkgloader
pkgloader.require('skytools', '3.0')

import pgq
import skytools

class SimpleLocalConsumer(pgq.LocalConsumer):
    __doc__ = __doc__

    def reload(self):
        super(SimpleLocalConsumer, self).reload()
        self.dst_query = self.cf.get("dst_query")

    def process_local_event(self, db, batch_id, ev):
        curs = self.get_database('dst_db', autocommit = 1).cursor()

        if ev.ev_type[:2] not in ('I:', 'U:', 'D:'):
            return

        if ev.ev_data is None:
            payload = {}
        else:
            payload = skytools.db_urldecode(ev.ev_data)

        payload['pgq.tick_id'] = self.batch_info['cur_tick_id']
        payload['pgq.ev_id'] = ev.ev_id
        payload['pgq.ev_time'] = ev.ev_time
        payload['pgq.ev_type'] = ev.ev_type
        payload['pgq.ev_data'] = ev.ev_data
        payload['pgq.ev_extra1'] = ev.ev_extra1
        payload['pgq.ev_extra2'] = ev.ev_extra2
        payload['pgq.ev_extra3'] = ev.ev_extra3
        payload['pgq.ev_extra4'] = ev.ev_extra4

        self.log.debug(self.dst_query, payload)
        curs.execute(self.dst_query, payload)
        if curs.statusmessage[:6] == 'SELECT':
            res = curs.fetchall()
            self.log.debug(res)
        else:
            self.log.debug(curs.statusmessage)

if __name__ == '__main__':
    script = SimpleLocalConsumer("simple_local_consumer3", "src_db", sys.argv[1:])
    script.start()

