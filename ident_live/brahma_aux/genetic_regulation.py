#!/usr/local/bin/python3

############################################################## 
#
#
# ===================================================
# | Genetic Algorithm Framework <=  MARLIN  =>    |
# ===================================================
#
#
#
#  c. Rahul Tandon, 2025, RSA 2025
#  Built with brahma, c. Vixen Intelligence 2025
#  
#  *** NO UNAUTHORISED USE ***
#
#  *** Genetic Regulation Functionality ***
#
#  
##############################################################

# imports
import random

 
def normalise(x):
    # normalise x to range [-1,1]
    nom = (x - x.min()) * 2.0
    denom = x.max() - x.min()
    return  nom/denom - 1.0

def sigmoid(x, k=0.1):
    # sigmoid function
    # use k to adjust the slope
    s = 1 / (1 + np.exp(-x / k)) 
    return s 
 

class GeneticRegulatoryNetwork(object):
    def __init__(self, bot = None):
        
        self.bot = bot
        self.regulatory_vector = {}
        self.regulatory_matrix = {}
        self.genes = []
    def mutate(self):
        pass

    def init(self):
        pass
    
    def run(self):
        return 1
    
    
class MARLINGeneticRegulatoryNetowrk(GeneticRegulatoryNetwork):
    
    def __init__(self, bot=None):
        GeneticRegulatoryNetwork.__init__(self, bot = bot)
        
    def build_regulatory_matrix(self):
        
        
        # all dna strands
        for dnaTag, dna in self.bot.dNA.items():
            # all genome strands in individual dna strand
            for genomeID, genome_str in dna.genome.items():
                for gene_tag, gene in genome_str.genome.items():
                    self.regulatory_matrix[gene_tag] = None
                    self.genes.append(gene_tag)
        
        # build the correlation matrix
        for gene_id_active in self.genes:
            tmp_matrix = {}
            express = random.uniform(-1,1)
            self.regulatory_vector[gene_id_active] = express
            for gene_id in self.genes:
                express = 0
                if gene_id == gene_id_active:
                    tmp_matrix[gene_id] = express
                    continue
                
                express = random.uniform(-1,1)
                tmp_matrix[gene_id] = express
        
            self.regulatory_matrix[gene_id_active] = tmp_matrix
            
            
        
    def regulate(self, bot = None):
        
        # print (dna)
        for dna_id, dna in bot.dNA.items():
            excitation = 0.0
            expression_level = bot.dNAExpression[dna_id]
            for genomeID, genome_str in dna.genome.items():
                for gene_tag, gene in genome_str.genome.items():
                    if gene_tag in self.regulatory_vector:
                        if gene_tag in genome_str.genomeExpression:
                            excitation += genome_str.genomeExpression[gene_tag] * self.regulatory_vector[gene_tag]
                            print (genome_str.genomeExpression[gene_tag])
        
        
        
        return random.uniform(0,1)
    
    def evolve(self):
        pass

