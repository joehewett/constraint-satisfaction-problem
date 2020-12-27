import comedian
import demographic
import ReaderWriter
import timetable
import random
import math

class Scheduler:

    def __init__(self,comedian_List, demographic_List):
        self.comedian_List = comedian_List
        self.demographic_List = demographic_List

    #########################
    ######## TASK 1 #########
    #########################

    # At each stage of the recursion, check the constraints haven't been violated
    def violationsMain(self, assignments):
        ## Check that all comedians canMarket their show 
        tt = timetable.Timetable(1)
        showCounts = {}
        for demo, comedian in assignments.items():
            # Sanity check - should never get hit
            if not tt.canMarket(comedian, demo, False):
                return True
        
            if showCounts.get(comedian) == None:
                showCount = 0
            else:
                showCount = showCounts.get(comedian)

            # Increment showCount for this comedian 
            if showCount < 2: 
                showCounts.update({comedian: showCount + 1})
            else: 
                # If a comedian has done > 2 shows this week, return violation
                return True
        
        return False

    # Solves the task 1 CSP by backtracking
    # Recursively calls itself, backtracking when constraints are violated, until a valid solution of 25 demo/comedian assignments exists
    def assignMains(self, assignments, demoNumber): 
        
        tt = timetable.Timetable(1)

        # If we're reached 25 assignments, we've finished so return true
        if demoNumber >= 25: 
            return True
    
        demo = self.demographic_List[demoNumber]

        # For the new demographic, find the first comedian that can market it, and assign them to it
        for comedian in self.comedian_List:
            if tt.canMarket(comedian, demo, False): 
                # Assign the demo to the comedian 
                assignments.update({demo: comedian})
                # Check the 2 shows/wk constraint isn't violated
                if self.violationsMain(assignments) == False: 
                    # Recursively call assignMains with the newly added-to list of assignments, and the next demo to assign
                    if self.assignMains(assignments, demoNumber + 1) == True: 
                        return True
                    del assignments[demo]

        return False
    
    def createSchedule(self):
        timetableObj = timetable.Timetable(1)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        assignments = {}

        # Begin backtrack to find a valid pairing between demographics and comedians
        if self.assignMains(assignments, 0) == False:
            print("No valid assignment of demographics to comedians was found")
            return False

        # Sort the list alphabetically by comedian name  
        sortedList = sorted(assignments.items(), key = lambda c: c[1].name)

        # Add all the demo/comedian pairs as sessions
        # Filling by session rather than day, in combination with our ordered list of pairs, means we'll never schedule a comedian for 2 sessions in one day
        for session in range(1,6):
            for day in range(5):
                # s counts from 0 to 24
                s = (session - 1) * 5 + day
                timetableObj.addSession(days[day], session, sortedList[s][1], sortedList[s][0], "main")

        return timetableObj

    #########################
    ######## TASK 2 #########
    #########################

    # Recursive algorithm for Task 2 
    def assignTests(self, extendedDemoList, comediansNotBusy, assignments, demoNumber): 
        tt = timetable.Timetable(2)

        # If we've reached assignments, we've finished so return true
        if demoNumber >= 50: 
            return True
    
        # Get the demographic we're looking at in this recursion, and whether we're assigning a test for that demo, or a main 
        demo = extendedDemoList[demoNumber][0]
        isTest = extendedDemoList[demoNumber][1]
        
        # For the new demographic, find the first comedian that can market it, and assign them to it
        for comedian, hours in comediansNotBusy.items():
            if tt.canMarket(comedian, demo, isTest): 
                # Can't use a dict for this one because of duplicate demos (1 test, 1 main) so use list of 3 element tuples
                t = [demo, comedian, isTest]
                newHours = 1 if isTest else 2 

                if hours >= newHours: 
                    # remove hours from comediansNotBusy
                    comediansNotBusy.update({comedian: hours - newHours})
                    # remove comedian from available comics if hours left is 0 
                    if hours == newHours:
                        del comediansNotBusy[comedian]

                    assignments.append(t)

                    if self.assignTests(extendedDemoList, comediansNotBusy, assignments, demoNumber + 1) == True: 
                        return True
                        
                    # If this assignment failed, remove it and add hours and comedian back to list
                    removed = assignments.pop()
                    comedian = removed[1]
                    plusHours = 1 if removed[2] == True else 2
                    alreadyHours = 0 if comediansNotBusy.get(comedian) == None else comediansNotBusy.get(comedian)
                    comediansNotBusy.update({comedian: alreadyHours + plusHours})

        return False
        
    # Main function for Task 2 - initiates a backtracking recursion (assignTests()) to solve the task 2 CSP (checked with violatesTest()) 
    def getSortedDemoList(self): 
        tt = timetable.Timetable(2)
        demos = []
        sortedDemos = []

        # Iterate over demographics and work out how many comics can do the test/main show for the given topics
        for demographic in self.demographic_List:
            canDoMainCount = 0
            # Check how many comics are qualified to do the main show for this demo
            for comedian in self.comedian_List:
                if tt.canMarket(comedian, demographic, False):
                    canDoMainCount += 1
            demos.append([demographic, False, canDoMainCount])

            canDoTestCount = 0
            # Check how many comics are qualified to do the test show for this demo
            for comedian in self.comedian_List:
                if tt.canMarket(comedian, demographic, True):
                    canDoTestCount += 1
            demos.append([demographic, True, canDoTestCount])

        # Sort list by the number of comics that can do show
        sortedDemos = sorted(demos, key = lambda p: p[2])

        return sortedDemos

    # Task 2 driver - similar to task 1, but does some preprocessing and uses hueristics to cut down run time 
    def createTestShowSchedule(self):

        timetableObj = timetable.Timetable(2)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        assignments = []
        # Get a list of 50 shows, (1 test, 1 main for each demo) sorted by the number of comics that canMarket that show
        extendedDemoList = self.getSortedDemoList()

        # We're going to keep a list of comedians and their avaialable time, so we can avoid trying to assign shows to fully-booked comedians
        comediansNotBusy = {}
        for comedian in self.comedian_List:
            comediansNotBusy.update({comedian: 4})

        # Begin backtrack to find a valid pairing between demographics and comedians
        if self.assignTests(extendedDemoList, comediansNotBusy, assignments, 0) == False:
            print("No valid assignment of demographics (including tests) to comedians was found")
            return False

        # Sort the list alphabetically by comedian name  
        sortedList = sorted(assignments, key = lambda c: c[1].name)

        # Add all the demo/comedian pairs as sessions
        # Filling by session rather than day, in combination with our ordered list of pairs, means we'll never schedule a comedian for 2 sessions in one day
        for session in range(1,11):
            for day in range(5):
                # s counts from 0 to 49
                s = (session - 1) * 5 + day
                isTest = sortedList[s][2]
                test = "test" if isTest else "main"
                timetableObj.addSession(days[day], session, sortedList[s][1], sortedList[s][0], test)
        #Here is where you schedule your timetable

        return timetableObj

    #It costs £500 to hire a comedian for a single main show.
    #If we hire a comedian for a second show, it only costs £300. (meaning 2 shows cost £800 compared to £1000)
    #If those two shows are run on consecutive days, the second show only costs £100. (meaning 2 shows cost £600 compared to £1000)

    #It costs £250 to hire a comedian for a test show, and then £50 less for each extra test show (£200, £150 and £100)
    #If a test shows occur on the same day as anything else a comedian is in, then its cost is halved. 

    #Using this method, return a timetable object that produces a schedule that is close, or equal, to the optimal solution.
    #You are not expected to always find the optimal solution, but you should be as close as possible. 
    #You should consider the lecture material, particular the discussions on heuristics, and how you might develop a heuristic to help you here. 
    def createMinCostSchedule(self):
        #Do not change this line
        timetableObj = timetable.Timetable(3)

        #Here is where you schedule your timetable

        #This line generates a random timetable, that may not be valid. You can use this or delete it.
        self.randomMainAndTestSchedule(timetableObj)

        #Do not change this line
        return timetableObj


    #This simplistic approach merely assigns each demographic and comedian to a random, iterating through the timetable. 
    def randomMainSchedule(self,timetableObj):

        sessionNumber = 1
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        dayNumber = 0
        for demographic in self.demographic_List:
            comedian = self.comedian_List[random.randrange(0, len(self.comedian_List))]

            timetableObj.addSession(days[dayNumber], sessionNumber, comedian, demographic, "main")

            sessionNumber = sessionNumber + 1

            if sessionNumber == 6:
                sessionNumber = 1
                dayNumber = dayNumber + 1

    #This simplistic approach merely assigns each demographic to a random main and test show, with a random comedian, iterating through the timetable.
    def randomMainAndTestSchedule(self,timetableObj):

        sessionNumber = 1
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        dayNumber = 0
        for demographic in self.demographic_List:
            comedian = self.comedian_List[random.randrange(0, len(self.comedian_List))]

            timetableObj.addSession(days[dayNumber], sessionNumber, comedian, demographic, "main")

            sessionNumber = sessionNumber + 1

            if sessionNumber == 11:
                sessionNumber = 1
                dayNumber = dayNumber + 1

        for demographic in self.demographic_List:
            comedian = self.comedian_List[random.randrange(0, len(self.comedian_List))]

            timetableObj.addSession(days[dayNumber], sessionNumber, comedian, demographic, "test")

            sessionNumber = sessionNumber + 1

            if sessionNumber == 11:
                sessionNumber = 1
                dayNumber = dayNumber + 1

























        # demos = {}
        # for demographic in self.demographic_List:
        #     canDoCount = 0
        #     for comedian in self.comedian_List:
        #         if timetableObj.canMarket(comedian, demographic, False):
        #             canDoCount += 1
        #     demos.update({demographic.reference: canDoCount})

        #     print(str(demographic.topics) + " can be filled by " + str(demos.get(demographic.reference)) + " Comedians")         
                

        # for demo in sorted(demos, key=demos.get):
        #     print(demo + " " + str(demos.get(demo)))

        # for demographic in self.demographic_List:
        #     # only assign commedian if canMarket
        #     # canMarket(self, comedian, demographic, isTest)
        #     # and that comedian has done < 3 shows so far, and < 2 today
        #     for comedian in self.comedian_List:
        #         if timetableObj.canMarket(comedian, demographic, False):
        #             print("Comedian " + comedian.name + " is being assigned to demographic " + demographic.reference)
        #             print(comedian.themes)
        #             print(demographic.topics)
        #             print("")

        #             timetableObj.addSession(days[dayNumber], sessionNumber, comedian, demographic, "main")
        #             break

        #     sessionNumber = sessionNumber + 1

        #     if sessionNumber == 6:
        #         sessionNumber = 1
        #         dayNumber = dayNumber + 1

        # #This line generates a random timetable, that may not be valid. You can use this or delete it.
        # #self.randomMainSchedule(timetableObj)

    #Using the comedian_List and demographic_List, create a timetable of 5 slots for each of the 5 work days of the week.
    #The slots are labelled 1-5, and so when creating the timetable, they can be assigned as such:
    #   timetableObj.addSession("Monday", 1, comedian_Obj, demographic_Obj, "main")
    #This line will set the session slot '1' on Monday to a main show with comedian_obj, which is being marketed to demographic_obj. 
    #Note here that the comedian and demographic are represented by objects, not strings. 
    #The day (1st argument) can be assigned the following values: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
    #The slot (2nd argument) can be assigned the following values: 1, 2, 3, 4, 5 in task 1 and 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 in tasks 2 and 3. 
    #Comedian (3rd argument) and Demographic (4th argument) can be assigned any value, but if the comedian or demographic are not in the original lists, 
    #   your solution will be marked incorrectly. 
    #The final, 5th argument, is the show type. For task 1, all shows should be "main". For task 2 and 3, you should assign either "main" or "test" as the show type.
    #In tasks 2 and 3, all shows will either be a 'main' show or a 'test' show
    
    #demographic_List is a list of Demographic objects. A Demographic object, 'd' has the following attributes:
    # d.reference  - the reference code of the demographic
    # d.topics - a list of strings, describing the topics that the demographic like to see in their comedy shows e.g. ["Politics", "Family"]

    #comedian_List is a list of Comedian objects. A Comedian object, 'c', has the following attributes:
    # c.name - the name of the Comedian
    # c.themes - a list of strings, describing the themes that the comedian uses in their comedy shows e.g. ["Politics", "Family"]

    #For Task 1:
    #Keep in mind that a comedian can only have their show marketed to a demographic 
        #if the comedian's themes contain every topic the demographic likes to see in their comedy shows.
    #Furthermore, a comedian can only perform one main show a day, and a maximum of two main shows over the course of the week.
    #There will always be 25 demographics, one for each slot in the week, but the number of comedians will vary.
    #In some problems, demographics will have 2 topics and in others, 3.
    #A comedian will have between 3-8 different themes. 

    #For Task 2 and 3:
    #A comedian can only have their test show marketed to a demographic if the comedian's themes contain at least one topic
        #that the demographic likes to see in their comedy shows.
    #Comedians can only manage a 4 hours of stage time, where main shows 2 hours and test shows are 1 hour.
    #A Comedian can not be on stage for more than 2 hours a day.

    #You should not use any other methods and/or properties from the classes, these five calls are the only methods you should need. 
    #Furthermore, you should not import anything else beyond what has been imported above. 
    #To reiterate, the five calls are timetableObj.addSession, d.name, d.genres, c.name, c.talents

    #This method should return a timetable object with a schedule that is legal according to all constraints of task 1.