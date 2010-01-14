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

"""Set target directory"""
target_dir = os.path.abspath(sys.path[0])
target_dir = Filename.fromOsSpecific(target_dir).getFullpath()


class Universe(DirectObject, EoAUniverse):
    """Universe
    -----------
    Out main class, the Universe"""
   
    def __init__(self):
        """Initialize our world
        
        Our game loop looks a little different than the standard 
            -do logic
            -render
        because Panda3d's tasks are being used.  The basic idea still carries
        over though, and we'll try to follow the same logic by storing states
        in our Universe class then calling a task to render everything (this
        is a TODO)
        
            Set up environment
            Set up lighting
            Set up physics
            Set up actors
            Set up collisions
            
            Run tasks
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
        
        """Set up GUI"""
        self.init_gui()

        """------------TASKS---------------------------------------"""
        self.elapsed = 0.0
        self.prev_time = 0.0
        
        """Set up tasks"""
        #Set up lighting updates
        base.taskMgr.add(self.update_lighting, 'update_lighting')
        
        #Set up movement updates
        base.taskMgr.add(self.update_movement, 'update_movement')
        
        #Set up camera updates
        base.taskMgr.add(self.update_camera, 'update_camera')
        
        #Keep track of entities, update animation if they are moving
        base.taskMgr.add(self.update_entity_animations,
            'update_entity_animations')
        
        #Setup mouse collision test
        base.taskMgr.add(self.update_mouse_collisions, 
            'update_mouse_collisions')
        
        """Set up skydome"""
        #self.init_skydome()
        #Skydome task
        #base.taskMgr.add(self.cameraUpdated, "camupdate")
        """--------------------------------------------------------"""

    """------------------initial setup functions-------------------------------
                                                                       
                         INITIAL SETUP FUNCTIONS                         
                                                                       
        --------------------------------------------------------------------"""
    """=======Controls============================================="""
    def init_controls(self):
        """Set up controls.  Use direct input and keymaps
        
        TODO
            -Allow user to control keys from config settings
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
                                    "mouse3": 0, "scroll_up":0, 
                                    "scroll_down":0}
        
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
        #Call functino to set the player's target
        self.accept("mouse1", self.set_target_on_mouseclick)
        self.accept("mouse1-up", self.controls_set_key, ["mouse1", 0])
        #mouse3 is right click
        self.accept("mouse3", self.controls_set_key, ["mouse3", 1])
        self.accept("mouse3-up", self.controls_set_key, ["mouse3", 0]) 
        #mouse2 is scroll wheel click
        self.accept("mouse2", self.controls_set_key, ["mouse2", 1])
        self.accept("mouse2-up", self.controls_set_key, ["mouse2", 0])
        #mouse scroll
        self.accept('wheel_up', self.controls_set_key,["scroll_up", 1 ]) 
        self.accept('wheel_down', self.controls_set_key, ["scroll_down", 1])        
        self.accept ('escape', sys.exit)  # hit escape to quit!
        
        """--------COMMAND KEYS--------"""
        #autoattack
        self.accept ('z', self.engage_target)  # hit escape to quit!

        
    def controls_set_key(self, key, value):
        """Set up keyboard keys
        
        Create a key_map dictionary to store the key being pressed and the 
        value (which will be either 1 for on or 0 for off)
        """
        
        self.controls['key_map'][key] = value
           
    """=======Lights==============================================="""
    def init_lights(self):
        """init_lights
        Set up light system
        """
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setBloom(blend=(0,0,0,.5), desat=-0.5, 
                        intensity=1.0, size="small")
        if (filterok == False):
            print "Your video card cannot handle this"
            return
        self.glowSize=.2
        
        # Create a simple directional light
        self.lights = {}
        
        #Set up directional light
        self.lights['dlight'] = render.attachNewNode (DirectionalLight\
                                ('DirectionalLight'))
        self.lights['dlight'].setColor(VBase4(1, 1, 1, 1))
        render.setLight(self.lights['dlight'])
        self.lights['dlight'].setPos(50,50,50)
        self.lights['dlight'].lookAt(0,0,0)
        
        #Sun position
        self.lights['sunPos'] = 0
        
        # Create an ambient light
        self.lights['alight'] = AmbientLight('AmbientLight')
        self.lights['alight'].setColor(VBase4(0.1, 0.1, 0.1, 0.1))
        self.lights['alnp'] = render.attachNewNode(self.lights['alight'])
        render.setLight(self.lights['alnp'])
        
        #Create an invisible "sun" node which the dlight will lookAt()
        self.lights['sun_node'] = render.attachNewNode("sun_node")
        self.lights['sun_node'].setPos(10,10,10)
        self.lights['sun_node'].setScale(2)
        
        #Create a sun model that will be a visual representation of where the
        #   sun is.  Will be, essentially, in the opposite position of the 
        #   fake sun node
        self.lights['sun_model'] = loader.loadModel(target_dir+'/models/sphere.egg')
        self.lights['sun_model'].reparentTo(render)
        self.lights['sun_model'].setPos(10,10,10)
        self.lights['sun_model'].setScale(2)
        
        self.lights['sky_box'] = loader.loadModel(target_dir+'/models/skybox.egg')
        self.lights['sky_box'].reparentTo(render)
        self.lights['sky_box'].setScale(5)
        sky_tex = loader.loadTexture(\
                target_dir+'/models/textures/clouds_bw.png')
        sky_tex.setWrapU(Texture.WMRepeat)
        sky_tex.setWrapV(Texture.WMRepeat)
        self.lights['sky_box'].setTexture(sky_tex,1)
        
    """=======Actors==============================================="""
    def init_actors(self):
        """init_actors
        Setup actors"""
        
        #Setup the PC entity
        self.entities['PC'] = EoAEntity(gravity_walker=True,modelName="boxman", 
                                    name='PC', startPos=(0,0,5), 
                                    max_health=521, max_power=82,
                                    stats={'agi':10, 'dex':19, 'int':19, 
                                            'sta':15, 'str':14, 'wis':18})
               
        """for i in range(5):
            self.entities['NPC_'+str(i)] = EoAEntity(modelName="boxman", 
                        max_health=100,
                        name='NPC_'+str(i),startPos=(random()*i+i,
                                                    random()*i+i,80))
        """
    """=======Camera==============================================="""
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
    
    """=======Skydome=============================================="""
    def init_skydome(self):
        #SKYBOX
        self.skybox = loader.loadModel(target_dir+'/models/dome2')
        self.skybox.reparentTo(render)
        self.skybox.setScale(4000,4000,1000)
        #self.skybox.setLightOff()
        texturefile = target_dir + "/models/textures/clouds_bw.png"
        texture = loader.loadTexture(texturefile)
        self.textureStage0 = TextureStage("stage0")
        self.textureStage0.setMode(TextureStage.MReplace)
        self.skybox.setTexture(self.textureStage0,texture,.2)
        self.rate = Vec4(0.004, 0.002, 0.008, 0.010)
        self.textureScale = Vec4(1,1,1,1)
        self.skycolor = Vec4(.1, .1, .1, 0)
        self.skybox.setShader( loader.loadShader(target_dir+\
            '/shaders/skydome2.sha' ) )
        self.skybox.setShaderInput("sky", self.skycolor)
        self.skybox.setShaderInput("clouds", self.rate)
        self.skybox.setShaderInput("ts", self.textureScale)

    """-----------------tasks--------------------------------------------------
                                                                       
                        TASKS                        
                                                                       
        --------------------------------------------------------------------"""
    """=======Update character movement============================"""
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
    
    """======Update camera========================================="""
    def update_camera(self,task):
        """Check for camera control input and update accordingly"""
        
        # Get the time self.elapsed since last frame. We need this
        # for framerate-independent movement.
        self.elapsed = globalClock.getDt()
        
        """Rotate Camera left / right"""
        if (self.controls['key_map']['cam_left']!=0):
            """Rotate the camera to the left"""
            #increment the camera timer, determines speed of camera rotation
            self.controls['camera_settings']['timer'] += .1
            angledegrees = self.controls['camera_settings']['timer'] * 50
            angleradians = angledegrees * (math.pi / 180.0)
            
            #Set the X, Y as the zoom value * sine or cosine (respectively) of
            #   angle radians, which is determined by rotating the camera left
            #   or right around the character.  The zoom variable determines 
            #   in essence, the zoom level which is calcuated simply as
            #   self.elapsed * 20.  Notice this is also the value we use to
            #   setY when we zoom in or out - no coincidence, these numbers
            #   are the same because we want to know the location of the 
            #   camera when we pan around the character (this location is
            #   multiplied by sin or cos of angleradians
            base.camera.setPos(self.controls['camera_settings']['zoom']*\
                                math.sin(angleradians),
                               -self.controls['camera_settings']['zoom']*\
                               math.cos(angleradians),
                               base.camera.getZ())
                               
            #Set the beading / yaw (h) of the camera to point at the character
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
                               base.camera.getZ())
            base.camera.setHpr(angledegrees, 0, 0)
            
        """Zoom camera in / out"""
        #ZOOM IN
        if (self.controls['key_map']['cam_up']!=0):   
            #Zoom in
            base.camera.setY(base.camera, +(self.elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] -= self.elapsed*20
        
        #Zoom in on mouse scroll forward
        if (self.controls['key_map']['scroll_up']!=0):          
            #Zoom in
            base.camera.setY(base.camera, +(self.elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] -= 1
            #Reset the scroll state to off
            self.controls['key_map']['scroll_up'] = 0
       
        #ZOOM OUT
        if (self.controls['key_map']['cam_down']!=0): 
            #Zoom out
            base.camera.setY(base.camera, -(self.elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] += self.elapsed*20
            
        #Zoom in on mouse scroll forward   
        if (self.controls['key_map']['scroll_down']!=0):          
            #Zoom in
            base.camera.setY(base.camera, -(self.elapsed*20))
            #Store the camera position
            self.controls['camera_settings']['zoom'] -= 1
            #Reset the scroll state to off
            self.controls['key_map']['scroll_down'] = 0
            
        #self.entities['PC'].physics['playerWalker'].getCollisionsActive()
        return Task.cont
    
    """======Update lighting========================================="""
    def update_lighting(self, task):
        #Update the Sun's position.
        #TODO - tie this in with day/night/time system

        #Move the sun
        angleDegrees = task.time * 100.0
        angleRadians = angleDegrees * (math.pi / 180.0)
        self.lights['sun_node'].setPos(75*math.sin(angleRadians), 
            0,-75.0*math.cos(angleRadians))
        
        #Set the sun model's position based on the sun node.  Will be reversed
        #   in the X direction
        self.lights['sun_model'].setPos(-self.lights['sun_node'].getX(),
        3, -self.lights['sun_node'].getZ())
        
        #self.lights['dlight'].setHpr(0,angleDegrees,0)
        self.lights['dlight'].lookAt(self.lights['sun_node'])
        
        #self.lights['sky_box'].setHpr(0,angleDegrees,0)
        
        #Set the skybox's position to the camera's position so the camera
        #   never touches the skybox, makes the skybox appear to never move
        self.lights['sky_box'].setPos(base.camera.getPos())
        return Task.cont
    
    """=======update_entity_animations============================="""
    def update_entity_animations(self, task):
        """Check to see if any entities have moved since the last check
        If entity d(xyz) has changed, play animation"""
        
        #Loop through all entities and animate them
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
                
 
        """to update NPC's location
            pos = self.entities['NPC_0'].getPos()
            self.entities['NPC_0'].setPos(x,y,z)
        """
        return Task.cont
        
        
    """=======update_mouse_collisions=============================="""       
    def update_mouse_collisions(self, task):    
        """Handle muse collisions for hover and click"""
        
        #TODO - optimize? Does this provide an advatge?
        #Task.time returns a float with many digits, so doing all these checks
        #per iteration is a little time consuming. Let's compare only the first
        #digit of task.time to see if we should do the mouse collisions checks
        #or not.  Since the timing does not have to be 100% perfect as we're
        #checking for mouse interactions, we can afford not to be as exact
        #as possible.  Need to check if following test saves any FPS
         
        #normal test
        #if self.prev_time != task.time:
        
        #optimized test
        #if float("%.1f" % self.prev_time) != float("%.1f" % task.time):
        
        
        #Check to see if we can access the mouse
        if base.mouseWatcherNode.hasMouse():
            #get the mouse position
            mpos = base.mouseWatcherNode.getMouse()

            #Set the position of the ray based on the mouse position
            self.physics['collisions']['mouse']['picker_ray'].setFromLens(\
                base.camNode, mpos.getX(), mpos.getY())

            #Do the actual collision pass (Do it only on the squares for
            #efficiency purposes)
            base.cTrav.traverse(EoAUniverse.nodes['entity_root'])        
            
            #Get number of entries in the collision handler
            if self.physics['collisions']['mouse']['cHandler'].\
                getNumEntries() > 0:
                #Get the closest object
                self.physics['collisions']['mouse']['cHandler'].sortEntries()
                #Store the picked object
                self.physics['collisions']['mouse']['current_node'] = self.\
                    physics['collisions']['mouse']['cHandler'].\
                    getEntry(0).getIntoNodePath()
                self.physics['collisions']['mouse']['current_node'] = self.\
                    physics['collisions']['mouse']['current_node'].\
                    findNetTag('mouse_obj_tag')
                
                try:
                    if not self.physics['collisions']['mouse']\
                    ['current_node'].isEmpty():
                        #Get the entity from the python tag
                        """Check for mouse hopping from object to object,
                        mouse might hover over NPC_1 to NPC_2.  If we don't
                        check for this, a node may stay highlighted if the 
                        mouse collides from NPC to NPC"""
                        
                        #Check if the current picked object is equal to the 
                        #previous picked object (and that it isn't none)
                        if self.physics['collisions']['mouse']['prev_node'] !=\
                        self.physics['collisions']['mouse']['current_node'] \
                        and self.physics['collisions']['mouse']\
                        ['prev_node'] is not None:
                            #Turn off the highlight light
                            self.physics['collisions']['mouse']['prev_node'].\
                                setLightOff()
                            
                            #Turn back on the default lights
                            self.physics['collisions']['mouse']['prev_node'].\
                                setLight(self.lights['alnp'])
                            self.physics['collisions']['mouse']['prev_node'].\
                                setLight(self.lights['dlight'])
                            #We don't set the previously picked node object 
                            #here because we don't want to set the previous
                            #node to the current node if the previous node
                            #is equal to none
                            
                        """If the hovered over node is not the curret node,
                        set light"""
                        #Add an effect
                        #Create an ambient light so the name node will be 
                        #one uniform light
                        ambient = AmbientLight('ambient')
                        ambient.setColor(Vec4(.5,.7,.7,.1))
                        ambientNP = self.physics['collisions']['mouse']\
                            ['current_node'].attachNewNode(\
                            ambient.upcastToPandaNode())
                         
                        # If we did not call setLightOff() first, the green 
                        #light would add to the total set of lights on this 
                        #object.  Since we do call setLightOff(), we are 
                        #turning off all the other lights on this object first,
                        #and then turning on only the green light.
                        self.physics['collisions']['mouse']['current_node'].\
                            setLightOff()
                        self.physics['collisions']['mouse']['current_node'].\
                            setLight(ambientNP)
                        
                        #We set the highlighting for the moused over node, 
                        #now set the previous node to the current selected node
                        if self.physics['collisions']['mouse']['prev_node'] !=\
                        self.physics['collisions']['mouse']['current_node']:
                            self.physics['collisions']['mouse']['prev_node'] =\
                            self.physics['collisions']['mouse']['current_node']
                        
                except:
                    print "Error on mouse over node " + str(self.physics\
                        ['collisions']['mouse']['current_node'])
            else:
                #The mouse isn't over anything, check to see if the previous
                #node is set
                if self.physics['collisions']['mouse']['prev_node'] \
                is not None:
                    if self.entities['PC'].target != \
                    self.physics['collisions']['mouse']['prev_node'].\
                        getPythonTag('entity'):
                    #Turn off the highlight light
                        self.physics['collisions']['mouse']['prev_node'].\
                        setLightOff()
                    
                        #Turn back on the default lights
                        self.physics['collisions']['mouse']['prev_node'].\
                            setLight(self.lights['alnp'])
                        self.physics['collisions']['mouse']['prev_node'].\
                            setLight(self.lights['dlight'])
                        
                    #Set the previous node to none
                    self.physics['collisions']['mouse']['prev_node'] = None
                    
                self.physics['collisions']['mouse']['current_node'] = None
        #self.prev_time = task.time
        return Task.cont
    
    """=======Update skybox========================================"""
    def cameraUpdated(self, task):
        #self.lights['sunPos']
        self.skycolor = Vec4( (self.lights['sunPos'] % 360.0) / 360,
                                (self.lights['sunPos'] % 360.0) / 360,
                                (self.lights['sunPos'] % 360.0) / 360
                                ,0 )
        self.skybox.setShaderInput("sky", self.skycolor)
        render.setShaderInput('time', task.time)
        return Task.cont
            
    """-----------------EoA Universe Functions---------------------------------
                                                                       
                        EoA Universe Functions                       
                                                                       
        --------------------------------------------------------------------"""   
    """=======Engage target======================================""" 
    def engage_target(self, force_state=None):
        """Engage target.  Will turn on autoattack (if configured)"""  
        
        """Update Target Box GUI Element"""
        #if there is a target, engage it
        if self.entities['PC'].target is not None:
            #Take some fake damage
            self.entities['PC'].target.take_damage(dmg_amt=5)
            
            #Already engaged, DISENGAGE
            if self.entities['PC'].is_engaged or force_state == 0:
                #They're already engaged, so disengage
                self.GUI.update_gui_element_target_box_engage(engaged=0)
                #Disengage
                self.entities['PC'].is_engaged = False
                #If state is forced, exit function
                print "DISENGAGE"
                if force_state == 0:
                    return
                    
            #Not already engaged, ENGAGE
            elif not self.entities['PC'].is_engaged or force_state == 1:
                #They aren't engaged, so engage
                self.GUI.update_gui_element_target_box_engage(engaged=1)
                #Engage
                self.entities['PC'].is_engaged = True
                #If sate is forced, exit function
                print "ENGAGE"
                if force_state == 1:
                    return
        
    """=======Set PC's target======================================"""
    def set_target_on_mouseclick(self):
        """Set the player's target to an entity based on mouse click"""
        
        #if self.physics['collisions']['mouse']['prev_node'] is not None:
        #    print self.physics['collisions']['mouse']['prev_node']
        if self.physics['collisions']['mouse']['current_node'] is not None:
            """If something was clicked"""
            
            picked_entity = self.physics['collisions']['mouse']\
                ['current_node'].getPythonTag('entity')
            #print 'clicked' + str(picked_entity.name)
            self.entities['PC'].set_target(target=picked_entity)
            
            if self.physics['collisions']['mouse']['prev_target'] is not None \
            and self.physics['collisions']['mouse']['prev_target'] != \
            self.physics['collisions']['mouse']['current_node']:
                self.physics['collisions']['mouse']['prev_target'].\
                setLightOff()
            
                #Turn back on the default lights
                self.physics['collisions']['mouse']['prev_target'].\
                    setLight(self.lights['alnp'])
                self.physics['collisions']['mouse']['prev_target'].\
                    setLight(self.lights['dlight'])

            #Set previous target to the current node (set the last clicked on
            #node equal to the node the mouse is over)
            self.physics['collisions']['mouse']['prev_target'] = \
                self.physics['collisions']['mouse']['current_node']
            
        else:
            """No entities are under the click, so clear the target and any
            lighting on the previously selected node"""
            
            try:
                #Turn off the previous selected node's lights
                self.physics['collisions']['mouse']['prev_target'].\
                    setLightOff()
                
                #Turn back on the default lights
                self.physics['collisions']['mouse']['prev_target'].\
                    setLight(self.lights['alnp'])
                self.physics['collisions']['mouse']['prev_target'].\
                    setLight(self.lights['dlight'])                
            except:
                print "Could not turn off node's lighting"
                
            #Clear the PC's current target
            self.entities['PC'].set_target(target=None)
            
            #Clear the target text
            """TODO create a set_target_on_mouseclick method that updates
            targetbox"""
            self.GUI.target_box['target_text'].setText("")
"""------------------------------------------------------------------------"""

"""Instantiate the universe and call the built in Panda3d run() function""" 
game = Universe()
run()
