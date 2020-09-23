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

# Now run this command. It should output the file path of the virtual environment
pipenv --venv
# For example mine prints: "~/.local/share/virtualenvs/timeclok-VkAi0thm"

# Now Edit the clok.sh file. And change the following 2 variables.
# copy the output of pipenv --venv and past it where <path_to_your_python_bin> is below
PYTHON_BIN=<path_to_your_python_bin>
WORKING_DIR=<the location of your timeclok directory>

# Here are mine for an example. Yours will be a little different
PYTHON_BIN=~/.local/share/virtualenvs/timeclok-VkAi0thm
WORKING_DIR=~/Projects/timeclok

# Make sure that your run script can be executed by running the following.
chmod +x clok.sh

# Now change back to your home directory. Then run the following command to create a link
# to the executable script called clok in your home directory.
ln <the timeclok directory>/clok.sh clok
# here is the command I used as an example
ln ~/Projects/timeclok/clok.sh

# Now your all set, Run the following to make sure everything works
./clok --help

# if you dont want to type the ./ before clok everytime then add the following
# to the end of your .bashrc file. Then close your terminal and open a new one.
alias clok="./clok"
```
If I knew how to make the install easier I would. If anything just for the practice and
experience of it.

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
* Add windows support.

#### Note
If you followed the installation instructions, then instead of typing python clok.py you 
can just type clok

## Setup
In order to setup the app you first need to install it. Then you just do the following to
initialize the database.

```shell script
# Create the local sqlite database
python clok.py init
```
This program creates a sqlite database at ~/.timeclok/time-clock.db which it stores
everything in. Currently this project only supports linux/mac, but changing it to support 
windows would be pretty simple, just change the variables in core/defines to directories
that you have access to and it will work.

### Clocking In
```shell script
# clock in
python clok.py in

# clock in at a certain time
python clok.py in --when "2020-09-22 08:00:00"
```

### Clocking Out
```shell script
# clock out
python clok.py out
# Note: clock out can be called multiple times without calling a new clock in. This
# Will just overwrite the last clock out time with the current time.

# clock out a certain time
python clok.py out --when "2020-09-22 17:00:00"
```

### Adding Past Days
```shell script
# clock in at a certain time
python clok.py in --when "2020-09-20 08:00:00" --out "2020-09-20 08:00:00"
```

### Showing status
```shell script
# Display current days status
python clok.py status
# (prints the following)
# ID    Date Key   Month  Week   Clock In             Clock Out            Hours 
# 1     20200921   9      38     2020-09-21 08:20:00  2020-09-21 15:32:00  7.2   
# 2     20200922   9      38     2020-09-22 08:03:00  2020-09-22 10:00:00  1.95  
# 3     20200922   9      38     2020-09-22 12:30:00  2020-09-22 17:00:00  4.5   
# 4     20200923   9      38     2020-09-23 08:05:00  2020-09-23 14:50:42  6.762   
# Total Hours Worked: 19.633

# to show status for a longer period of time you can specify a key
# print a summary of the current days work hours.
python clok.py status day 

# print a summary of the current weeks work hours.
python clok.py status week # this is the default period, and can be left out

# print a summary of the current months work hours.
python clok.py status month

# Additionally, each of these commands can take an optional <key> parameter that will
# allow the user to specify a different period to display.
python clok.py status day 20200922
# (prints the following)
# ID    Date Key   Month  Week   Clock In             Clock Out            Hours 
# 2     20200922   9      38     2020-09-22 08:03:00  2020-09-22 10:00:00  1.95  
# 3     20200922   9      38     2020-09-22 12:30:00  2020-09-22 17:00:00  4.5   

# you can do the same with week and month and it will print the month or week you specify
python clok.py status week 38 # this will print all work days from week 9
python clok.py status month 9
```

# Journal
This program includes a basic journal that just stores a journal record that has the same
keys as the time clock entries. 

```shell script
# Write a journal entry
python clok.py journal m "a message that can contain \n (any special chars)"
```
```shell script
# Write a journal entry for a past time
python clok.py journal m  --when "2020-09-22 08:00:00" "message"
```

### Dump to json file
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

### Clear a days time clock/journal entries
First find the ID number of the entry you want to delete using clok.py status
then use the following to delete it.
```shell script
# Delete a record from the time log
python clok.py clear
python clok.py journal clear
```
