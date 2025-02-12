input2events = {}
input2events['small'] = {}
input2events['medium'] = {}
input2events['large'] = {}

input2events['small']['ivf_key'] = 'Func3_xc_enc/small.ivf'
input2events['medium']['ivf_key'] = 'Func3_xc_enc/medium.ivf'
input2events['large']['ivf_key'] = 'Func3_xc_enc/large.ivf'

import json
with open('input.json', 'w') as f:
    json.dump(input2events, f) 