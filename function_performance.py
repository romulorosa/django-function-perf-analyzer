# coding: utf-8
from functools import wraps
from django.db import connection
from difflib import SequenceMatcher
import time


class QueryPerf(object):

    def __init__(self, time=0, sql=''):
        self.time = float(time)
        self.raw_query = sql
        self.similars = 0

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return not self.__lt__(other)

    def __repr__(self):
        return 'Time: {}\nSimilars: {}\nSQL: {} \n'.format(
            self.time,
            self.similars,
            self.raw_query
        )

    def __str__(self):
        return 'Time: {}\nSimilars: {}\nSQL: {} \n'.format(
            self.time,
            self.similars,
            self.raw_query
        )

    def add_time(self, time):
        self.time += time
        self.similars += 1


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def function_perf(func, similar_qry_ratio=0.9, max_print=10):
    """"
        WARNING:
            You MUST have to set DEBUG=True on settings to use this, so run
            this code on specifc container in disposable. DON'T set DEBUG=True
            in production.

        USE CASE:
            Use this to view a rank of query spent time

        USAGE EXAMPLE:
            query_perf(process_report)(target_type='deliveries', file_format='xlsx', extra=kwargs)

    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        connection.queries = []
        func_start_time = time.time()
        ret_val = func(*args, **kwargs)
        func_end_time = time.time()

        db_time = 0
        queries = []
        for qry_info in connection.queries:
            raw_qry = qry_info.get('sql', '')
            time_qry = float(qry_info.get('time', 0))
            db_time += time_qry
            has_similar = False
            for qry in queries:
                # search for similar queries already anylized
                if similar(qry.raw_query, raw_qry) >= similar_qry_ratio:
                    qry.add_time(time_qry)
                    has_similar = True
                    break
            if not has_similar:
                queries.append(QueryPerf(**qry_info))
        queries.sort(reverse=True)

        func_execution_time = func_end_time - func_start_time
        print '\n'+'-'*40+' ANALYSIS REPORT '+'-'*40
        print 'Function total execution time: {}s\nDB total time: {}s\n'.format(
            func_execution_time,
            db_time
        )
        print 'TOP {} slowest queries\n'.format(max_print)
        for idx, q in enumerate(queries[:max_print]):
            print '-> Query #{}'.format(idx+1)
            print '\tQuery execution time: {} ' \
                  '\t({}% of total time | {}% of DB time)\n' \
                  '\tNumber of similar queries: {}\n' \
                  '\tSQL: {} \n'.format(
                q.time,
                round(q.time/func_execution_time, 6)*100,
                round(q.time/db_time, 6)*100,
                q.similars,
                q.raw_query
            )

        return ret_val

    return func_wrapper

