def find_dict(dict, func):
    for k, v in dict.items():
        if func(k,v):
            return k, v

    return None, None

#subtracts collection2 from collection1
def subtract(collection1, collection2):
    for x in collection2:
        collection1.remove(x)
