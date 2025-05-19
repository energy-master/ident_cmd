



import sys, requests, re

# -- bot id --
bot_id = sys.argv[1]

# -- number of decisions --
number_decisions_reqd = sys.argv[2]
number_decisions = 0

# -- from --
decisions_path = 'https://marlin-network.hopto.org/mldata/decisions'


# -- download decisions ---
r_ = requests.get(decisions_path, allow_redirects=True, stream=True) 
html = r_.text   
pattern=r'href=[\'"]?([^\'" >]+)'
decision_files = re.findall(pattern, html)


for decision_file in decision_files[5:]:
    
    file_bot_id = '_'.join(decision_file.split('_')[0:2])
    
    if file_bot_id == bot_id:
        # download csv file
        decision_file_path = f'{decisions_path}/{decision_file}'
        
  
        r = requests.get(decision_file_path, allow_redirects=True, stream=True)
        print (r.text)
        
        # <- decision stats ->
