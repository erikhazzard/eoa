"""
End of Ages

"""
"""System Imports"""
import sys, math, os
from random import random

"""Panda Module imports"""
from pandac.PandaModules import *

loadPrcFileData("", """
show-frame-rate-meter #t
""")
loadPrcFileData('',"""
sync-video 0
""")

"""Direct modules"""
import direct.directbase.DirectStart
from direct.showbase.InputStateGlobal import inputState
from direct.actor.Actor import Actor
from direct.controls.GravityWalker import GravityWalker
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.filter.CommonFilters import CommonFilters


from EoALib import *


class Universe(DirectObject, EoAUniverse):
    """Universe
    -----------
    Out main class, the Universe"""
   
    def __init__(self):
        """Initialize our world
        
            Set up environment
            Set up lighting
            Set up physics
            Set up actors
            Set up collisions
        """          
        
        """------------INIT---------------------------------------"""
        """Set up input"""
        self.init_controls()
        
        """Set up environment"""
        self.init_environment()
        
        """Set up lights"""
        self.init_lights()
        
        """Set up physics"""
        self.init_physics()
        
        """Set up collisions"""
        self.init_collisions()

        """Set up actors"""
        self.init_actors()  
  
        """Set up camera"""
        self.init_camera()
        

        """--------------------------------------------------------"""
        
        """------------TASKS---------------------------------------"""
        self.elapsed = 0.0
        
        """Set up tasks"""
        #Set up movement update
        base.taskMgr.add(self.update_movement, 'update_movement')
        
        #Set up camera update
        base.taskMgr.add(self.update_camera, 'update_camera')
        
        #Keep track of entities, update animation if they are moving
        base.taskMgr.add(self.update_entity_animations, 'update_entity_animations')
        
        #Setup mouse collision test
        base.taskMgr.add(self.update_mouse_collisions, 'update_mouse_collisions')
        """--------------------------------------------------------"""

    """=======Controls=========
        CONTROLS SETUP
        ======================="""
    def init_controls(self):
        """Set up controls.  Use direct input and keymaps
        """
        
        # Now, assign some controls to the events that the GravityWalker will
        #watch for 
        #Create a dictionary to save controls
        """WASD Settings"""
        self.controls = {}
      
        self.controls['forwardControl'] = inputState.watch('forward', 'w', 
                                'w-up', inputSource=inputState.WASD)
        self.controls['reverseControl'] = inputState.watch('reverse', 's', 
                                's-up', inputSource=inputState.WASD)
        self.controls['turnLeftControl'] = inputState.watch('turnLeft', 'a',
                                'a-up', inputSource=inputState.WASD)
        self.controls['turnRightControl'] = inputState.watch('turnRight', 'd', 
                                'd-up', inputSource=inputState.WASD)
        self.controls['jumpControl'] = inputState.watch('jump', 'space', 
                                'space-up', inputSource=inputState.Keyboard)
        
        self.controls['isMoving'] = False
        
        """Key map settings"""
        self.controls['key_map'] = {"cam_left":0, "cam_right":0, "cam_up":0,
                                    "cam_down":0, "mouse1":0, "mouse2": 0,
                                    "mouse3": 0}
        
        #Camera Control Keys
        self.accept("arrow_left", self.controls_set_key, ["cam_left",1])
        self.accept("arrow_right", self.controls_set_key, ["cam_right",1])
        self.accept("arrow_left-up", self.controls_set_key, ["cam_left",0])
        self.accept("arrow_right-up", self.controls_set_key, ["cam_right",0])
        self.accept("arrow_up", self.controls_set_key, ["cam_up",1])
        self.accept("arrow_down", self.controls_set_key, ["cam_down",1])
        self.accept("arrow_up-up", self.controls_set_key, ["cam_up",0])
        self.accept("arrow_down-up", self.controls_set_key, ["cam_down",0])

        #mouse keys
        #mouse1 is left click
        self.accept("mouse1", self.controls_set_key, ["mouse1", 1])
        self.accept("mouse1-up", self.controls_set_key, ["mouse1", 0])
        #mouse3 is right click
        self.accept("mouse3", self.controls_set_key, ["mouse3", 1])
        self.accept("mouse3-up", self.controls_set_key, ["mouse3", 0]) 
        #mouse2 is scroll wheel click
        self.accept("mouse2", self.controls_set_key, ["mouse2", 1])
        self.accept("mouse2-up", self.controls_set_key, ["mouse2", 0])
        base.accept ('escape', sys.exit)  # hit escape to quit!
        
    def controls_set_key(self, key, value):
        """Set up keyboard keys"""
        self.controls['key_map'][key] = value
        
    
    """=======Lights===========
        LIGHTS SETUP
        ======================="""
    def init_lights(self):
        """init_lights
        Set up light system
        """
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setBloom(blend=(0,0,0,1), desat=-0.5, 
                        intensity=1.0, size="small")
        if (filterok == False):
            print "Your video card cannot handle this"
            return
        self.glowSize=.1
        
        # Create a simple directional light
        self.lights = {}
        
        #Set up directional light
        self.lights['dlight'] = render.attachNewNode (DirectionalLight\
                                ('DirectionalLight'))
        self.lights['dlight'].setColor(VBase4(1, 1, 1, 1))
        render.setLight(self.lights['dlight'])
        self.lights['dlight'].setPos(1, 1, 1)
        self.lights['dlight'].lookAt(0, 0, 0)
        
        #Sun position
        self.lights['sunPos'] = 0
        # Create an ambient light
        self.lights['alight'] = AmbientLight('AmbientLight')
        self.lights['alight'].setColor(VBase4(0.5, 0.5, 0.5, 0.2))
        self.lights['alnp'] = render.attachNewNode(self.lights['alight'])
        render.setLight(self.lights['alnp'])
    
        #self.shader = loader.loadShader("g.sha")
        #render.setShader(self.shader)
        
    """=======Actors===========
        ACTOR SETUP
        ======================="""
    def init_actors(self):
        """init_actors
        Setup actors"""
        #Create a dictionary to hold all our actors
        self.entities = {} 
        
        #Setup the PC entity
        self.entities['PC'] = Entity(gravity_walker=True,modelName="boxman", 
                                    name='PC', startPos=(0,0,5))
               
        for i in range(10):
            self.entities['NPC_'+str(i)] = Entity(modelName="boxman", 
                        name='NPC_'+str(i),startPos=(random()*i+i,
                                                    random()*i+i,30))
        
    """=======Camera===========
        CAMERA SETUP
        ======================="""
    def init_camera(self):
        """init_camera
        Set up the camera.  Allow for camera autofollow, freemove, etc"""
        
        base.disableMouse()
        base.camera.reparentTo(self.entities['PC'].Actor)
        base.camera.setPos(0, -15, 25)
        base.camera.lookAt(self.entities['PC'].Actor)
        angledegrees = 2
        angleradians = angledegrees * (math.pi / 180.0)
        base.camera.setPos(20*math.sin(angleradians),-20.0*\
                    math.cos(angleradians),3)
        base.camera.setHpr(angledegrees, 0, 0)
        
        """Set up some camera controls"""
        self.controls['camera_settings'] = {}
        #Camera timer is used to control how long a button is being held
        #to control the camera
        self.controls['camera_settings']['timer'] = 0
        self.controls['camera_settings']['zoom'] = 20
        
        
    """------------------TASKS--------------------------------------------"""
    """=======update_movement==
        UPDATE CHARACTER MOVEMENT
        ======================="""
    def update_movement(self,task):
        """Task that updates the walking animation on our GravityWalker
        """
        
        # Adjust to match the walkcycle, to minimize sliding
        self.entities['PC'].Actor.setPlayRate(0.5 * \
                            self.entities['PC'].physics['playerWalker'].speed, 
                            'walk') 
        
        #Check if the player is moving.  If so, play walk animation
        if inputState.isSet('forward') or inputState.isSet('reverse') or \
           inputState.isSet('turnLeft') or inputState.isSet('turnRight'):
            if self.controls['isMoving'] is False:
                self.entities['PC'].Actor.loop('walk')
                self.controls['isMoving'] = True
        else:
            if self.controls['isMoving']:
                print 'stopped'
                self.entities['PC'].Actor.stop()
                self.entities['PC'].Actor.loop('idle')
                self.controls['isMoving'] = False
        #Done here
        return Task.cont
    
    """=======update_camera=
        UPDATE CAMERA
        ======================="""
    def update_camera(self,task):
        """Check for camera control input and update accordingly"""
        
        # Get the time self.elapsed since last frame. We need this
        # for framerate-independent movement.
        self.elapsed = globalClock.getDt()
        
        """Rotate Camera left / right"""
        if (self.controls['key_map']['cam_left']!=0):
            """Rotate the camera to the left"""
            #increment the camera timer
            self.controls['camera_settings']['timer'] += .1
            angledegrees = self.controls['camera_settings']['timer'] * 50
            angleradians = angledegrees * (math.pi / 180.0)
            
            base.camera.setPos(self.controls['camera_settings']['zoom']*\
                                math.sin(angleradians),
                               -self.controls['camera_settings']['zoom']*\
                               math.cos(angleradians),
                               3)
            base.camera.setHpr(angledegrees, 0, 0)
            
        if (self.controls['key_map']['cam_right']!=0):
            """Rotate the camera to the right"""
            #increment the camera timer
            self.controls['camera_settings']['timer'] -= .1
            angledegrees = self.controls['camera_settings']['timer'] * 50
            angleradians = angledegrees * (math.pi / 180.0)

            base.camera.setPos(self.controls['camera_settings']['zoom']*\
                                math.sin(angleradians),
                               -self.controls['camera_settings']['zoom']*\
                               math.cos(angleradians),
                               3)
            base.camera.setHpr(angledegrees, 0, 0)
            
        """Zoom camera in / out"""
        if (self.controls['key_map']['cam_up']!=0):          
            #Zoom in
            base.camera.setY(base.camera, +(self.elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] -= 1
                  
        if (self.controls['key_map']['cam_down']!=0): 
            #Zoom out
            base.camera.setY(base.camera, -(self.elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] += 1
            print self.controls['camera_settings']['zoom']
        
        #Update the Sun's position.
        #TODO - tie this in with day/night/time system
        self.lights['sunPos'] += .2
        #Move the sun
        self.lights['dlight'].setHpr(0,self.lights['sunPos'],0)
        #Finish
        #self.entities['PC'].physics['playerWalker'].getCollisionsActive()
        return Task.cont
    
    """=======update_entity_animations
        UPDATE ENTITY ACTOR ANIMATIONS
        ======================="""
    def update_entity_animations(self, task):
        '''Check to see if any entities have moved since the last check
        If entity d(xyz) has changed, play animation'''
        
        #Loop through all entities
        for i in self.entities:
            if i != "PC":
                #Get the entity's current position
                test_pos = self.entities[i].getPos()
                #Turn it into an integer for checking

                test_pos_int = [float("%.2f" % j) for j in test_pos]

                #See if the current position matches the previous position
                if test_pos_int != self.entities[i].prevPos:
                    #Check to see if the entity has been moving
                    if self.entities[i].is_moving is False and \
                        self.entities[i].moving_buffer > 20:
                        #Play the walk animation
                        self.entities[i].Actor.loop('walk')
                        
                        #The entity is moving now
                        self.entities[i].is_moving = True
                        
                        #Reset the moving buffer
                        self.entities[i].moving_buffer = 0
                    #Increment the moving buffer by one to help reduce 
                    #skittering
                    self.entities[i].moving_buffer += 1
                else:
                    #else, the previous and current position is the same
                    if self.entities[i].is_moving:
                        #Check to see if entity is set as moving to ensure we
                        #don't do this loop the idle animation every frame
                        self.entities[i].Actor.stop()
                        self.entities[i].Actor.loop('idle')
                        self.entities[i].is_moving = False
                  
                #Set the entity's previous position
                self.entities[i].prevPos = test_pos_int
                
 
        '''to update NPC's location
            pos = self.entities['NPC_0'].physics['sphereActor'].getPos()
            self.entities['NPC_0'].physics['sphereActor'].setPos(pos[0],pos[1],pos[2])
        '''
        return Task.cont
        
        
    """=======update_mouse_collisions=
        UPDATE COLLISIONS FROM MOUSE
        ======================="""       
    def update_mouse_collisions(self, task):          
        #Check to see if we can access the mouse. We need it to do anything else
        if base.mouseWatcherNode.hasMouse():
            #get the mouse position
            mpos = base.mouseWatcherNode.getMouse()

            #Set the position of the ray based on the mouse position
            self.physics['collisions']['picker_ray'].setFromLens(base.camNode, 
                mpos.getX(), mpos.getY())

            #Do the actual collision pass (Do it only on the squares for
            #efficiency purposes)
            base.cTrav.traverse(EoAUniverse.nodes['entity_root'])        
             
            #assume for simplicity's sake that myHandler is a CollisionHandlerQueue
            if self.physics['collisions']['mouse_cHandler'].getNumEntries() > 0:
                self.physics['collisions']['mouse_cHandler'].sortEntries() #this is so we get the closest object
                pickedObj=self.physics['collisions']['mouse_cHandler'].getEntry(0).getIntoNodePath()
                pickedObj=pickedObj.findNetTag('myObjectTag')
            try:
                if not pickedObj.isEmpty():
                    #handlePickedObject(pickedObj)
                    print pickedObj
            except:
                pass
        return Task.cont
game = Universe()
run()
