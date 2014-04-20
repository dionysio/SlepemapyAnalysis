from numpy import log2
from sys import maxint


class ClassificationMethod():
    def __init__(self):
        pass

    def classify(self, data, number_of_classes):
        pass

class NestedMeans(ClassificationMethod):
    def _classify(self, data,num):
        """recursive helper function of nested-means
        """
    
        if num<=0 or data.empty:
            return []
        breaks = [data.mean()]+self._classify(data[data<mean],num-1)+self._classify(data[data>=mean],num-1)
        breaks = list(set(breaks)) #drop duplicate bins
        breaks.sort()
        return breaks
    
    
    def classify(self, data,number_of_classes=4):
        """Data is divided by nested-means.
    
        :param data: values to bin
        :param number_of_classes: divide values into this many bins, has to be a power of 2
        """
    
        if len(data)<number_of_classes:
            return [data.min()-1,data.max()+1]
        breaks = [data.min()-1,data.max()+1]+self._classify(data,log2(number_of_classes))
        breaks = list(set(breaks)) #drop duplicate bins
        breaks.sort()
        return breaks


class Equidistant(ClassificationMethod):
    def classify(self, data,number_of_classes=6):
        """Data is divided by equally distant ranges.
    
        :param data: values to bin
        :param number_of_classes: divide values into this many bins
        """
    
        x = (data.max() - data.min())/number_of_classes
        breaks = [data.min()-1,data.max()+1]+[i*x for i in range(1,number_of_classes)]
        breaks = list(set(breaks)) #drop duplicate bins
        breaks.sort()
        return breaks


class Jenks(ClassificationMethod):
    def classify(self, data, number_of_classes=6):
        """Port of original javascript implementation by Tom MacWright from https://gist.github.com/tmcw/4977508
    
        Data is divided by jenks algorithm.
    
        :param data: values to bin
        :param number_of_classes: divide values into this many bins
        """
    
        input = data.copy()
        input.sort()
        input = input.tolist()
        length = len(data)
    
        #define initial values of the LC and OP
        lower_class_limits = [[1 for x in range(0,number_of_classes+1)] if y==0 else [0 for x in range(0,number_of_classes+1)] for y in range(0,length+1)] #LC
        variance_combinations = [[0 for x in range(0,number_of_classes+1)] if y==0 else [maxint for x in range(0,number_of_classes+1)] for y in range(0,length+1)] #OP
        variance = 0
    
        #calculate optimal LC
        for i in range(1,length):
            sum = 0 #SZ
            sum_squares = 0 #ZSQ
            counter = 0 #WT
    
            for j in range(0,i+1):
                i3 = i - j + 1 #III
                value = input[i3-1]
                counter+=1 #WT
    
                sum += value
                sum_squares += value * value
                variance = sum_squares - (sum * sum) / counter
                i4 = i3 - 1 #IV
    
                if (i4 != 0) :
                    for k in range(0,number_of_classes+1):
                        #deciding whether an addition of this element will increase the class variance beyond the limit
                        #if it does, break the class
                        if (variance_combinations[i][k] >= (variance + variance_combinations[i4][k - 1])) :
                            lower_class_limits[i][k] = i3
                            variance_combinations[i][k] = variance + variance_combinations[i4][k - 1]
            lower_class_limits[i][1] = 1
            variance_combinations[i][1] = variance #we can use variance_combinations in calculations of goodness-of-fit, but we do not need it right now
    
        #create breaks
        length -= 1
        breaks = []
        breaks.append(input[0]-1) #append lower bound that was not found during calculations
        breaks.append(input[length]+1) #append upper bound that was not found during calculations
        while (number_of_classes > 1):
            breaks.append(input[lower_class_limits[length][number_of_classes] - 2])
            length = lower_class_limits[length][number_of_classes] -1
            number_of_classes-=1
    
        breaks = list(set(breaks)) #drop duplicate bins
        breaks.sort()
        return breaks