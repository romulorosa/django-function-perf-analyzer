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
    """
    WARNING: You should set your settings.DEBUG = True

    This function gives a basic performance execution analysis
    measuring the time spent in whole function and computing the
    time spent doing queries on database. The queries will be displayed
    in order of spent time.
    You can use as decorator or simply wrapper.
    Args:
        func: function which will be analyzed
        similar_qry_ratio: the ratio to consider a given query similiar to other.
            This is used because in function execution we can have some query
            executed many times with different arguments.
        max_print: the max number of queries which will be printed on screen

    Returns:
        A simply report of queries executed in function.
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
