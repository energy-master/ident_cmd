



import sys
from dotenv import load_dotenv, dotenv_values
import pickle
import json

load_dotenv()
config = dotenv_values("config.env")

data_path = config['FEATURE_DIR']
model = sys.argv[1]
bot_id = sys.argv[2]
# load bot

bot_fp = f'{data_path}/{model}/{bot_id}.vixen'

# print (bot_fp)
with open(bot_fp,'rb') as bfp:
    bot = pickle.load(bfp)

bot_structure = (bot.printStr())

bot_structure_json = json.loads(bot_structure)
bot_formatted_str = json.dumps(bot_structure_json,indent=10)

print (bot_formatted_str)