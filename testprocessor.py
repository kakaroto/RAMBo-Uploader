from termcolor import colored

class TestProcessor():
    def __init__(self):
        self.fullStep = []
        self.halfStep = []
        self.quarterStep = []
        self.sixteenthStep = []
        self.vrefs = []
        self.supplys = []
        self.supplyVoltages = []
        self.mosfetHigh = []
        self.mosfetLow = []
        self.thermistors = []
        self.errors = ""
        self.failedAxes = [False,False,False,False,False]
        self.failedMosfets = [False,False,False,False,False,False]
        self.axisNames = ["X","Y","Z","E0","E1"]
        self.thermistorNames = ["T0","T1","T2"]
        self.supplyNames = ["Extruder rail","Bed rail", "5V rail"]
        self.mosfetNames = ["Bed","Fan2","Fan1","Heat1","Fan0","Heat0"]  
        
    def testVrefs(self):
        passed = True
        if self._wasTimedOut(self.vrefs):
            print colored("...Timed out at vref test", 'red')
            return False
        for idx, val in enumerate(self.vrefs):
            if not 170 <= val <= 195:
                self.errors += colored(self.axisNames[idx] + " axis vref incorrect\n", 'red')
                passed &= False
        if max(self.vrefs) - min(self.vrefs) >= 15:
            self.errors +=  colored("Vref variance too high!\n",'red')
            passed &= False
        return passed

    def testSupplys(self):
        passed = True
        if self._wasTimedOut(self.supplys):
            print colored("...Timed out at supply test", 'red')
            return False
        for i in [0,1]:
            if 11.5 <= self.supplyVoltages[i] <= 12.5:
                pass
            else:
                self.errors += colored("Test " + self.supplyNames[i] + " supply\n", 'red')
                passed &= False
        if 4.7 <= self.supplyVoltages[2] <= 5.2:
            pass
        else:
            self.errors += colored("Test " + self.supplyNames[2] + " supply\n", 'red')
            passed &= False
        return passed

    def testThermistors(self):
        passed = True
        if self._wasTimedOut(self.thermistors):
            print colored("...Timed out at thermistor test", 'red')
            return False
        for idx, val in enumerate(self.thermistors):
            if not 975 <= val <= 985:
                self.errors += colored("Check Thermistor " + self.thermistorNames[idx] + "\n", 'red')
                passed = False
        return passed

    def testMosfetLow(self):
        passed = True
        if self._wasTimedOut(self.mosfetLow):
            print colored("...Timed out at MOSFET low test", 'red')
            return False
        for idx, val in enumerate(self.mosfetLow):
            if not val == 1 and not self.failedMosfets[idx]:
                self.errors += colored("Check " + self.mosfetNames[idx] + " MOSFET\n", 'red')
                self.failedMosfets[idx] = True
                passed = False
        return passed

    def testMosfetHigh(self):
        passed = True
        if self._wasTimedOut(self.mosfetHigh):
            print colored("...Timed out at MOSFET high test", 'red')
            return False
        for idx, val in enumerate(self.mosfetHigh):
            if not val == 0 and not self.failedMosfets[idx]:
                self.errors += colored("Check MOSFET " + self.mosfetNames[idx] + "\n", 'red')
                self.failedMosfets[idx] = True
                passed = False
        return passed

    def testStepperResults(self, vals):
        passed = True
        if self._wasTimedOut(vals):
            print colored("...Timed out at stepper test", 'red')
            return False
        for i in range(5): #Iterate over each stepper
            forward = vals[i] #Forward value are the first 5 in the list
            reverse = vals[i+5] #Reverse are the last 5
            print "Forward -> " + str(forward) + "Reverse -> " + str(reverse)
            for j in range(5): #Iterates over each entry in the test list
                #Here we fold the recording values onto each other and make sure
                #each residency time in a flag section is within +- 10 for
                #the forward and reverse segments
                validRange = range(reverse[4-j]-10,reverse[4-j]+10)
                if forward[j] not in validRange and not self.failedAxes[i]:
                    self.errors += colored("Check "+self.axisNames[i]+" stepper\n", 'red')
                    self.failedAxes[i] = True
                    passed = False
        return passed
        
    def verifyAllTests(self):
        passed = True
        
        if self.supplys: #Just realized this is spelled wrong
            print "Supply voltage values..."
            self.supplyVoltages = self._analogToVoltage(readings = self.supplys)
            print self.supplyVoltages
            passed &= self.testSupplys()

        if self.vrefs:
            print "Vref values..."
            print self.vrefs
            passed &= self.testVrefs()

        if self.thermistors:
            print "Target thermistor readings..."
            print self.thermistors
            passed &= self.testThermistors()

        if self.mosfetHigh:
            print "Mosfet high values..."
            print self.mosfetHigh
            passed &= self.testMosfetHigh()

        if self.mosfetLow:
            print "Mosfet low values..."
            print self.mosfetLow
            passed &= self.testMosfetLow()

        if self.fullStep:
            print "Full step results"
            passed &= self.testStepperResults(self.fullStep)

        if self.halfStep:
            print "Half step results"
            passed &= self.testStepperResults(self.halfStep)

        if self.quarterStep:
            print "Quarter step results"
            passed &= self.testStepperResults(self.quarterStep)

        if self.sixteenthStep:
            print "Sixteeth step results"
            passed &= self.testStepperResults(self.sixteenthStep)

        return passed
        
    def showErrors(self):
        print self.errors

    def restart(self):
        self.fullStep = []
        self.halfStep = []
        self.quarterStep = []
        self.sixteenthStep = []
        self.vrefs = []
        self.supplys = []
        self.supplyVoltages = []
        self.mosfetHigh = []
        self.mosfetLow = []
        self.thermistors = []
        self.errors = ""
        self.failedAxes = [False,False,False,False,False]
        self.failedMosfets = [False,False,False,False,False,False]

    def _wasTimedOut(self, vals):
        if -1 in vals:
            return True
        else:
            return False
            
    def _analogToVoltage(readings = [], voltage = 5, bits = 10, dividerFactor = 0.091):
        #divider factor is R2/(R1+R2)
        for val in readings:
            self.supplyVoltages += (float(val)/pow(2, bits)) * (voltage/dividerFactor)