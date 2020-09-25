TimeClok
==========

This is a simple time clock app that I wrote to keep track of time for different jobs. It 
allows the user to "clock in" and "clock out" just like all the different time clocks you 
find in businesses all over the world. It has a pretty simple command line interface and
includes a few journaling commands as well.
I built this program because I needed the functionality that it has, and I also needed a 
break from the project I was working on.
The reason that it is named clok, is because cloc is taken, and clock could be as well.


## Installation
Download the repo to your system. Then Do the following. Installation currently requires
```shell script
cd timeclok # Change directories into the timeclok dir

# install the dependencies and create a virtual environment with pipenv
pipenv install

# Make sure that your run script can be executed by running the following.
chmod +x clok.sh

# Now create a link in your home directory to the command.
# here is the command I used as an example
ln ~/Projects/timeclok/clok.sh clok.sh

# Now your all set, Run the following to make sure everything works
./clok.sh --help

# Enable calling the program by typing clok instead of ./clok.sh
alias clok="./clok.sh"
```

This program creates a sqlite database at ~/.timeclok/time-clok.db which it stores
everything in. Currently this project only supports linux/mac, but changing it to support 
windows would be pretty simple, just change the variables in core/defines to directories
that you have access to and it will work.

#### Note
If you followed the installation instructions, then instead of typing *python clok.py* you 
can just type *clok* from now on instead of requiring you to be in the timeclok directory
and calling *python clok.py* explicitly from within a pipenv shell instance.

## Jobs
#### Managing Jobs
```shell script
# If you don't want to you don't even need to create a job. 
# the 'default' job is created the first time you run the program.
clok jobs --show
# ID     Job Name
# 1      default  <- Current
## thats great, it shows us that we have one job, and its the job were using now.

# add a new job, (it won't let you add a job that already exists)
# Note: also, all job names are stored lowercase only, less confusion that way.
clok jobs --add work
clok jobs --show
# ID     Job Name
# 1      default  <- Current
# 2      work  

# Well thats cool, but how do we switch to this new job?
# We need to call the job switch command and specify a job
clok jobs --switch work
clok jobs --show
# ID     Job Name
# 1      default
# 2      work  <- Current

# Thats it for jobs.
```
Notes. When you switch from one job to another, if you have a clok running in one job
it will automatically clok you out from that job. Then it will switch you to a new job.
Timeclok will also tell you what it is doing most of the time by printing messages to
the console. I left these messages out because I'm in a hurry.


#### Clocking In
```shell script
# clock in
python clok.py in

# clock in at a certain time
python clok.py in --when "2020-09-22 08:00:00"

# doing the same and recording a message about it
python clok.py in --m "a message that can contain \n (any special chars)"
python clok.py in --when "2020-09-22 08:00:00" --m "message"
```

#### Clocking Out
```shell script
# clock out
python clok.py out
# Note: clock out can be called multiple times without calling a new clock in. This
# Will just overwrite the last clock out time with the current time.

# clock out a certain time
python clok.py out --when "2020-09-22 17:00:00"
# doing the same and recording a message about it
python clok.py out --m "a message that can contain \n (any special chars)"
python clok.py out --when "2020-09-22 08:00:00" --m "message"
```

#### Adding Past Days
```shell script
# clock in at a certain time
python clok.py in --when "2020-09-20 08:00:00" --out "2020-09-20 08:00:00"

# adding a past day with a message entry
python clok.py in --when "2020-09-20 08:00:00" --out "2020-09-20 08:00:00" --m "message"
```

#### Showing status
```shell script
# Display current days status
python clok.py show
# (prints the following)
# ID     Job              Date Key   Month  Week   Clock In             Clock Out            Hours 
# 1      default         20200921   9      38     2020-09-21 08:20:00  2020-09-21 17:00:00  8.67  
# 2      default         20200922   9      38     2020-09-22 12:30:00  2020-09-22 18:00:00  5.5   
# 3      default         20200922   9      38     2020-09-22 08:00:00  2020-09-22 10:00:00  2.0   
# 4      default         20200923   9      38     2020-09-23 08:10:00  2020-09-23 19:00:00  10.83 
# 5      default         20200925   9      38     2020-09-25 09:35:00  (current 14:14:14)   4.65  
# Total Hours Worked: 31.654

# to show status for a longer period of time you can specify a key
# print a summary of the current days work hours.
python clok.py show day 

# print a summary of the current weeks work hours.
python clok.py show week # this is the default period, and can be left out

# print a summary of the current months work hours.
python clok.py show month

# Additionally, each of these commands can take an optional <key> parameter that will
# allow the user to specify a different period to display.
python clok.py show day --key 20200922
# (prints the following)
# ID     Job              Date Key   Month  Week   Clock In             Clock Out            Hours 
# 2      vitality         20200922   9      38     2020-09-22 12:30:00  2020-09-22 18:00:00  5.5   
# 3      vitality         20200922   9      38     2020-09-22 08:00:00  2020-09-22 10:00:00  2.0    

# you can do the same with week and month and it will print the month or week you specify
python clok.py show week --key 38 # this will print all work days from week 9
python clok.py show month --key 9
```

#### Dump to json file
The following command dumps the entire database to a json file. This includes the time clock
entries as well as the journal entries.
```shell script
# Dump the database to ~/.timeclok/time-clock{date-stamp}.json
python clok.py dump 

# Dump to specified file
python clok.py dump dump-file.json
```

# Joint functionality
The Following commands work for both the journal and the clock.

### Delete a time clock/journal entry
First find the ID number of the entry you want to delete using clok.py status
then use the following to delete it.
```shell script
# Delete a record from the time log
python clok.py delete {id}
python clok.py journal delete {id}
```

