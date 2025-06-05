

# import root decision
from marlin_brahma.fitness.performance import *


version = "1.0"
print(f'Loading IDent decision structure.  [IdentDecision[v.{version}]]')
"""
Decision logic is required in order to evaluate bot performance.

"""

class IdentDecision(RootDecision):
    
    def __init__(self, decision_data = None):
        RootDecision.__init__(self,decision_type="IdentDecision", decision_status=decision_data['status'], type=decision_data['type'])
        self.Market = decision_data['env']
        self.time_bounds = [decision_data['iter_start_time'], decision_data['iter_end_time']]
        self.DecisionTypes = {1:'IDent', 0:'Idle'}
        self.Decision = self.DecisionTypes[decision_data['action']]
        self.xr = decision_data['xr']
        self.xr_start = decision_data['xr_start']
        self.max_memory = decision_data['memory']
        self.decision_id = decision_data['decision_id']
        self.iter_frame = decision_data['iter_frame']
        
        
    def __str__(self):
        return ("HP IDent 1.0, Market, {0} , Decision Type, {1} , Memory, {8}, XR_Start, {7}, Time From, {2}, Time To, {6}, Action, {3} , Result, {4}, ID, {5}, Iter_frame, {9}".format(self.Market, self.Decision, self.time_bounds[0], self.Decision, self.xr, self.decision_id, self.time_bounds[1], self.xr_start, self.max_memory, self.iter_frame ))
  
  
  
  
class IdentEvaluation(EvaluateDecisions):
    
    def __init__(self, bot, BotPerformance):
        EvaluateDecisions.__init__(self,bot=bot, botPerformance=BotPerformance)
        self.decision_summary = None
        self.fitnessValue = 0.0
        
        
    def evaluateFitness(self):
        # print ("custom eval")
        fitness_value = 0.0
        if self.botPerformance == None:
            # no decisions made
            self.fitnessValue = 0.0
            # print (f'{self.bot.name} made no decisions.')
            return None

        # print (f'{self.bot.name} made some decisions.')
        number_profiles = 0
        for epochTag, epoch in self.botPerformance.PerformanceHolder.items():
            for decision_profile in epoch.DecisionProfiles:
                if decision_profile.Status == "Closed":
                    number_profiles += 1
                    # print ("closed")
                    fitness_value += self.getDecisionProfileFitness(decision_profile)
                    # print (fitness_value)
        #print (f'final fitness : {fitness_value} | {number_profiles} | {self.bot.name}')
        self.fitnessValue = fitness_value
        return fitness_value


    def getDecisionProfileFitness(self, decisionProfile : DecisionProfile = None):
        
        xr_total = 0
        winners = 0
        losers = 0
        if decisionProfile is not None:
            for decision in decisionProfile.DecisionList:
                if (decision.Decision == "Idle"):
                    #print (decision.xr)
                    if decision.xr == True:
                        xr_total += 1
                        winners += 1
                    else:
                        xr_total -= 1
                        losers += 1
                    
        # ratio = float(winners/(winners+losers))
        # print (ratio, xr_total, winners, losers)
        # print (f'tally : {xr_total}')
        # return ratio
        return xr_total