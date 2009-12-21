import direct.directbase.DirectStart
from direct.interval.IntervalGlobal import * #to make things flash on collisions
from pandac.PandaModules import *
from direct.showbase import DirectObject #so that we can accept messages


class World( DirectObject.DirectObject ):
    def __init__( self ):
        #initialize traverser
        base.cTrav = CollisionTraverser()

        #initialize handler
        self.collHandEvent=CollisionHandlerEvent()
        self.collHandEvent.addInPattern('into-%in')
        self.collHandEvent.addOutPattern('outof-%in')

        #initialize collision count (for unique collision strings)
        self.collCount=0

        #load a model.  reparent it to the camera so we can move it.
        s = loader.loadModel('smiley')	
        s.reparentTo(camera)
        s.setPos(0, 25,0)

        #setup a collision solid for this model
        sColl=self.initCollisionSphere(s, True)
        print sColl[1]
        print "*" * 20

        #add this object to the traverser
        base.cTrav .addCollider(sColl[0] , self.collHandEvent)

        #accept the events sent by the collisions
        self.accept( 'into-' + sColl[1], self.collide3)
        self.accept( 'outof-' + sColl[1], self.collide4)
        print sColl[1]

        #load a model.  
        t = loader.loadModel('smiley')	
        t.reparentTo(render)
        t.setPos(5, 25,0)

        #setup a collision solid for this model
        tColl=self.initCollisionSphere(t, True)

        #add this object to the traverser
        base.cTrav .addCollider(tColl[0], self.collHandEvent)

        #accept the events sent by the collisions
        self.accept( 'into-' + tColl[1], self.collide)
        self.accept( 'outof-' + tColl[1], self.collide2)
        print tColl[1]

        print "WERT"


    def collide(self, collEntry):
        print "WERT: object has collided into another object"
        Sequence(Func(collEntry.getFromNodePath().getParent().setColor, VBase4(1,0,0,1)),
                 Wait(.2),
                 Func(collEntry.getFromNodePath().getParent().setColor, VBase4(0,1,0,1)),
                 Wait(.2),
                 Func(collEntry.getFromNodePath().getParent().setColor, VBase4(1,1,1,1))).start()			     
                

    def collide2(self, collEntry):
        #collEntry.getFromNodePath().getParent().remove()
        print "WERT.: object is no longer colliding with another object"
        
    def collide3(self, collEntry):
        #collEntry.getFromNodePath().getParent().remove()
        print "WERT2: object has collided into another object"

    def collide4(self, collEntry):
        #collEntry.getFromNodePath().getParent().remove()
        print "WERT2: object is no longer colliding with another object"
        

    def initCollisionSphere( self, obj, show=False):
        #get the size of the object for the collision sphere
        bounds = obj.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius()*1.1

        #create a collision sphere and name it something understandable
        collSphereStr = 'CollisionHull' +str(self.collCount)+"_"+obj.getName()
        self.collCount+=1
        cNode=CollisionNode(collSphereStr)
        cNode.addSolid(CollisionSphere(center, radius ) )

        cNodepath=obj.attachNewNode(cNode)
        if show:
            cNodepath.show()

        # return a tuple with the collision node and its corrsponding string
        # return the collison node so that the bitmask can be set
        return (cNodepath,collSphereStr )



#run the world.  move around with the mouse to create collisions
w= World()
run()
