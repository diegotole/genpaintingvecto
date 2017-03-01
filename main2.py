from PIL import Image, ImageDraw
import math
import re
import cProfile
import random
import time
from datetime import datetime

from settings import *
from copy import deepcopy
import pickle
import numpy as np

#print np.__path__
#import cv2

class EcoSystem:

    def __init__(self, img_source=None, population_size=10):
        if (img_source is None):
            img_source = "imgs/mona_port.bmp"

        self.img = Image.open(img_source)
        self.w, self.h = self.img.size
        self.vec = None

        self.generation = 0

        self.population = []

        self.population_size = population_size

        self.getTargetVec()

        for i in range(population_size):
            p = Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=i, ischild=0)
            p.createNew()
            p.getFitness(self.vec)
            self.population.append(p)

        self.population.sort(key=lambda x: x.getFitness(self.vec), reverse=False)

    def getTargetVec(self):

        if(self.vec):
            return self.vec

        vec = []

        #px = self.img.load()

        # for row in range(self.w):
        #     r_list = []
        #     for column in range(self.h):
        #         pt = px[row, column]
        #         r_list.append(pt)
        #
        #     vec.append( r_list )



        self.vec = np.array(self.img)
        #self.vec = vec
        return vec


    def evolve(self, n_generations=10):

        n_deaths = int(self.population_size * ECO_GEN_DEATH_RATIO)
        index_limit_kills = self.population_size - n_deaths
        new_comers_counts = int(self.population_size * ECO_NEW_RANDOM_RATIO)

        for g in range(n_generations):

            self.population.sort(key=lambda x: x.getFitness(self.vec), reverse=False)
            self.population = self.population[:index_limit_kills]  #kill bottom

            self.generation += 1

            #add randoms
            for i in range(new_comers_counts):

                p = Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=i, ischild=0)
                p.createNew()
                self.population.append(p)



            n_kids = self.population_size - len(self.population)
            self.MateTopOnes(how_many_kids=n_kids)

        self.population.sort(key=lambda x: x.getFitness(self.vec), reverse=False)

        print "top: %s, error: %s %%" % (self.population[0].fitness, (float(self.population[0].fitness) / (
        self.w * self.h * (pow(255, 2) + pow(255, 2) + pow(255, 2) + pow(255, 2)))))




    def MateTopOnes(self, how_many_kids=1 ):

        start_index = 0
        end_index = abs( int(self.population_size * ECO_ELIGIBLE_PARENTS_RATIO) -1)





        for i in range(how_many_kids):

            genes = []

            p1_ = self.population[random.randint(start_index, end_index)]
            p2_ = self.population[random.randint(start_index, end_index)]


            for x in range(HILL_POLYGONS_PER_PAINT):

                coin = random.randint(0, 1)

                if coin:
                    genes.append(  deepcopy(p1_.polygon_list[i]) )
                else:
                    genes.append(deepcopy(p2_.polygon_list[i]))

            paint = Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=i, ischild=1)
            paint.loadPaint(mypolygon_list=genes)
            paint.mutate()

            self.population.append(paint)









class HillClimb:

    def __init__(self, img_source=None):

        if(img_source is None):
            #img_source = "imgs/mona_port.bmp"
            img_source = "imgs/rsz_mona_lisa.jpg"



        self.img = Image.open(img_source)
        self.w, self.h = self.img.size
        #print "size %s %s" % (self.w, self.h)
        self.vec = None

        self.generation = 0

        self.getTargetVec()

        self.dad = Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=0, ischild=0)
        self.dad.createNew()

    def getChild(self, dad):



        child = Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=0, ischild=1)
        child.loadPaint(mypolygon_list= deepcopy( self.dad.polygon_list ))
        child.mutate()
        child.getFitness(self.vec)

        return child



    def climb(self, turns):

        print "climb called"
        for i in range(turns):

            child = self.getChild(self.dad)

            #print child.getFitness(self.vec), self.dad.getFitness(self.vec)

            if(child.getFitness(self.vec) < self.dad.getFitness(self.vec)):
                self.generation +=1
                self.dad =  deepcopy( child )



        print "top: %s, error: %s %%" % (self.dad.fitness , (float(self.dad.fitness)/  (self.w * self.h * (pow(255,2)+ pow(255,2)+ pow(255,2)) ) ) )
        #print "np - top: %s, error: %s %%" % (self.dad.fitness , (float(self.dad.fitness)/  (self.w * self.h *  np.sum(pow(255,2)+ pow(255,2)+ pow(255,2))  ) ) )


    def getTargetVec(self):

        if(self.vec):
            return self.vec

        #vec_ori = np.transpose(np.array(self.img), (1,0,2))
        vec_ori = np.array(self.img)

        # px = self.img.load()
        #
        # for row in range(self.w):
        #     r_list = []
        #     for column in range(self.h):
        #         pt = px[row, column]
        #         r_list.append(pt)
        #
        #     vec_ori.append( r_list )




        # vec = np.array(self.img)
        # vec.transpose()
        #
        # vec_cv = cv2.imread("imgs/mona_port.bmp")
        #
        # for x in range(200):
        #     for y in range(200):
        #
        #         if( vec_cv[x][y][0] != vec_ori[x][y][0] ):
        #             print "different %s %s" % (x,y)
        #             print vec[x][y], vec_ori[x][y]
        #             return




        self.vec = vec_ori

        return vec_ori


