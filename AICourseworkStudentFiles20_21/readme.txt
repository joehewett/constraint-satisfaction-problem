There are a total of six files used for this coursework. They are as follows:

scheduler.py - this module contains 3 methods, createSchedule, createTestShowSchedule and createMinCostSchedule. 
The first one must return a valid timetable object, with each day and each slot assigned. 
The second must return a valid timetable for the second task, which consists of ten sessions a day, with main and test shows. 
The third method must return a legal schedule, that also has the lowest cost possible. 
The preamble of scheduler.py explains the other methods from other classes that you may use, and in addition you may only import the python math and random libraries. 
When you're ready to submit, this file must be renamed to yourUniID.py, e.g. 1003685.py. 


runScheduler.py - this is the file that is run to test your solution. This file will run your scheduler, test if it is legal and print out the cost. 
Feel free to edit line 16 to load in a different problem file, and edit the scheduler method called from createSchedule to createTestShowSession or createMinCostSchedule. 


There are four other files included in this coursework bundle. They have the following functions:

comedian.py - Contains the comedian class. Notably, a comedian is defined as a name and a list of themes. 
While this class has a few mutator methods (setName, setThemes, addTheme), the only legal ways for you to use these classes is as follows:
	c.name -- Returns the name of comedian c as a string.
	c.themes -- Returns the themes used by comedian c as a list of strings.


demographic.py - Contains the demographic class. Notably, a demographic is defined as a reference code and a list of topics. 
While this class has a few mutator methods (setReference, setTopics, addTopic), the only legal ways for you to use this class is as follows:
	d.reference -- Returns the reference code of demographic d as a string.
	d.topics -- Returns the topics that appeal to demographic d as a list of strings. 


timetable.py - Contains the timetable class. 
This class will be used to store the schedule you create, and a show slot can be assigned a demographic and a comedian through the 'addSession' method, as described in the preamble 
for schedule.py. Importantly, the only valid days of the week are Monday, Tuesday, Wednesday, Thursday and Friday and the only slot numbers that are valid are 1, 2, 3, 4, 5, 6 ,7 , 8, 9 
and 10. This class also contains the method to allow you to check you schedule is legal, and is used in runScheduler.py. However, this method cannot be used by your submitted solution in 
the scheduler.py file. When a timetable is created, the task number is also given, so that it can check against the correct rules. The following method can be used in your final submission:
	
	timetable.addSession(day, timeslot, comedian, demographic, show_Type) -- This will fill the designated timeslot(which should be a number) on the 
    given day (either Monday, Tuesday, Wednesday, Thursday, Friday) with the given comedian and demographic. show_Type should be a string with the value of either 'main' or 'test'. 
    For task 1 all sessions should be 'main' and for tasks 2 and 3 there will be both 'main' and 'test' sessions. 


ReaderWriter - class for reading in the example problems, and is also capable of writing out lists of actors and shows if you wish to create more problems to test your solution against. 
The use of the reader method can be see in runSchedule.py. To use the writer method it must be passed a list of comedian objects, a list of demographic objects and a filename. 
The readRequirements method converts the text file it is passed into a list of comedian and demographic objects. 

Each file is commented, and there is a limit to the methods and attributes you can use. 

Don't forget you should be using Python3, and can test your scheduler by running the 'runScheduler' file. 

