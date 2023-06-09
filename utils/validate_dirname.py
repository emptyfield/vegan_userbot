import re

def is_valid_dirname(dirname):
    # Check for invalid characters
    if not re.match(r'^[\w\-\s]+$', dirname):
        return False
    
    # Check for reserved names
    reserved_names = ['.', '..', 'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
    if dirname.lower() in reserved_names:
        return False
    
    return True
