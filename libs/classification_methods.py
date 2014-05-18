from numpy import log2
from sys import maxint
from sys import float_info

class ClassificationMethod():
    def __init__(self):
        pass

    def classify(self, data, number_of_classes):
        pass

class NestedMeans(ClassificationMethod):
    def _classify(self, data, num):
        """recursive helper function of nested-means
        """
    
        if num<=0 or data.empty:
            return []
        mean = sum(data)/len(data)
        breaks = [mean]+self._classify(data[data<mean],num-1)+self._classify(data[data>=mean],num-1)
        return breaks
    
    
    def classify(self, data,number_of_classes=4):
        """Data is divided by nested-means.
    
        :param data: values to bin
        :param number_of_classes: divide values into this many bins, has to be a power of 2
        """
    
        if len(data)<number_of_classes:
            return [min(data),max(data)]
        breaks = [min(data),max(data)]+self._classify(data,log2(number_of_classes))
        return breaks


class Equidistant(ClassificationMethod):
    def classify(self, data, number_of_classes=6):
        """Data is divided by equally distant ranges.
    
        :param data: values to bin
        :param number_of_classes: divide values into this many bins
        """
    
        x = (max(data) - min(data))/number_of_classes
        breaks = [min(data),max(data)]+[i*x for i in range(1,number_of_classes)]
        return breaks


class Jenks(ClassificationMethod):
    def classify(self, data, number_of_classes=6):
        '''original code comes from 
        http://danieljlewis.org/2010/06/07/jenks-natural-breaks-algorithm-in-python/
        '''

        data.sort()

        #unreadable one liners
        #mat1 = [[0 for j in range(number_of_classes+1)] for i in range(len(data))] 
        #mat1.insert(1,[0]+([1 for i in range(number_of_classes)]))
        #mat2 = [[0 for j in range(number_of_classes+1)]]+[[0 for j in range(number_of_classes+1)]]+[[0]+[float('inf') for i in range(number_of_classes)] for j in range(len(data)-1)]

        
        mat1 = []
        mat2 = [] 
        for i in xrange(0,len(data)+1): 
            temp1 = []
            temp2 = [] 
            for j in xrange(0,number_of_classes+1): 
                temp1.append(0) 
                temp2.append(0)
            mat1.append(temp1) 
            mat2.append(temp2)

        for i in xrange(1,number_of_classes+1): 
            mat1[1][i] = 1 
            mat2[1][i] = 0 
            for j in xrange(2,len(data)+1): 
                mat2[j][i] = float('inf') 

        v = 0.0 
        for l in xrange(2,len(data)+1): 
            s1 = 0.0 
            s2 = 0.0 
            w = 0.0 
            for m in xrange(1,l+1): 
                i3 = l - m + 1 

                val = float(data[i3-1]) 

                s2 += val * val 
                s1 += val 

                w += 1 
                v = s2 - (s1 * s1) / w 
                i4 = i3 - 1 

                if i4 != 0: 
                    for j in xrange(2,number_of_classes+1): 
                        if mat2[l][j] >= (v + mat2[i4][j - 1]): 
                            mat1[l][j] = i3 
                            mat2[l][j] = v + mat2[i4][j - 1] 
            mat1[l][1] = 1 
            mat2[l][1] = v 

        k = len(data) 
        breaks = [0 for i in xrange(number_of_classes+1)]
        breaks[-1] = max(data)
        for i in reversed(xrange(2,number_of_classes+1)):
            id = int((mat1[k][i]) - 2)

            breaks[i - 1] = data[id] 
            k = int((mat1[k][i] - 1))
        return breaks