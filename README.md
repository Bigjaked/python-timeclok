Time Clock
==========

This is a simple time clock that i wrote to keep track of time for different jobs.
It has a pretty simple command line interface and includes a few journaling commands as well.

This program creates a sqlite database at ~/.timeclock/time-clock.db which it stores everything 
in.

## Setup
In order to setup the app you first need to install it. Then you just do the following
I will put some better installation instructions here later, but I don't have time to set 
up a PYPI repo yet. Once I do, you can just install this with pip. For you you have to
Download the repo and install manually.

```shell script
# Create the local sqlite database
python timeclock.py init
```

### Clocking In
```shell script
# clock in
python timeclock.py clock in

# clock in at a certain time
python timeclock.py clock in --when "2020-09-22 08:00:00"
```

### Clocking Out
```shell script
# clock out
python timeclock.py clock out

# clock out a certain time
python timeclock.py clock out --when "2020-09-22 17:00:00"
```

### Adding Past Days
```shell script
# clock in at a certain time
python timeclock.py clock in --when "2020-09-20 08:00:00" --out "2020-09-20 08:00:00"
```

### Showing status
```shell script
# Display current days status
python timeclock.py status
```



### Delete a time clock
First find the ID number of the entry you want to delete using timeclock.py status
then use the following to delete it.
```shell script
# Delete a record from the time log
python timeclock.py clock delete {id}
```

# Journal
This program includes a basic journal that just stores a journal record that has the same
keys as the time clock entries. 

```shell script
# Write a journal entry
python timeclock.py journal m "a message that can contain \n (any special chars)"
```
```shell script
# Write a journal entry for a past time
python timeclock.py journal m  --when "2020-09-22 08:00:00" "message"
```





### Dump to json file
The following command dumps the entire database to a json file. This includes the time clock
entries as well as the journal entries.
```shell script
# Dump the database to ~/.timeclock/time-clock{date-stamp}.json
python timeclock.py dump 

# Dump to specified file
python timeclock.py dump dump-file.json
```