
#!/usr/local/bin/python3
import json
import random
import requests
import pickle
import psutil
import os
from rich.progress import Progress
import marlin_brahma.fitness.performance as performance
import marlin_brahma.world.population as pop
import logging
# --------------------------------------------------------------
# --- Setup Class ---                                          |
# --------------------------------------------------------------


class AlgorithmSetup(object):
    """Class to control optimisation algorithm.

    Args:
        object (): root class object
    """

    def __init__(self, config_file_path: str = "config.json"):

        self.args = {}

        # load config file
        run_config = None
        with open(config_file_path, 'r') as config_f:
            run_config = json.load(config_f)

        if run_config is not None:
            self.args = run_config


# --------------------------------------------------------------
# --- IDent Application Class ---                               |
# --------------------------------------------------------------


class SpeciesIdent(object):
    """_summary_

    Args:
        object (_type_): _description_
    """

    def __init__(self, setup: AlgorithmSetup = None):
        self.algo_setup = setup
        id = random.randint(0, 99999)
        self.batch_id = f'brahma_{id}'
        self.population = None
        self.data_feed = None
        self.derived_data = None
        # performance and evaluation
        self.performance = None
        self.algo_setup.args['run_id'] = self.batch_id
        self.loaded_bots = {}
        self.mode = 0
        self.bulk = 0
        self.ss_ids = []
        self.multiple_derived_data = None
        self.multiple_data = -1
        self.feature_targets = {}
        self.loaded_targets = []
        self.selected_bots = []
        
        self.selected_loaded_bots = {}

    def generation_reset(self):
        self.performance = performance.Performance()

    def load_bot(self, bot_path):
        # print ("loading...")
        # print (bot_path)
        file_ptr = open(bot_path, 'rb')
        bot = pickle.load(file_ptr)
        # print(bot)
        return bot

    def update_bots(self, bot_dir="",feature_list = []):
        self.loaded_bots = {}
        number_loaded = 0
        
        with Progress() as progress:
            process = psutil.Process(os.getpid())
            task1 = progress.add_task(
                f"[green] Updating initial distribution of features/bots.", total=int(len(feature_list)))

            for bot_id in feature_list:
                bot_path = f'{bot_dir}/{bot_id}.vixen'
                # print(bot_path)
                error = False
                # print (f'loading {version}')

                try:
                    bot = self.load_bot(bot_path)
                    self.loaded_bots[bot_id] = bot
                    number_loaded += 1
                    # print(number_loaded)
                    progress.update(task1, advance=1)
                except Exception as e:
                    error = True
                    print(f'error loading {bot_id} {type(e).__name__}')
                    
                
        

    def load_bots(self, filter_data, version="1_0_0", version_time_from="", version_time_to="", bot_dir="", number_features=1000, update=False, direct=False):
        # print (filter_data)
       
        print ("======")
        self.selected_bots = []
        
        feature_data = None
        features_name_list = []
        number_read = 0
        number_loaded = 0
        versions_list = version.split('/')
        data = None
        print (f'Updating bots  : {update}')
        
        if update:
            print('Updating features/bots list.')
            url = 'https://vixen.hopto.org/rs/api/v1/data/features'
            post_data = {'market': filter_data, 'version_time_from': version_time_from,
                         'version_time_to': version_time_to}
            
            x = requests.post(url, json=post_data)
            data = x.json()
            
        else:
            if not direct:
                # print('loading features/bots list...')
                with open('feature_list.json', 'r') as f:
                    feature_data = json.load(f)
                # print('loaded.')
                bot_ids = feature_data['ids']
                data = {}
                data['data'] = []
                for bid in bot_ids:
                    d = {'botID': bid}
                    data['data'].append(d)

            else:
                # get bot ids from files in folder
                l=os.listdir(bot_dir)
                li=[x.split('.')[0] for x in l]
                data = {}
                data['data'] = li
        
        with Progress() as progress:
            process = psutil.Process(os.getpid())
            task1 = progress.add_task(
                f"[green] Loading features/bots.", total=int(number_features))

            for key in data["data"]:
                number_read += 1
                bot_id = ""
                if not direct:
                    bot_id = key['botID']
                else:
                    bot_id = key

                

                bot_path = f'{bot_dir}/{bot_id}.vixen'
                error = False
                
                try:
                    bot = self.load_bot(bot_path)
                    
                    add = True

                    
                    if hasattr(bot, 'version'):
                        
                        # print (bot.version)
                        # print (bot)
                        if (bot.version) not in versions_list:
                            # print (f' hit : v: {bot.version} | {versions_list}')
                            # print ("wrong v")
                            add = False
                            continue
                        else:
                            
                            # print (f' hit : v: {bot.version} | {versions_list}')
                            pass

                    else:
                        if "1_0_0" != version:
                            add = False
                            # print ("wrong v1")
                            continue

                    if add:
                        
                        
                        self.selected_bots.append(bot_id)
                        features_name_list.append(bot_id)
                        self.loaded_bots[bot_id] = bot
                        number_loaded += 1
                        # print(number_loaded)
                        progress.update(task1, advance=1)
                        
                        self.feature_targets[bot_id] = bot.env
                        if bot.env not in self.loaded_targets:
                            self.loaded_targets.append(bot.env)
                            
                        # if number_loaded > float(number_features):
                        #     print('Number required loaded.')
                        #     break
                            
                except Exception as e:
                    error = True
                    print ("ERROR")
                    print(f'error loading {bot_id} {type(e).__name__}')

                if error == False:
                    pass
                    # print (f'success loading {bot_id}')

            if update == True:
                feature_data = {
                    "ids": features_name_list
                }
                # print ("Writing feature list.")
                with open('feature_list.json', 'w+') as f:
                    json.dump(feature_data, f)

            # print(feature_data)
        if len(self.selected_bots) > int(number_features):
            
            self.selected_bots = random.choices(self.selected_bots,k=int(number_features))
        else:
            return 0
        
        
        for k, v in self.loaded_bots.items():
            # if k not in self.selected_bots:
            #     self.loaded_bots.pop(k)
            if k in self.selected_bots:
                self.selected_loaded_bots[k] = v

        # self.loaded_bots = {}
        # self.loaded_bots = self.selected_loaded_bots

        self.mode = 1
        self.bulk = 1
        
        # print(f'number loaded : {number_loaded}')
        # print(f'number read : {number_read}')
        l = len(self.loaded_bots)
        
        # print (self.loaded_bots)
        # print (f'refined bots loaded : {l}')
        # print (self.loaded_bots)
        
        
        # exit()
        return l

    def run(self):
        pass

    def build_world(self):
        """Build the population of bots using brahma_marlin. Genes are present in ../genes
        """

        try:
            logging.critical('Building population')
            self.population = pop.Population(
                parms=self.algo_setup.args, name="hp_classifier")
            logging.critical('Building... ')
            self.population.Populate(species="AcousticBot", args=None)
            logging.debug("Population built")
        except Exception as err:
            logging.critical(f"Error building population {err=} {type(err)=}")

    def evolve_world(self):
        pass

    def output_world(self):
        pass


# --------------------------------------------------------------
# --- IDent Feature Update   ---                               |
# --------------------------------------------------------------
