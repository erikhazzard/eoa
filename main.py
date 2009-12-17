"""
End of Ages

"""

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

import sys, math, os
from random import random


class Universe(DirectObject):
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
        """Set up tasks"""
        #Set up movement update
        base.taskMgr.add(self.update_movement, 'update_movement')
        
        #Set up camera update
        base.taskMgr.add(self.update_camera, 'update_camera')
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
        
    """=======Environment======
        ENVIRONMENT SETUP
        ======================="""
    def init_environment(self):
        # Load an environment we can run around in
        self.environment = loader.loadModel('models/world')
        self.environment.reparentTo(render)
    
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
        self.lights['dlight'] = render.attachNewNode (DirectionalLight\
                                ('DirectionalLight'))
        self.lights['dlight'].setColor(VBase4(1, 1, 1, 1))
        render.setLight(self.lights['dlight'])
        self.lights['dlight'].setPos(1, 1, 1)
        self.lights['dlight'].lookAt(0, 0, 0)
        self.lights['sunPos'] = 0
        # Create an ambient light
        self.lights['alight'] = AmbientLight('AmbientLight')
        self.lights['alight'].setColor(VBase4(0.5, 0.5, 0.5, 0.2))
        self.lights['alnp'] = render.attachNewNode(self.lights['alight'])
        render.setLight(self.lights['alnp'])
    
    """=======Physics==========
        PHYSICS SETUP
        ======================="""
    def init_physics(self):
        """init_physics
        Set up the physics"""

        # Turn on particles, required to use Panda physics
        base.enableParticles()
        
        """Assign some masks
       Purpose: We'll use masks to check for collisions for different objects
       
       We're going to create a self.physics dictionary that will store things
       related to the physics system, including bit masks, gravity settings,
       etc.
       """

        #Create a dictionary to store various physics settings
        self.physics = {'collisions': \
                            {'bit_masks': \
                                {'bit_values':{}} \
                            }, \
                        'gravity':{} \
                        }
        
        """Set up some bit masks"""        
        #bit_values is a dictionatary containing bit values for 
        #various bit masks
        self.physics['collisions']['bit_masks']['bit_values']['floor'] = 1
        self.physics['collisions']['bit_masks']['bit_values']['wall'] = 2
        self.physics['collisions']['bit_masks']['bit_values']['sphere'] = 3
        self.physics['collisions']['bit_masks']['bit_values']['player'] = 4

        #Set up the floor mask
        self.physics['collisions']['bit_masks']['floor'] = BitMask32()
        self.physics['collisions']['bit_masks']['floor'].setBit(self.physics\
                            ['collisions']['bit_masks']['bit_values']['floor'])

        #Set up the wall mask
        self.physics['collisions']['bit_masks']['wall'] = BitMask32()
        self.physics['collisions']['bit_masks']['wall'].setBit(self.physics\
                            ['collisions']['bit_masks']['bit_values']['wall'])
        self.physics['collisions']['bit_masks']['wall'].setBit(self.physics\
                            ['collisions']['bit_masks']['bit_values']['floor'])
        
        """Set up Gravity""" 
        self.physics['gravity']['gravity_FN'] = ForceNode('globalGravityForce')
        self.physics['gravity']['gravity_NP'] = render.attachNewNode(
                            self.physics['gravity']['gravity_FN'])
        #Set the force of gravity.  We'll use Earth's
        self.physics['gravity']['g_force'] = LinearVectorForce(0, 0, -9.81)
        
        #Set constant acceleration
        self.physics['gravity']['g_force'].setMassDependent(False)
        self.physics['gravity']['gravity_FN'].addForce(self.physics['gravity']\
                            ['g_force'])
        
        # add it to the built-in physics manager
        base.physicsMgr.addLinearForce(self.physics['gravity']['g_force'])
        
    """=======collisions========
        COLLISON SETUP
        ======================="""
    def init_collisions(self):
        """Set up collisions"""
        # Create a basic collision traverser
        self.physics['collisions']['cTrav'] = CollisionTraverser()
        
        """Set collisions for objects"""
        # Turn on collisions for all the objects named Ground and Rock
        # Everything else we leave invisible to collisions
        for ground in self.environment.findAllMatches ('**/Ground*'):
            ground.setCollideMask(BitMask32().bit(self.physics['collisions']\
                            ['bit_masks']['floor']))
        
        for rock in self.environment.findAllMatches ('**/Rock*'):
            rock.setCollideMask(self.physics['collisions']['bit_masks']\
                            ['wall'])
    
    """=======Actors===========
        ACTOR SETUP
        ======================="""
    def init_actors(self):
        """init_actors
        Setup actors"""
        #Create a dictionary to hold all our actors
        self.entities = {'PC':{}} 
        
        self.entities['PC']['Actor'] = Actor()
        self.entities['PC']['Actor'].loadModel('models/boxman')
        self.entities['PC']['Actor'].loadAnims({'idle' : 'models/boxman-idle'})
        self.entities['PC']['Actor'].loadAnims({'walk' : 'models/boxman-walk'})

        # start our walking animation
        self.entities['PC']['Actor'].loop('walk')

        self.entities['PC']['Actor'].setPos(0, 0, 5)
        self.entities['PC']['Actor'].reparentTo(render)
        
        # Create a GravityWalker and let's set some defaults
        #Create an empty dictionary to store physics for actors
        self.physics['actor_physics'] = {}
        self.physics['actor_physics']['playerWalker'] = GravityWalker()
        
        self.physics['actor_physics']['playerWalker'].setAvatar(\
                        self.entities['PC']['Actor'])
        self.physics['actor_physics']['playerWalker'].setWalkSpeed(forward=5,\
                        jump=15, reverse=4, rotate=90)
                        
        self.physics['actor_physics']['playerWalker'].setWallBitMask( \
                        BitMask32().bit( \
                        self.physics['collisions']['bit_masks']['bit_values']
                        ['wall']))
                        
        self.physics['actor_physics']['playerWalker'].setFloorBitMask(\
                        BitMask32().bit(self.physics['collisions']\
                        ['bit_masks']['bit_values']['floor']))
                        
        self.physics['actor_physics']['playerWalker'].initializeCollisions(
                        self.physics['collisions']['cTrav'], 
                        self.entities['PC']['Actor'], avatarRadius=0.5,
                        floorOffset=0.1, reach=0.5)
                        
        self.physics['actor_physics']['playerWalker'].enableAvatarControls()
        self.physics['actor_physics']['playerWalker'].placeOnFloor()

        # By setting the wall sphere to a player bitmask, we can have spheres 
        #we created above react against the player, since they are using a
        #CollisionPusherHandler
        self.physics['actor_physics']['playerWalker'].cWallSphereNodePath.\
                    setCollideMask(BitMask32().bit(self.physics['collisions']\
                    ['bit_masks']['bit_values']['player']))  
    
        """Name above head"""
        self.chatTextParent=aspect2d.attachNewNode('chat text dummy')
        self.chatDL = DirectLabel(parent=self.chatTextParent,
                    frameColor=(0,0,0,0),
                    text_fg=(1,1,1,1), 
                    #text_shadow=(0,0,0,1),
                    text_align=TextNode.ACenter,
                    text='Your Name', # the name
                    text_pos=(0,-1.2),
                    )
        self.chatTextParent.setZ(-5)
        self.chatTextOutputParent = self.entities['PC']['Actor'].attachNewNode(
                    'chat text dummy')
        self.chatTextOutput = self.chatDL.instanceUnderNode(
                    self.chatTextOutputParent, 'chat text')
        self.chatTextOutput.setScale(.5)
        self.chatTextOutput.setZ(self.entities['PC']['Actor'].getTightBounds()\
                    [1][2]-2.2) # put it above smiley
        self.chatTextOutputParent.setBillboardPointEye()
        self.chatTextPos = self.entities['PC']['Actor'].exposeJoint(None, 
                    'modelRoot', 'Head')
        self.chatTextOutputParent.setPos(self.chatTextPos.getPos()[0],
                    self.chatTextPos.getPos()[1],
                    self.chatTextPos.getPos()[2] - 2)
        
    """=======Camera===========
        CAMERA SETUP
        ======================="""
    def init_camera(self):
        """init_camera
        Set up the camera.  Allow for camera autofollow, freemove, etc"""
        
        base.disableMouse()
        base.camera.reparentTo(self.entities['PC']['Actor'])
        base.camera.setPos(0, -15, 25)
        base.camera.lookAt(self.entities['PC']['Actor'])
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
        self.entities['PC']['Actor'].setPlayRate(0.5 * \
                            self.physics['actor_physics']\
                            ['playerWalker'].speed, 'walk') 
        
        #Check if the player is moving.  If so, play walk animation
        if inputState.isSet('forward') or inputState.isSet('reverse') or \
           inputState.isSet('turnLeft') or inputState.isSet('turnRight'):
            if self.controls['isMoving'] is False:
                print 'moving'
                #self.entities['PC']['Actor'].stop()
                self.entities['PC']['Actor'].loop('walk')
                self.controls['isMoving'] = True
        else:
            if self.controls['isMoving']:
                print 'stopped'
                self.entities['PC']['Actor'].stop()
                self.entities['PC']['Actor'].loop('idle')
                self.controls['isMoving'] = False
        
        #Done here
        return Task.cont
    
    """=======update_camera=
        UPDATE CAMERA
        ======================="""
    def update_camera(self,task):
        """Check for camera control input and update accordingly"""
        
        # Get the time elapsed since last frame. We need this
        # for framerate-independent movement.
        elapsed = globalClock.getDt()
        
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
            base.camera.setY(base.camera, +(elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] -= 1
                  
        if (self.controls['key_map']['cam_down']!=0): 
            #Zoom out
            base.camera.setY(base.camera, -(elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] += 1
            print self.controls['camera_settings']['zoom']
            
        self.lights['sunPos'] += 1
        #Move the sun
        self.lights['dlight'].setHpr(0,self.lights['sunPos'],0)
        #Finish
        return Task.cont
    
game = Universe()
run()
