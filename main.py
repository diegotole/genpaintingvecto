
from PIL import Image, ImageDraw

import re
import cProfile
import random

#im = Image.open("imgs/thestarrynight.jpg")

#w,h =  im.size

#px = im.load()



#open images
#for pixel in px_list:
#
#    print pixel

#for x in range(w):
#    for y in range(h):
#
#        print px[x,y]
#        break
#    break



#extract pixel info

class EcoSystem:

    def __init__(self, img_source, population_size=10, islands=1):

        #get target image size
        self.img = Image.open(img_source)
        self.w,self.h = self.img.size
        self.vec = None
        #get population number
        self.population_size = population_size
        self.generation = 1
        #generate initial population

        #initial_id = "gen-1-n-%s"
        self.population = []
        #self.population = [  Painting(self.w,self.h, gen_n=self.generation, born_n=i)   for i in range(population_size)    ]

        for i in range(population_size):
            self.population.append(   Painting(w=self.w,h=self.h, gen_n=self.generation, born_n=i, ischild=0,mypolygon_list=[])     )

        print "population created"
        self.getTargetVec()

        for p in self.population:
            p.getFitness(self.vec)


        self.population.sort(key=lambda x: x.getFitness(self.vec), reverse=False)



        #for i in range(islands):

        #for p in range(population_size):

        #    self.append(   )

    def evolve(self, n_generations=10):

        print "evolve called"

        percent20 = int(self.population_size * 0.2)
        index_limit = self.population_size - percent20
        percent10  = int(self.population_size * 0.1)

        for g in range(n_generations):

            #rank by fitness
            self.population.sort(key=lambda x: x.getFitness(self.vec), reverse=False)
            #kill bottom 20%


            #print index_limit
            self.population = self.population[:index_limit]

            self.generation += 1
            #add random 10%
            map(self.population.append,

                [Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=i, ischild=0 , mypolygon_list=[] ) for i in range(percent10)]

                )

            #add 10% of kids
            n_kids = self.population_size - len(self.population)
            self.MateTopOnes(how_many_kids=n_kids)

            #if(redraw):


            for p in self.population:
                p.getFitness(self.vec)

        self.population.sort(key=lambda x: x.getFitness(self.vec), reverse=False)
        print "top: %s, error: %s %%" % (self.population[0].fitness , (float(self.population[0].fitness)/  (self.w * self.h * (pow(255,2)+ pow(255,2)+ pow(255,2)+ pow(255,2)) ) ) )

    def MateTopOnes(self, how_many_kids=1, top_parents=0.1):

        start_index = 0
        end_index = self.population_size * top_parents


        for i in range(how_many_kids):

            p1_ = self.population[random.randint(start_index, end_index)]
            p2_ = self.population[random.randint(start_index, end_index)]


            genes = []
            #p1 loop
            for p in p1_.polygon_list:

                if(random.randint(0,1)):
                    genes.append(p)


            #p2 loop
            for p in p2_.polygon_list:

                if (random.randint(0, 1)):
                    genes.append(p)

            p = Painting(w=self.w, h=self.h, gen_n=self.generation, born_n=i, ischild=1 , mypolygon_list=genes)
            redraw = p.mutate()
            #if(redraw):
            #    print "got a mutation %s" % redraw
            self.population.append( p )
           # self.population.append(
            #
           #     Painting(w=self.w, h=self.h, gen_n=self.generation   ,born_n=i, mypolygon_list=genes)
            #
           # )
            return redraw

    def getTargetVec(self):

        if(self.vec):
            return self.vec

        vec = []

        px = self.img.load()

        for row in range(self.w):
            r_list = []
            for column in range(self.h):
                pt = px[row, column]
                r_list.append(pt)

            vec.append( r_list )

        self.vec = vec

        return vec






