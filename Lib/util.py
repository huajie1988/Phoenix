__author__ = 'Huajie'

class Util(object):
    def __init__(self):
        pass

    def str2dict(self,str,separator):
        list=str.split(separator)
        if len(list)<2:
            return {}

        return {list[0]:list[1]}
