



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
        # total_length = r.headers.get('content-length')
        
        # save_filepath = "tmp_.dat"
    
        # f = open(save_filepath, 'wb')
        # dl = 0
        # total_length = int(total_length)
        # for data in r.iter_content(chunk_size=2000):
        #     dl += len(data)
        #     f.write(data)
        #     done = int(50* dl / total_length)
        #     sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
        #     sys.stdout.flush()

        # sys.stdout.flush()
        
        
        
        
        # pretty print csv file
    