class Brush:

    @staticmethod
    def paintme(im, polygon):

        draw = ImageDraw.Draw(im, 'RGBA')
        draw.polygon(polygon.corner_list, fill=polygon.color)


class Painting:



    def __init__(self, w, h, gen_n, born_n, ischild):

        self.w = w
        self.h = h

        self.gen_n = gen_n
        self.born_n = born_n
        self.ischild = ischild

        self.polygon_list = []
        self.fitness = None

        self.im = Image.new(mode="RGB", size=(w,h))

        #self.draw = ImageDraw.Draw(self.im, 'RGBA')

        #self.polygon_list = mypolygon_list

    def createNew(self):


            #print "creating polygons"
            p_n = self.getPolygonsNumber()
            self.polygon_list = []
            #print "n polygons %s" % self.p
            TEMP = 0
            for i in range(p_n):
                TEMP+=1
                corners = self.getNCorners()


                color = (self.getRandomColor() , self.getRandomColor(), self.getRandomColor(), self.getRandomColor() )
                mypolygon = Polygon(
                        color=color  ,
                        n_corners=corners,
                        w=self.w,
                        h=self.h

                    )



                self.polygon_list.append(mypolygon)



            #self.draw.polygon(  mypolygon.corner_list , fill=mypolygon.color     )
            s = len(self.polygon_list)
            #TEMP = 0
            for i in range(s):
                #TEMP += 1
                #self.draw.polygon(self.polygon_list[i].corner_list, fill=self.polygon_list[i].color)
                Brush.paintme(self.im, polygon=self.polygon_list[i])


    def loadPaint(self, mypolygon_list):
        self.polygon_list = mypolygon_list
        self.fitness = None
        self.im = Image.new(mode="RGB", size=(self.w, self.h))


        s = len(mypolygon_list)
        #TEMP = 0
        for i in range(s):
         #   TEMP +=1
            #self.draw.polygon(mypolygon_list[i].corner_list, fill=mypolygon_list[i].color)
            Brush.paintme(self.im, polygon=self.polygon_list[i])


         #print "RAN %s TIMES" % (TEMP)

    def mutate(self):

        size = len(self.polygon_list)
        redraw = 0
        for i in range(size):
            self.polygon_list[i].mutate()

        self.loadPaint(self.polygon_list)


    def getFitness(self, target):
        #numpy euclidean distance
        if (self.fitness):
            # print "using cache"
            return self.fitness

        fitness = 0

        px = np.array(self.im)
        #px = np.transpose(np.array(self.im), (1,0,2))


        #fitness = np.sqrt(     np.sum(     ((px - target) ** 2)    )    )
        fitness =      np.sum(     ((px - target) ** 2)    )

        w = self.w
        h = self.h


        self.fitness = fitness
        return fitness



    def getFitness_new(self, target):

        # if (self.fitness):
        #     # print "using cache"
        #     return self.fitness

        fitness = 0
        px = self.im.load()

        w = self.w
        h = self.h

        calc2 = self.fitness_calc2

        fitness = reduce(
            (lambda x,y: x+y),
            [    calc2(row, column, px, target)               for column in range(h)         for row in range(w)]
        )

        self.fitness = fitness
        return fitness



    def getFitness_current(self, target):


        if(self.fitness):
            #print "using cache"
            return self.fitness

        #self.getFitness2(target)

        fitness = 0
        px = self.im.load()

        w = self.w
        h = self.h

        #calc2 = self.fitness_calc2

        # fitness = reduce(
        #     (lambda x,y: x+y),
        #     [    calc2(row, column, px, target)               for column in range(h)         for row in range(w)]
        # )
        # ONLY_RED = 0
        # ONLY_GREEN = 0
        # ONLY_BLUE = 0
        #
        # ONLY_REDns = 0
        # ONLY_GREENns = 0
        # ONLY_BLUEns = 0



        for row in range(h):
            for column in range(w):
                r, g, b = px[row, column]

                tr, tg, tb = target[row][column]

                # ONLY_RED +=  (r-tr)**2
                # ONLY_GREEN += ( g-tg )**2
                # ONLY_BLUE += (b- tb)**2
                #
                # ONLY_REDns += (r - tr)
                # ONLY_GREENns += (g - tg)
                # ONLY_BLUEns += (b - tb)




                fitness += (  ((r - tr) ** 2)      +    ((g - tg) ** 2)     + ((b - tb) ** 2)     )


        self.fitness = fitness

        #print ONLY_RED, ONLY_GREEN, ONLY_BLUE, ONLY_REDns, ONLY_GREENns, ONLY_BLUEns

        return fitness

    def fitness_calc2(self, row, column, px, target):

        r, g, b = px[row, column]

        tr, tg, tb = target[row][column]

        return (r - tr)**2 + (g - tg)**2 + (b - tb)**2



    def getPolygonsNumber(self):

        #return 50
        #return random.randint(1, 250)
        return HILL_POLYGONS_PER_PAINT


    def getNCorners(self):

        #return random.randint(3, 10)
        return HILL_POLYGONS_N_VERTICES

    def getRandomColor(self):
        #print random.randint(0,255)
        return random.randint(HILL_COLOR_MIN_VALUE,HILL_COLOR_MAX_VALUE)


