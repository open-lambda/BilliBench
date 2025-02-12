input2events = {}
input2events['small'] = {}
input2events['medium'] = {}
input2events['large'] = {}

input2events['small']['content_key']    = "Func8_UploadReview/star_war_small"
input2events['medium']['content_key']   = "Func8_UploadReview/star_war_medium"
input2events['large']['content_key']    = "Func8_UploadReview/star_war_large"


import json
with open('input.json', 'w') as f:
    json.dump(input2events, f) 