class Painting:



    def __init__(self, w, h, gen_n, born_n, ischild,mypolygon_list = []):

        self.w = w
        self.h = h

        self.gen_n = gen_n
        self.born_n = born_n
        self.ischild = ischild


        #self.color = (self.getRandomColor() , self.getRandomColor(), self.getRandomColor() )

        self.fitness = None
        #self.img_id = img_id

        self.im = Image.new(mode="RGB", size=(w,h), color=1)
        #Image.n
        self.draw = ImageDraw.Draw(self.im, 'RGBA')

        self.polygon_list = mypolygon_list

        if(len(mypolygon_list) == 0):

            #print "creating polygons"
            self.p = self.getPolygonsNumber()
            #print "n polygons %s" % self.p
            for i in range(self.p):
                corners = self.getNCorners()

                #print "n corners %s" % corners
                #corner_list = []
                #for c in range(corners):
                    #x,y = self.getPtCoord()
                    #corner_list.append( (x,y)  )
                color = (self.getRandomColor() , self.getRandomColor(), self.getRandomColor(), self.getRandomColor() )
                mypolygon = Polygon(
                        color=color  ,
                        n_corners=corners,
                        w=self.w,
                        h=self.h

                    )



                #self.polygon_list.append(corner_list)
                #self.draw.polygon(corner_list, fill=(self.getRandomColor() , self.getRandomColor(), self.getRandomColor() ))

                self.polygon_list.append(mypolygon)
                self.draw.polygon(  mypolygon.corner_list , fill=mypolygon.color     )
        else:
        #    print "list passed: %s" % mypolygon_list
                redraw = self.mutate()
                s = len(mypolygon_list)
                for i in range(s):

                    self.draw.polygon(mypolygon_list[i].corner_list, fill=mypolygon_list[i].color)



        #    if()
        #self.im.save("gallery/gen-%s-b-%s.jpg" % (gen_n, born_n) , 'JPEG')



    def mutate(self):

        size = len(self.polygon_list)
        redraw = 0
        for i in range(size):
            redraw += self.polygon_list[i].mutate()

        return redraw

    def getFitness(self, target):

        if(self.fitness):
            return self.fitness

        fitness = 0
        px = self.im.load()

        #for row_n in target:
        #    for column in row:
        for row in range( self.w ):
            for column in range(self.h):

                r,g,b = px[row, column]
                tr, tg, tb = target[row][column]

                fitness +=  pow( r-tr , 2 ) + pow(g - tg , 2) + pow(b - tb, 2)

        self.fitness = fitness

        return fitness



    def getPolygonsNumber(self):

        return 50
        #return random.randint(1, 100)



    def getNCorners(self):

        return random.randint(3, 10)

    def getRandomColor(self):

        return random.randint(0,255)


class Polygon:


    def mutate(self):

        size = len(self.corner_list)
        redraw = 0

        for i in range(size):

            if(random.randint(1,1000) == 1):
                #coord will move
                redraw +=1
                self.corner_list[i] = self.getPtCoord()



        if ( random.randint(1, 1000) == 1):
            #add point

            self.corner_list.append( self.getPtCoord() )

            redraw += 1

        if ((random.randint(1, 1000) == 1)  and ( size > 3  )):
            # remove point

            random_index = random.randint(0, size -1)

            self.corner_list.pop(random_index)

            redraw += 1


        if (random.randint(1, 1000) == 1):
            #change RED
            self.color = (random.randint(0,255) ,self.color[1] ,self.color[2], self.color[3]   )
            redraw += 1

        if (random.randint(1, 1000) == 1):
            #change GREEN
            self.color = ( self.color[0],  random.randint(0,255) , self.color[2], self.color[3]  )
            redraw += 1

        if (random.randint(1, 1000) == 1):
            #change BLUE
            self.color = (self.color[0], self.color[1], random.randint(0,255), self.color[3])
            redraw += 1

        if (random.randint(1, 1000) == 1):
            #change ALPHA
            self.color = (self.color[1],self.color[2],self.color[3],random.randint(0,255))
            redraw += 1

        return redraw



    def getPtCoord(self):

        x = random.randint(0, self.w )
        y = random.randint(0, self.h)

        return (x,y)

    def __init__(self, color, n_corners, w, h):

        self.w = w
        self.h = h

        self.color = color
        self.corner_list = [ self.getPtCoord()  for i in range(n_corners)   ]





if __name__ == "__main__":

    eco = EcoSystem("imgs/rsz_thestarrynight.jpg")


    eco.evolve(10)

    current_top = eco.population[0]



    #for p in eco.population:
    #    print p.fitness

    #print eco.population[0].fitness

    #eco.evolve(100)

    #print eco.population[0].fitness

    #eco.evolve(100)

    #print eco.population[0].fitness





