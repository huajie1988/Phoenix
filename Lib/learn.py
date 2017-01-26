__author__ = 'Huajie'
import math,sys

class Learn(object):
    a=2
    b=2
    c=2
    d=2
    e=2
    sigma=.2
    def __init__(self):
        pass

    def calc(self,sample,val):

        span=0.001
        avg_span=span/4
        a=self.a
        b=self.b
        c=self.c
        d=self.d
        e=self.e
        variance_start=(a)*sample[0]+(b)*sample[1]+(c)*sample[2]+(d)*sample[3]+(e)
        min=(val-variance_start)*(val-variance_start)
        min_theta=[a,b,c,d,e]
        theta=[[min_theta[0],min_theta[1],min_theta[2],min_theta[3],min_theta[4]]]*5
        for i in xrange(100000):
            theta[0]=[(min_theta[0]-span),(min_theta[1]+avg_span),(min_theta[2]+avg_span),(min_theta[3]+avg_span),(min_theta[4]+avg_span)]
            theta[1]=[(min_theta[0]+avg_span),(min_theta[1]-span),(min_theta[2]+avg_span),(min_theta[3]+avg_span),(min_theta[4]+avg_span)]
            theta[2]=[(min_theta[0]+avg_span),(min_theta[1]+avg_span),(min_theta[2]-span),(min_theta[3]+avg_span),(min_theta[4]+avg_span)]
            theta[3]=[(min_theta[0]+avg_span),(min_theta[1]+avg_span),(min_theta[2]+avg_span),(min_theta[3]-span),(min_theta[4]+avg_span)]
            theta[4]=[(min_theta[0]+avg_span),(min_theta[1]+avg_span),(min_theta[2]+avg_span),(min_theta[3]+avg_span),(min_theta[4]-span)]
            val1=theta[0][0]*sample[0]+theta[0][1]*sample[1]+theta[0][2]*sample[2]+theta[0][3]*sample[3]+theta[0][4]
            val2=theta[1][0]*sample[0]+theta[1][1]*sample[1]+theta[1][2]*sample[2]+theta[1][3]*sample[3]+theta[1][4]
            val3=theta[2][0]*sample[0]+theta[2][1]*sample[1]+theta[2][2]*sample[2]+theta[2][3]*sample[3]+theta[2][4]
            val4=theta[3][0]*sample[0]+theta[3][1]*sample[1]+theta[3][2]*sample[2]+theta[3][3]*sample[3]+theta[3][4]
            val5=theta[4][0]*sample[0]+theta[4][1]*sample[1]+theta[4][2]*sample[2]+theta[4][3]*sample[3]+theta[4][4]
            variance=[]
            variance.append((val-val1)*(val-val1))
            variance.append((val-val2)*(val-val2))
            variance.append((val-val3)*(val-val3))
            variance.append((val-val4)*(val-val4))
            variance.append((val-val5)*(val-val5))
            c=0
            for v in variance:
                if v<min:
                    min=v
                    min_theta=theta[c]
                c+=1

        return min_theta


    def calcGuessScore(self,score):

        return score

    def calcGuessTheta(self,score,score_real):
        span=0.001
        k=1.75
        c=-5.5
        variance_start=score*k+c
        min=(score_real-variance_start)*(score_real-variance_start)
        min_theta=[k,c]
        theta=[min_theta[0],min_theta[1]]*2

        for i in xrange(100000):
            theta[0]=[(min_theta[0]-span),(min_theta[1]+span)]
            theta[1]=[(min_theta[0]+span),(min_theta[1]-span)]
            val1=theta[0][0]*score+theta[0][1]
            val2=theta[1][0]*score+theta[1][1]
            variance=[]
            variance.append((score_real-val1)*(score_real-val1))
            variance.append((score_real-val2)*(score_real-val2))
            cnt=0
            for v in variance:
                if v<min:
                    min=v
                    min_theta=theta[cnt]
                cnt+=1

        return min_theta
