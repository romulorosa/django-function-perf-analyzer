# Django function performance analyzer

This is a simple script with a function which can be used as a decorator or wrapper and print a simple report of function execution. This function will measure the execution time of a given function and compute the time spent by the queries executed on database. Functions like that can be usefull in situations when you need tunning or find some bottlenecks. This will give you a directive about which is the slowest part of your function.

## How to use
**IMPORTANT**: You should turn on the django debug mode (settings.DEBUG = True)

As a function decorator:
```
@function_perf
def foo():
   import time
   print 'Searching on my db...'
   users = Users.objects.filter(pk__gte=10)
   books = Books.objects.filter(title__icontains='History')
   sales = Sales.objects.filter(sales__users__in=users)
   time.sleep(2)
   print 'Found {} users'.format(users.count())
```

As a function wrapper:
```
function_perf(process_my_report)(type='sales', file_format='xlsx', extra=kwargs)
```

Otput example:
```
---------------------------------------- ANALYSIS REPORT ----------------------------------------

TOP 10 slowest queries

Function total execution time: 2.0840280056s
DB total time: 0.068s

-> Query #1
	Query execution time: 0.062 	(2.975% of total time | 91.1765% of DB time)
	Number of similar queries: 0
	SQL: SELECT "players_user"."id", "players_user"."created", "players_user"."updated" FROM "players_user WHERE "players_user"."pk" = 10 

-> Query #2
	Query execution time: 0.004 	(0.1919% of total time | 5.8824% of DB time)
	Number of similar queries: 0
	SQL: SELECT COUNT(*) FROM "library_books" 
```