class Polygon:

    def __init__(self, color, n_corners, w, h):

        self.w = w
        self.h = h
        self.origin = self.getOrigin()

        self.color = color
        self.corner_list = [ self.getPtCoord()  for i in range(n_corners)   ]


    def getOrigin(self):

        x = random.randint(0, self.w )
        y = random.randint(0, self.h)

        return (x,y)

    def getPtCoord(self):



        x = min(max(0, self.origin[0]+ random.randint(
            -HILL_POLYGON_ORIGIN_TO_VERTICE_MAX_DISTANCE, HILL_POLYGON_ORIGIN_TO_VERTICE_MAX_DISTANCE)
                    ), self.w                     )

        y = min(max(0, self.origin[1] + random.randint(
            -HILL_POLYGON_ORIGIN_TO_VERTICE_MAX_DISTANCE, HILL_POLYGON_ORIGIN_TO_VERTICE_MAX_DISTANCE)
                    ), self.h                   )


        return (x,y)

    def mutateColor(self, color):

        newcolor = abs(color + ( -HILL_MUTATION_COLOR_DISTANCE ** random.randint(1,2) )) % 256
        return newcolor

    def mutate(self):

        size = len(self.corner_list)
        redraw = 0

        for i in range(size):

            if(random.randint(1,HILL_MUTATION_CORNER_MOVE_RATE) == 1):
                #coord will move
                self.corner_list[i] = self.getPtCoord()
                redraw += 1


        if ( random.randint(1, HILL_MUTATION_CORNER_ADD_RATE) == 1):
            #add point

            self.corner_list.append( self.getPtCoord() )
            redraw += 1

        if ((random.randint(1, HILL_MUTATION_CORNER_REMOVE_RATE) == 1)  and ( size > 3  )):
            # remove point

            random_index = random.randint(0, len(self.corner_list) -1)

            self.corner_list.pop(random_index)
            redraw += 1

        if (random.randint(1, HILL_MUTATION_COLOR_CHANGE_RATE) == 1):
            #change RED
            self.color = (self.mutateColor( self.color[0] ) ,self.color[1] ,self.color[2], self.color[3]   )
            redraw += 1

        if (random.randint(1, HILL_MUTATION_COLOR_CHANGE_RATE) == 1):
            #change GREEN
            self.color = ( self.color[0],  self.mutateColor( self.color[1] ) , self.color[2], self.color[3]  )
            redraw += 1

        if (random.randint(1, HILL_MUTATION_COLOR_CHANGE_RATE) == 1):
            #change BLUE
            self.color = (self.color[0], self.color[1], self.mutateColor( self.color[2] ), self.color[3])
            redraw += 1

        if (random.randint(1, 10) == 1):
            #change ALPHA
            self.color = (self.color[0],self.color[1],self.color[2],self.mutateColor( self.color[3] ))
            redraw += 1

        #print redraw

if __name__ == "__main__":

    print "start"
    # hill = HillClimb()
    # hill.climb(1000)
    #
    # test1  = Painting( w=hill.w, h=hill.h, gen_n =0, born_n=0, ischild=0 )
    # test1.loadPaint(hill.dad.polygon_list)
    #
    # print hill.dad.getFitness(hill.vec)
    # print test1.getFitness(hill.vec)
    #
    # print hill.generation



    #eco = EcoSystem(population_size=10)
    #eco.evolve(10)
    #eco.evolve(1000)
    hill = HillClimb()
    #hill.dad.loadPaint(  pickle.load(open( 'brain_cache/besthill9', 'r' )) )
    #hill.dad.im.show(title="zero")
    print hill.dad.getFitness(hill.vec  )
    hill.climb(150000)
    hill.dad.im.show()
    #hill.climb(1000)

    # vec_ori = []
    # mynp1 = np.array( hill.img )
    #mynp2 = np.array(hill.img.load())
    #mynp1 = np.transpose(mynp1, (1,0,2))


    # px = hill.img.load()
    #
    # for row in range(200):
    #     r_list = []
    #     for column in range(200):
    #         pt = px[row, column]
    #         r_list.append(pt)
    #
    #     vec_ori.append(r_list)
    #
    # COUNT1 = 0
    # COUNT2 = 0
    #
    # for x in range(200):
    #     for y in range(200):
    #
    #         r, g, b = px[x, y]
    #
    #         np1r, np1g, np1b =   mynp1[x][y]
    #         np2r, np2g, np2b =   mynp1[y][x]
    #
    #         if((np1r !=r) or (np1g != g) or (np1b != b) ) :
    #             COUNT1+=1
    #
    #
    #         elif((np2r !=r) or (np2g != g) or (np2b != b) ) :
    #              COUNT2+=1
    #
    #
    #
    #
    # print COUNT1, COUNT2










