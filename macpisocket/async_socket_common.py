#!/usr/bin/env python


def extract_field_value(message, idx_field):
    field = message.split(',')[idx_field]   # gives a string LIKE 'wants:open' or 'wants:close'
    value = field.split(':')[1]  # gives value LIKE 'open' or 'close'
    return field, value


class AnalysisResults(object):
    
    def __init__(self, img_fname):
        self.img_fname = img_fname
        self.state = None
        self.median = None
        
    def compute(self):
        # FIXME make this compute real state from image and GET RID OF IMPORTS
        import time
        import random
        time.sleep(5)
        self.state = random.choice(['open', 'close'])
        self.median = 191
