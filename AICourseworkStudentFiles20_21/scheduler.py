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

    def getShowCounts(self, comicScore, assignments):
        for a in assignments:
            c = a[1]
            t = a[2]
            score = 1 if t else 5

            if comicScore.get(c) == None:
                oldScore = 0
            else:
                oldScore = comicScore.get(c)
            
            newScore = score + oldScore
            comicScore.update({c: newScore})
        
    # Recursive algorithm for Task 2 
    def assignMainsAndTest(self, extendedDemoList, comediansNotBusy, assignments, demoNumber): 
        tt = timetable.Timetable(2)

        # If we've reached assignments, we've finished so return true
        if demoNumber >= 50: 
            return True
    
        # Get the demographic we're looking at in this recursion, and whether we're assigning a test for that demo, or a main 
        demo = extendedDemoList[demoNumber][0]
        isTest = extendedDemoList[demoNumber][1]
        
        scnb = sorted(comediansNotBusy, key=comediansNotBusy.get)
        for a in scnb:
            print(a)

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

                    if self.assignMainsAndTest(extendedDemoList, comediansNotBusy, assignments, demoNumber + 1) == True: 
                        return True
                        
                    # If this assignment failed, remove it and add hours and comedian back to list
                    removed = assignments.pop()
                    comedian = removed[1]
                    plusHours = 1 if removed[2] == True else 2
                    alreadyHours = 0 if comediansNotBusy.get(comedian) == None else comediansNotBusy.get(comedian)
                    comediansNotBusy.update({comedian: alreadyHours + plusHours})

        return False
        
    # Main function for Task 2 - initiates a backtracking recursion (assignMainsAndTest()) to solve the task 2 CSP (checked with violatesTest()) 
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
        if self.assignMainsAndTest(extendedDemoList, comediansNotBusy, assignments, 0) == False:
            print("No valid assignment of demographics (including tests) to comedians was found")
            return False

        # Sort the list alphabetically by comedian name  
        sortedList = sorted(assignments, key = lambda c: c[1].name)

        # Add all the demo/comedian pairs as sessions
        # Filling by session rather than day, in combination with our ordered list of pairs, means we'll never schedule a comedian for 2 sessions in one day
        for session in range(1,11):
            out = " | "
            for day in range(5):
                # s counts from 0 to 49
                s = (session - 1) * 5 + day
                isTest = sortedList[s][2]
                out += "T " if isTest else "M "
                out += sortedList[s][1].name[:2] + " | "
                test = "test" if isTest else "main"
                timetableObj.addSession(days[day], session, sortedList[s][1], sortedList[s][0], test)
            print(out)
        #Here is where you schedule your timetable

        return timetableObj
        
    #########################
    ######## TASK 3 #########
    #########################

    def getDay(self, slotNumber): 
        i = slotNumber
        if i < 10:
            i = 0
        else:
            while i >= 10:
                i = i / 10
        day = int(i) 
        return day

    def applySoftConstraints(self, unorderedAssignments, n, timeslots):
        assignmentScores = {}
        day = self.getDay(n)

        todaysStart = day * 10
        yesterdaysStart = (todaysStart - 10) if todaysStart > 0 else 0 

        for assignment in unorderedAssignments:
            assignmentScores.update({tuple(assignment): 0})
            mainYesterday = False
            mainToday = False 
            testsToday = 0
            d = assignment[0]
            c = assignment[1]
            test = assignment[2]

            for i in range(todaysStart, todaysStart + 10):
                if timeslots[i] is not None and timeslots[i][1] == c:
                    if timeslots[i][2] == True:
                        testsToday += 1 
                    elif timeslots[i][2] == False:
                        mainToday = True
            if yesterdaysStart > 0:
                for i in range(yesterdaysStart, yesterdaysStart + 10):
                    if timeslots[i] is not None and timeslots[i][1] == c:
                        if timeslots[i][2] == False:
                            mainYesterday = True 
                    
            if not test and not mainToday and mainYesterday:
                assignmentScores.update({assignment: 400})
            if test and testsToday == 1:
                assignmentScores.update({assignment: 300})
                
        sortedScores = sorted(assignmentScores.items(), key = lambda a:a[1], reverse=True)
        sortedAssignments = []
        for assignment in sortedScores:
            sortedAssignments.append(assignment[0])

        return sortedAssignments

    def futureFailureDetected(self, slotNumber, timeslots, assignments):
        day = self.getDay(slotNumber)

        # If we're on day 4 and still have > 2 hours of shows in assignments, we're going to have a bad time
        comicHours = {}
        if day == 4:
            for a in assignments:
                c = a[1]
                t = a[2]
                newHours = 1 if t else 2
                hoursAlready = comicHours.get(c) if comicHours.get(c) is not None else 0
                comicHours.update({c: hoursAlready + newHours})

            for i in range(40, 50):
                if timeslots[i] is None:
                    continue
                if timeslots[i][1] == c:
                    hoursAlready = comicHours.get(c) if comicHours.get(c) is not None else 0
                    comicHours.update({c: hoursAlready + 1 if timeslots[i][2] else 2})

        for comic, hours in comicHours.items():
            if hours > 2: 
                return True

        return False 

    def scheduleViolations(self, timeslots, slotNumber, assignments, assignment):
        day = self.getDay(slotNumber)
        todaysStart = day * 10

        # Try to detect if this configuration is destined to fail so we can backtrack early
        if self.futureFailureDetected(slotNumber, timeslots, assignments):
            return True

        comedian = assignment[1]
        hours = 1 if assignment[2] == True else 2
        todayHours = 0 
        for i in range(todaysStart, todaysStart + 10):
            if timeslots[i] == None:
                continue
            if timeslots[i][1] == comedian:
                if timeslots[i][2] == False:
                    todayHours += 2
                elif timeslots[i][2] == True:
                    todayHours += 1
        
        if todayHours + hours > 2:
            return True

        return False

    def assignShowsToDays(self, assignments, timeslots, slotNumber):
        # If we've reached 50 assignments, we've finished (base) so return true
        if slotNumber >= 50: 
            return True

        if timeslots[slotNumber] is not None:
            print("Error - trying to allocate to a timeslot that has already been filled")

        assignments = self.applySoftConstraints(assignments, slotNumber, timeslots)
        
        for assignment in assignments:
            if self.scheduleViolations(timeslots, slotNumber, assignments, assignment) == False:
                timeslots[slotNumber] = assignment
                assignments.remove(assignment)
                if self.assignShowsToDays(assignments, timeslots, slotNumber + 1) == True: 
                    return True
                assignments.append(timeslots[slotNumber])
                timeslots[slotNumber] = None

        return False


    def createMinCostSchedule(self):
        timetableObj = timetable.Timetable(3)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        assignments = []

        # Get a list of 50 shows, (1 test, 1 main for each demo) sorted by the number of comics that canMarket that show
        extendedDemoList = self.getSortedDemoList()

        # We're going to keep a list of comedians and their available time, so we can avoid trying to assign shows to fully-booked comedians
        comediansNotBusy = {}
        for comedian in self.comedian_List:
            comediansNotBusy.update({comedian: 4})

        # Begin backtrack to find a valid pairing between demographics and comedians
        if self.assignMainsAndTest(extendedDemoList, comediansNotBusy, assignments, 0) == False:
            print("No valid assignment of demographics (including tests) to comedians was found")
            return False

        sortedAssignments = sorted(assignments, key = lambda a: a[1].name)
        for a in sortedAssignments:
            print(a[1].name + " -      " + str(a[2]))
        timeslots = [None] * 50
        if self.assignShowsToDays(sortedAssignments, timeslots, 0) == False:
            print("No valid way of assigning those demographics to days (cap)")
            return False

        output = ["","","","","","","","","",""]
        for i in range(50):
            day = self.getDay(i)
            session = (i % 10)

            d = timeslots[i][0]
            c = timeslots[i][1]
            t = timeslots[i][2]
            output[session] += (" T " if t else " M ") + c.name[:2] + " |"
            timetableObj.addSession(days[day], session + 1, c, d, "test" if t else "main")

        for o in output:
            print(o)

        

        # # Add all the demo/comedian pairs as sessions
        # for day, sessions in dailySchedules.items():
        #     for session in range(10):
        #         demo = sessions[session][0]
        #         comedian = sessions[session][1]
        #         isTest = sessions[session][2]
        #         timetableObj.addSession(day, session + 1, comedian, demo, "test" if isTest else "main")

        # for o in output:
        #     print(o)

        return timetableObj

    # #This line generates a random timetable, that may not be valid. You can use this or delete it.
    # #self.randomMainSchedule(timetableObj)

    # Optimal Solution
    # 12 Comedians doing 2 main shows each, 1 per day on Mon-Tue, Tue-Wed, Wed-Thurs, Thurs-Fri - £7200
    # 6  Comedians doing 4 test shows each, 2 per day on any days - £2100 
    # 1  Comedian  doing 1 test show and 1 main show, on different days. - £750

    # Ma | Ma | Mb | Mb | Mt
    # Mc | Mc | Md | Md | Tm
    # Me | Me | Mf | Mf | Tm
    # Mg | Mg | Mh | Mh | Tn
    # Mi | Mi | Mj | Mj | Tn
    # Mk | Mk | Ml | Ml | To 
    # Tm | Tn | To | Tp | To
    # Tm | Tn | To | Tp | Tp
    # Tq | Tr | Ts | Ts | Tp
    # Tq | Tr | Ts | Ts | Ty

    # Dict of days containing lists
    # Dict of Comedian->List[Demo, isTest]
    # List of mainers: [Comedian, Demo]
    # List of testers [Comedian, Demo]
    # List of Others: [Comedian, Demo, isTest]
    # Fill MT, WT, with mainers
    # Then, if M > 2 free, fill M with testers, else T, else W etc
    # If 
    # If 0,1 or 1,0, assign anywhere
    # Strategy 
    # Don't randomly pick comics, or pick them in order of their availability.
    # Instead, pick them based on a score? 
    # Score can be calculated on the fly, in the recursive call
    # Take in a list of comics and their assignments 
    # If current demographic is Main, then order by comics that have 1 main 
    # If current dmeographic is Test, then order by comcis that have 3, 2, 1 tests
    # Once a comic is complete, delete 
    # 
    # Utility functions
    # Num comics with 2 mains
    # Num comics with 4 tests 
    # Num comics with other configurations 

    #Here is where you schedule your timetable

    #This line generates a random timetable, that may not be valid. You can use this or delete it.

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

    #It costs £500 to hire a comedian for a single main show.
    #If we hire a comedian for a second show, it only costs £300. (meaning 2 shows cost £800 compared to £1000)
    #If those two shows are run on consecutive days, the second show only costs £100. (meaning 2 shows cost £600 compared to £1000)

    #It costs £250 to hire a comedian for a test show, and then £50 less for each extra test show (£200, £150 and £100)
    #If a test shows occur on the same day as anything else a comedian is in, then its cost is halved. 

    #Using this method, return a timetable object that produces a schedule that is close, or equal, to the optimal solution.
    #You are not expected to always find the optimal solution, but you should be as close as possible. 
    #You should consider the lecture material, particular the discussions on heuristics, and how you might develop a heuristic to help you here. 

                # print("Adding assignment: " + str(assignment) + " to slot " + str(slotNumber))
                # print("Removing assignment from assignments. Assignments before:")
                # for a in assignments:
                #     print(a)
                # print("Assignments after removing assignment:")
                # for a in assignments:
                #     print(a)

                    
                # print("Adding back assignment: " + str(timeslots[slotNumber]) + " from slot " + str(slotNumber))
                # print("assignments now looks like:")
                # for a in assignments:
                #     print(a)