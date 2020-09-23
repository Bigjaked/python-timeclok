Time Clock
==========

This is a simple time clock app that I wrote to keep track of time for different jobs.
It has a pretty simple command line interface and includes a few journaling commands as well.

This program creates a sqlite database at ~/.timeclock/time-clock.db which it stores everything 
in.

## Setup
In order to setup the app you first need to install it. Then you just do the following
I will put some better installation instructions here later, but I don't have time to set 
up a PYPI repo yet. Once I do, you can just install this with pip. For you you have to
Download the repo and install manually.

## Future plans
* I plan to tie the journal messaging into the time clock directly and deprecate the journal
  commands. I also plan to add more functionality that will allow users to query the 
  database for a certain time span of months, weeks, or days.
* I plan to add the ability to switch between different jobs or projects by specifying a
  different job. I just need to figure out the most intuitive way to do this, while still
  maintaining the simple API that is already implemented. Will probably need to create a 
  default job that is used for all unspecified work.
* Make so when a user can switch jobs just by clocking into a different one. Need to clock
  out the current job at the same time. 


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
# Note: clock out can be called multiple times without calling a new clock in. This
# Will just overwrite the last clock out time with the current time.

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
# (prints the following)
# ID    Date Key   Month  Week   Clock In             Clock Out            Hours 
# 1     20200921   9      38     2020-09-21 08:20:00  2020-09-21 15:32:00  7.2   
# 2     20200922   9      38     2020-09-22 08:03:00  2020-09-22 10:00:00  1.95  
# 3     20200922   9      38     2020-09-22 12:30:00  2020-09-22 17:00:00  4.5   
# 4     20200923   9      38     2020-09-23 08:05:00  2020-09-23 14:50:42  6.762   
# Total Hours Worked: 19.633

# to show status for a longer period of time you can specify a key
# print a summary of the current days work hours.
python timeclock.py status day 

# print a summary of the current weeks work hours.
python timeclock.py status week # this is the default period, and can be left out

# print a summary of the current months work hours.
python timeclock.py status month

# Additionally, each of these commands can take an optional <key> parameter that will
# allow the user to specify a different period to display.
python timeclock.py status day 20200922
# (prints the following)
# ID    Date Key   Month  Week   Clock In             Clock Out            Hours 
# 2     20200922   9      38     2020-09-22 08:03:00  2020-09-22 10:00:00  1.95  
# 3     20200922   9      38     2020-09-22 12:30:00  2020-09-22 17:00:00  4.5   

# you can do the same with week and month and it will print the month or week you specify
python timeclock.py status week 38 # this will print all work days from week 9
python timeclock.py status month 9
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

# Joint functionality
The Following commands work for both the journal and the clock.

### Delete a time clock/journal entry
First find the ID number of the entry you want to delete using timeclock.py status
then use the following to delete it.
```shell script
# Delete a record from the time log
python timeclock.py clock delete {id}
python timeclock.py journal delete {id}
```

### Clear a days time clock/journal entries
First find the ID number of the entry you want to delete using timeclock.py status
then use the following to delete it.
```shell script
# Delete a record from the time log
python timeclock.py clock clear
python timeclock.py journal clear
```
