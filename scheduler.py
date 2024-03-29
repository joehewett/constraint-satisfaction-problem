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

    ######################### A simple CSP solver that uses backtracking find a valid configuation of Comics/Shows
    ######## TASK 1 ######### Comic/Show pairs are then assigned to a schedule using a structural trick, negating the need for a CSP
    #########################

    # At each stage of the recursion, check the constraints haven't been violated
    def violationsMain(self, assignments):
        # Check that all comedians canMarket their show 
        tt = timetable.Timetable(1)
        showCounts = {}
        for demo, comedian in assignments.items():
            # Sanity check - should never get hit
            if not tt.canMarket(comedian, demo, False):
                return True
        
            # Get the count of shows this comic has done this week
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
        else:
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

    ######################### Uses a more sophisticated search involves the use of a heuristic function that orders the list of possible assigments
    ######## TASK 2 ######### The heurstic orders the next assignment based on which one will get us towards 12 comedians with 2M, 6 with 4T and 1 with 1M 2T as this is the optimal combination
    ######################### In this task, we don't bother using a CSP to assign Comic->Demo pairs to timeslots. We just order by comic name and assign slot by slot, meaning no comic can ever have >1 show per day, making that constriant void
                                # this approach means we don't get an optimal score, but means we can run the timeslot assignment in O(n) rather than using a CSP to do it. 

    # Function to work out how many main shows and test shows a comedian is currently assigned, given a list of assignments
    def getShowCounts(self, assignments):
        comicScore = {}
        # Iterate over all assignments so far, and update the score for the comedian 
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
        # Return a dict of comic:score
        return comicScore
        
    # Given our current list of assignments of comic->demographic, take the next demographic and rank the comedians
    # based on how well they fit the potential demographic. We return this ordered list of comedians 
    # and try to assign them in that order 
    def applyAssignmentHeuristics(self, comedians, demo, isTest, assignments):
        # return a dict of {comedian, hours}, ordered by points
        tt = timetable.Timetable(2)

        # Get some scores based on who we think would be a good fit for this demographic, based on previous assignments
        # Score for each comedian = how many shows of each type they have done before, e.g. a comedian that has already done 3 Tests will get a score of 3 
        comicScores = {}
        for comic in comedians:
            testCount = 0 
            mainCount = 0 
            if not tt.canMarket(comic, demo, isTest):
                comicScores.update({comic: 0})        
                continue
            # For every assignment that this comic has, count the tests and mains. This will be their score
            for a in assignments:
                if not (a[1] == comic):
                    continue
                if a[2] == True:
                    testCount += 1
                elif a[2] == False:
                    mainCount += 1

            # Add 1 just to indicate that this person CAN do the demo, even if they score 0 on the other suitability criteraik
            score = 1 + (testCount if isTest else mainCount)
            comicScores.update({comic: score})        

        # Convert the points dictionary into a format that we can return and use
        orderedComediansList = sorted(comicScores.items(), reverse=True, key = lambda x: x[1])
        orderedComediansDict = {}
        for o in orderedComediansList:
            comedian = o[0]
            orderedComediansDict.update({comedian: comedians.get(comedian)})

        return orderedComediansDict

    # Recursive algorithm for Task 2 and the first part of task 3
    # Assigns 50 demographics (25 tests and 25 mains) to a set of comedians. 
    # Each time the function recurses, it orders the potential 
    def assignMainsAndTest(self, extendedDemoList, comediansNotBusy, assignments, demoNumber): 
        tt = timetable.Timetable(2)

        # If we've reached assignments, we've finished so return true
        if demoNumber >= 50: 
            return True
    
        # Get the demographic we're looking at in this recursion, and whether we're assigning a test for that demo, or a main 
        demo = extendedDemoList[demoNumber][0]
        isTest = extendedDemoList[demoNumber][1]
        
        comediansNotBusy = self.applyAssignmentHeuristics(comediansNotBusy, demo, isTest, assignments)
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
        
    # Organies the demographics in descending order of how many comedians can fulfil the show. We can to 
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

        # We're going to keep a list of comedians and their available time, so we can avoid trying to assign shows to fully-booked comedians
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

        return timetableObj
        
    ######################### Task 3 utilises a lot of the logic from task 2, with the addition of a CSP to assign the task 2 comic->demo pairs to timeslots in the schedule
    ######## TASK 3 ######### This second CSP uses a new heuristic, that uses a points based system for different features to decide which comic->demo pair to assign to a given timeslot
    ######################### The benefit of scoring possible assignments with points based on what features they have is that we can change the waiting of different potential assignments in order to fine-tune the CSP for time/cost
                                # the fine tuning can be done manually, by changing the weights of different features, or we can work out the optimal weightings via bruteforcing each combination 
                                # of weightings and taking the average score over the 8 example sheets. This is a task for a future version, as we found a satsifactory combination of weights by hand in this version, for this problem. 

    # Gets the day of the week from the index in a 50 element array
    def getDay(self, slotNumber): 
        i = slotNumber
        if i < 10:
            i = 0
        else:
            while i >= 10:
                i = i / 10
        day = int(i) 
        return day

    # Give every possible next assignment a score, based on whether it is a test/main and the surrounding tests/mains
    # Then return the list of assignments in descending order of score, so that we try the highest score option next
    def applySchedulingHeuristics(self, unorderedAssignments, n, timeslots):
        assignmentScores = {}
        day = self.getDay(n)
        todaysStart = day * 10
        yesterdaysStart = (todaysStart - 10) if todaysStart > 0 else -1 

        # Iterate over each of the possible next assignments
        for assignment in unorderedAssignments:
            assignmentScores.update({tuple(assignment): 0})
            mainYesterday = False
            mainToday = False 
            testsToday = 0
            c = assignment[1]
            test = assignment[2]

            # Check the assignments currently in "today". If they are by the same comic, we can work out whether or not we benefit from this assignment
            for i in range(todaysStart, todaysStart + 10):
                if timeslots[i] is not None and timeslots[i][1] == c:
                    if timeslots[i][2] == True:
                        testsToday += 1 
                    elif timeslots[i][2] == False:
                        mainToday = True
            # If yeseterday exists, then check all the shows yesterday and see if they're by the same comic 
            # We dont care about tests yesterday because we derive no benefit, but we do care about adjacent mains
            if yesterdaysStart >= 0:
                for i in range(yesterdaysStart, yesterdaysStart + 10):
                    if timeslots[i] is not None and timeslots[i][1] == c:
                        if timeslots[i][2] == False:
                            mainYesterday = True 
                    
            # If this is a main, and there was a main yesterday, then we should place a high value on putting this assignment in the given timeslot
            if not test and not mainToday and mainYesterday:
                assignmentScores.update({assignment: 400})
            if test and testsToday == 1:
                assignmentScores.update({assignment: 300})
                
        # Now sort scores by number of comic scores
        comicScores = self.getShowCounts(unorderedAssignments)
        for assignment in assignmentScores:
            comic = assignment[1]
            isTest = assignment[2]
            #print(comic)
            showScore = comicScores.get(comic)
            if not isTest and (showScore >= 5 and showScore <= 7): 
                showScore = 0
            #print(showScore)
            assignmentScore = assignmentScores.get(assignment)
            assignmentScores.update({assignment: showScore + assignmentScore})

        sortedScores = sorted(assignmentScores.items(), key = lambda a: a[1], reverse=True)

        sortedAssignments = []
        for assignment in sortedScores:
            sortedAssignments.append(assignment[0])

        return sortedAssignments

    # Before we embark upon the route, try to identify whether we are destined to fail. 
    # If we can spot a future failure ahead, we can cancel this search and go back without wasting time 
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

        # If it's friday and someone has > 2 hours to do, it's not going to work. Back out 
        for comic, hours in comicHours.items():
            if hours > 2: 
                return True

        return False 

    # Check for any schedule violations. 
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

    # Our second CSP, that takes a list of comic->show assignments, and tries to give them time slots to produce an optimal cost.
    def assignShowsToDays(self, assignments, timeslots, slotNumber):
        # If we've reached 50 assignments, we've finished (base) so return true
        if slotNumber >= 50: 
            return True

        if timeslots[slotNumber] is not None:
            print("Error - trying to allocate to a timeslot that has already been filled")

        # Before we pick an assignment, order them in order of best to worst
        # Best and worst are judged with a points based system in applySchedulingHeuristic()
        assignments = self.applySchedulingHeuristics(assignments, slotNumber, timeslots)
        
        # Pick the next assignment, check if it violates, if not recurse until we reach failure.
        for assignment in assignments:
            if self.scheduleViolations(timeslots, slotNumber, assignments, assignment) == False:
                timeslots[slotNumber] = assignment
                assignments.remove(assignment)
                if self.assignShowsToDays(assignments, timeslots, slotNumber + 1) == True: 
                    return True
                assignments.append(timeslots[slotNumber])
                timeslots[slotNumber] = None

        return False

    # Driver function for Task 3
    # We have split this task into 2 CSP's.
    # 1) We assign Comics->Demographics using the same CSP as Task 2
    # 2) We then assign those pairs to timeslots using a new CSP specifically for producing the lowest cost schedule
    def createMinCostSchedule(self):
        tt = timetable.Timetable(3)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        assignments = []
        timeslots = [None] * 50
        output = [""] * 10

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
        if self.assignShowsToDays(sortedAssignments, timeslots, 0) == False:
            print("No valid way of assigning those demographics to days (cap)")
            return False

        # Convert the list of timeslots & comic/show pairs into a timetable 
        for i in range(50):
            day = self.getDay(i)
            session = (i % 10)
            d = timeslots[i][0]
            c = timeslots[i][1]
            t = timeslots[i][2]
            output[session] += (" T " if t else " M ") + c.name[:2] + " |"
            tt.addSession(days[day], session + 1, c, d, "test" if t else "main")

        for o in output:
            print(o)

        return tt
