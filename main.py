""" 
End of Ages




"""
#System Modules
import random, sys, os, math

#Panda3d Related
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectGui import *

#Panda3d Modules
from pandac.PandaModules import *

#Panda AI module
#from libpandaai import *

#EoA Modules
from EoA import *




# Figure out what directory this program is in.
MYDIR=os.path.abspath(sys.path[0])
MYDIR=Filename.fromOsSpecific(MYDIR).getFullpath()


font = loader.loadFont("cmss12")
                        
class Universe(DirectObject):
    '''Universe
    Here we set up the game universe.'''
    def __init__(self):
        base.setFrameRateMeter(True)
        render.analyze() 
        base.win.setClearColor(Vec4(0,0,1,1))
        
        
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.  
        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        
        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        self.elapsed = 0
        self.mouse_last_x = 0
        self.mouse_last_y = 0
        self.last = 0
        self.mousebtn = [0,0,0]
        
        '''Set up input keys'''
        self.configureInput()
          
        ''' Set up lights and filters '''
        #self.setupLightsAndFilters()  
          
        '''Set up Actors'''
        self.Actors = {}
        #Create the main character
        self.Actors['PC'] = EoAActor(name = "PC", modelName="ralph", startPos=self.environ.find("**/start_point").getPos())
        #self.Actors['Pet'] = EoAActor(name = "Pet", modelName="eggCharacter1", startPos=self.environ.find("**/start_point").getPos(), scale=.05)
        #self.Actors['Pet'].loop('run')
        
        #Give the main character some weapons
        self.Actors['PC'].equipItem(location='primary', modelLocation='RightHand', item='sword', itemPos=[.11,.19,.06], itemHpr=[0,0,90], itemScale=1)
        self.Actors['PC'].equipItem(location='secondard', modelLocation='LeftHand', item='sword', itemPos=[.11,0,.06], itemHpr=[180,0,90], itemScale=1)
        
        ''' Set up Collision Detection '''
        self.setupCollisionDetection()
        
        
        #add move task to handle character movement
        taskMgr.add(self.move,"moveTask")
        
        # Game state variables
        self.isMoving = False

        # Set up the camera
        base.disableMouse()
        base.camera.setPos(self.Actors['PC'].getX(),self.Actors['PC'].getY()+10,2)

        """
        '''Setup AI'''
        self.AIWorld = AIWorld(render)
        taskMgr.add(self.AIUpdate,"AIUpdate")

        self.AIChar = AICharacter('Pet', self.Actors['Pet'], 100, .2, 10.0)
        self.AIWorld.addAiChar(self.AIChar)
        self.AIBehaviors = self.AIChar.getAiBehaviors() 
        self.AIBehaviors.pursue(self.Actors['PC'], 1)
        

        
        '''TESTING - FLOCKING BEHAVIOR'''
        self.flockersModel = [] #list of flocker models
        self.flockers = [] #list of flocker AI character
        self.flockersAI = [] #flocker AI behavior
        self.flockObject = Flock(0, 45, 10, 4, 2, 5) #create the flock
        self.flockCollide = []
        self.flockCollideHandler = []
        for i in range(5): #create 100 flockers
            #create flocker model
            self.flockersModel.append(EoAActor(name = "Pet%s" % (i), 
                                modelName="trex/trex", 
                                startPos=self.environ.find("**/start_point").getPos(), 
                                scale=.1, modelStates={'run':'models/trex/trex-run'}))
            self.flockersModel[i].loop('run')
                                
            #create flocker AI character
            self.flockers.append(AICharacter('Pet', self.flockersModel[i], 
                                100, .2, 10.0))
            
            #set position of ai model
            self.flockersModel[i].setPos(Vec3(
                self.environ.find("**/start_point").getPos()[0] + i*7*random.random(), 
                self.environ.find("**/start_point").getPos()[1] - i*7*random.random(), 
                self.environ.find("**/start_point").getPos()[2])) 
            
            #Add AI to flock
            self.flockObject.addAiChar(self.flockers[i])
            self.flockersAI.append(self.flockers[i].getAiBehaviors())
            self.flockersAI[i].flock(.9) #set flock priority
            self.flockersAI[i].wander(200.0, False, 100.0, .7) #set wander
            self.flockersAI[i].pursue(self.Actors['PC'], .2) #set pursue
            
            self.flockCollide.append(self.flockersModel[i].attachNewNode(self.PCGroundCol))
            self.flockCollideHandler.append(CollisionHandlerQueue())
            self.cTrav.addCollider(self.flockCollide[i], self.flockCollideHandler[i])
            
        self.AIWorld.addFlock(self.flockObject) #add flock to world
        """

               
        
    '''Input'''
    def setKey(self, key, value):
        '''Set up keyboard keys'''
        self.keyMap[key] = value
        
    def setMouseBtn(self, btn, value):
        '''Set up mouse keys'''
        self.mousebtn[btn] = value
    
    def configureInput(self):
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0, "cam-left":0, "cam-right":0, "cam-up":0, "cam-down":0}
        '''Set up input keys
        ToDo - read from config file'''
        # Accept the control keys for movement and rotation
        self.accept("escape", sys.exit)

        #Movement Keys 
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("s", self.setKey, ["backward",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("s-up", self.setKey, ["backward",0])

        #Camera Control Keys
        self.accept("arrow_left", self.setKey, ["cam-left",1])
        self.accept("arrow_right", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["cam-left",0])
        self.accept("arrow_right-up", self.setKey, ["cam-right",0])
        self.accept("arrow_up", self.setKey, ["cam-up",1])
        self.accept("arrow_down", self.setKey, ["cam-down",1])
        self.accept("arrow_up-up", self.setKey, ["cam-up",0])
        self.accept("arrow_down-up", self.setKey, ["cam-down",0])

        #mouse keys
        #mouse1 is left click
        self.accept("mouse1", self.setMouseBtn, [0, 1])
        self.accept("mouse1-up", self.setMouseBtn, [0, 0])
        #mouse3 is right click
        self.accept("mouse3", self.setMouseBtn, [1, 1])
        self.accept("mouse3-up", self.setMouseBtn, [1, 0]) 
        #mouse2 is scroll wheel click
        self.accept("mouse2", self.setMouseBtn, [2, 1])
        self.accept("mouse2-up", self.setMouseBtn, [2, 0])

     
    '''Collision'''
    def setupCollisionDetection(self):
        '''Collision Detectiona
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
        '''

        self.cTrav = CollisionTraverser()

        self.PCGroundRay = CollisionRay()
        self.PCGroundRay.setOrigin(0,0,1000)
        self.PCGroundRay.setDirection(0,0,-1)
        self.PCGroundCol = CollisionNode('ralphRay')
        self.PCGroundCol.addSolid(self.PCGroundRay)
        self.PCGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.PCGroundCol.setIntoCollideMask(BitMask32.allOff())


        self.PCGroundColNp = self.Actors['PC'].attachNewNode(self.PCGroundCol)

        self.PCGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.PCGroundColNp, self.PCGroundHandler)
        
        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
        '''Collision Rays'''
        # Uncomment this line to see the collision rays
        #self.PCGroundColNp.show()
        #self.camGroundColNp.show()
       


        #Uncomment this line to show a visual representation of the 
        #collisions occuring
        #self.cTrav.showCollisions(render)
        



    '''Filters'''
    def setupLightsAndFilters(self):
        ''' Filters '''
        #Set up some filters
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setBloom(blend=(0,0,0,1), desat=-0.5, intensity=1.0, size="small")
        if (filterok == False):
            print "Your video card cannot handle this"
            return
        self.glowSize=.1
       

        dlight = DirectionalLight('dlight')
        alight = AmbientLight('alight')
        
        dlnp = render.attachNewNode(dlight) 
        alnp = render.attachNewNode(alight)
        dlight.setColor(Vec4(1.0, 1.0, 1.0, 1))
        alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        dlnp.setHpr(0, -60, 0) 
        render.setLight(dlnp)
        render.setLight(alnp)
        self.filters.setBloom(blend=(0,0,0,1), desat=-0.5, intensity=3.0, size=self.glowSize)
        

        
    '''AI'''    
    def AIUpdate(self,task):
        '''AIUpdate
        updates AIWorld'''
        self.AIWorld.update()
        return Task.cont    
    
    '''Move task'''
    def move(self, task):
        ''' Accepts arrow keys to move either the player or the menu cursor, Also deals with grid checking and collision detection '''
        # Get the time elapsed since last frame. We need this
        # for framerate-independent movement.
        elapsed = globalClock.getDt()

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.Actors['PC'].getPos()

        # If a move-key is pressed, move ralph in the specified direction.
        if (self.keyMap["left"]!=0):
            self.Actors['PC'].setH(self.Actors['PC'].getH() + elapsed *200)  #Move character

        if (self.keyMap["right"]!=0):
            self.Actors['PC'].setH(self.Actors['PC'].getH() - elapsed*200)

        if (self.keyMap["forward"]!=0):
            self.Actors['PC'].setY(self.Actors['PC'], -(elapsed*25))
        
        if (self.keyMap["backward"]!=0):
            self.Actors['PC'].setY(self.Actors['PC'], +(elapsed*25))

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if self.keyMap["forward"] !=0 or self.keyMap["left"] !=0 or self.keyMap["right"] !=0 or self.keyMap["backward"] != 0 or self.mousebtn[0] and self.mousebtn[1]:
            if self.isMoving is False:
                self.Actors['PC'].loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.Actors['PC'].stop()
                self.Actors['PC'].pose("walk",5)
                self.isMoving = False
            
        '''Collision'''
        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.PCGroundHandler.getNumEntries()):
            entry = self.PCGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.Actors['PC'].setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.Actors['PC'].setPos(startpos)

        '''
            Update Name
        '''
        #OnscreenText(text='Char', style=1, fg=(1,1,1,1), font = font,
        #    pos = (0,0,0), align=TextNode.ARight, scale = .07)
        
        '''
            MOVE CAMERA
        '''
        
        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.
        base.camera.lookAt(self.Actors['PC'])
        
        #Control camera based on movement input
        if (self.keyMap["left"]!=0):
            base.camera.setX(base.camera, +(elapsed*34))    #Move camera
        if (self.keyMap["right"]!=0):
            base.camera.setX(base.camera, -(elapsed*34) )
            
        #Control camera based on camera control input
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -(elapsed*20))
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +(elapsed*20))
        if (self.keyMap["cam-up"]!=0):
            base.camera.setY(base.camera, -(elapsed*20))
        if (self.keyMap["cam-down"]!=0):
            base.camera.setY(base.camera, +(elapsed*20))
        
        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.
        camvec = self.Actors['PC'].getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0
            
        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.Actors['PC'].getZ() + 2.0):
            base.camera.setZ(self.Actors['PC'].getZ() + 2.0)
            
        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        	
        self.floater.setPos(self.Actors['PC'].getPos())
        self.floater.setZ(self.Actors['PC'].getZ() + 2.0)
        base.camera.lookAt(self.floater)
        
            
        '''Control Camera
        Allow mouse to control the camera
        '''
        # figure out how much the mouse has moved (in pixels) if clicked
        if self.mousebtn[0]:
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()

            #Check x
            if x < self.mouse_last_x:
                base.camera.setX(base.camera, +(elapsed*34))    #Move camera
                #self.Actors['PC'].setH(self.Actors['PC'].getH() + elapsed *200)  #Move character
                base.camera.lookAt(self.floater)
            elif x > self.mouse_last_x:
                base.camera.setX(base.camera, -(elapsed*34) )
                #self.Actors['PC'].setH(self.Actors['PC'].getH() - elapsed*200)
                base.camera.lookAt(self.floater)

            
            #Finished checking previous and current mouse location
            #Save the current x,y as last_x and last_y so we can compare in the next frame
            self.mouse_last_x = md.getX()
            self.mouse_last_y = md.getY()            
        
        if self.mousebtn[0] and self.mousebtn[1]:
            self.Actors['PC'].setY(self.Actors['PC'], -(elapsed*25))
        
        
        '''We're done with the task'''
        return Task.cont

w = Universe()
run()

