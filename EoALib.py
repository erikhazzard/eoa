"""EoA
End of Ages

This file contains the majority EoA's library classes and functions

"""
"""System Imports"""
import sys, math, os
from random import random

"""Panda Module imports"""
from pandac.PandaModules import *

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

"""Set target directory"""
target_dir = os.path.abspath(sys.path[0])
target_dir = Filename.fromOsSpecific(target_dir).getFullpath()


DEBUG = False
"""---------------------------------------------------------------------------
    Universe Class
    -----------------------------------------------------------------------"""    
class EoAUniverse(DirectObject):
    #Set up a dictionary for physics related objects
    physics = {'collisions': \
                            {'bit_masks': \
                                {'bit_values':{}} \
                            }, \
                'gravity':{} \
                }
    
    #Create an empty attribute for the environment. Will be overriden when
    #   init_environment is called
    environment = ''
    
    #Create a dictionary object to store all the entities
    entities = {}
    
    #Dictionary of nodes - to be used later?
    nodes = {}

    #Create an empty GUI placeholder object.  When init_gui() is called, this
    #   will hold the GUI object which will be accessable by other classes
    GUI = ''
    
    """=======Environment======
        ENVIRONMENT SETUP
        ======================="""
    def init_environment(self):
        # Load an environment we can run around in
        EoAUniverse.environment = loader.loadModel('models/world')
        EoAUniverse.environment.reparentTo(render)
       
        """Set up some nodes for organization / performance"""
        #Entity root will hold all our entities
        #Useful so we can use the mouse ray to only check for collisions with
        #entities
        EoAUniverse.nodes['entity_root'] = render.attachNewNode('entityRoot')
        EoAUniverse.nodes['entity_root'].setPos(0,0,0)
        
        #Allow for shaders
        render.setShaderAuto()
    
    """=======GUI======
        GUI SETUP
    ======================="""
    def init_gui(self):
        """Set the GUI attribute equal to a new EoAGUI object.
        
        There probably will ever only be one call made to EoAGUI() and it is
        here."""
        EoAUniverse.GUI = EoAGUI()
    
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
       
       We're going to create a EoAUniverse.physics dictionary that will store
       things related to the physics system, including bit masks, 
       gravity settings, etc.
       """
        
        """Set up some bit masks"""        
        #bit_values is a dictionatary containing bit values for 
        #various bit masks
        EoAUniverse.physics['collisions']['bit_masks']['bit_values']['floor'] = 1
        EoAUniverse.physics['collisions']['bit_masks']['bit_values']['wall'] = 2
        EoAUniverse.physics['collisions']['bit_masks']['bit_values']['npc'] = 3
        EoAUniverse.physics['collisions']['bit_masks']['bit_values']['player'] = 4

        #Set up the floor mask
        EoAUniverse.physics['collisions']['bit_masks']['floor'] = BitMask32()
        EoAUniverse.physics['collisions']['bit_masks']['floor'].setBit(EoAUniverse.physics\
                            ['collisions']['bit_masks']['bit_values']['floor'])

        #Set up the wall mask
        EoAUniverse.physics['collisions']['bit_masks']['wall'] = BitMask32()
        EoAUniverse.physics['collisions']['bit_masks']['wall'].setBit(EoAUniverse.physics\
                            ['collisions']['bit_masks']['bit_values']['wall'])
        EoAUniverse.physics['collisions']['bit_masks']['wall'].setBit(EoAUniverse.physics\
                            ['collisions']['bit_masks']['bit_values']['floor'])
        
        """Set up Gravity""" 
        EoAUniverse.physics['gravity']['gravity_FN'] = ForceNode('globalGravityForce')
        EoAUniverse.physics['gravity']['gravity_NP'] = render.attachNewNode(
                            EoAUniverse.physics['gravity']['gravity_FN'])
        #Set the force of gravity.  We'll use Earth's
        EoAUniverse.physics['gravity']['g_force'] = LinearVectorForce(0, 0, -9.81)
        
        #Set constant acceleration
        EoAUniverse.physics['gravity']['g_force'].setMassDependent(False)
        EoAUniverse.physics['gravity']['gravity_FN'].addForce(EoAUniverse.physics['gravity']\
                            ['g_force'])
        
        # add it to the built-in physics manager
        base.physicsMgr.addLinearForce(EoAUniverse.physics['gravity']['g_force'])
        
    """=======collisions========
        COLLISON SETUP
        ======================="""
    def init_collisions(self):
        """Set up collisions"""
        # Create a basic collision traverser
        base.cTrav = CollisionTraverser()
        
        """Set collisions for objects"""
        # Turn on collisions for all the objects named Ground and Rock
        # Everything else we leave invisible to collisions
        for ground in EoAUniverse.environment.findAllMatches('**/Ground*'):
            ground.setCollideMask(BitMask32().bit(EoAUniverse.physics\
                ['collisions']['bit_masks']['bit_values']['floor']))
        
        for rock in EoAUniverse.environment.findAllMatches('**/Rock*'):
            rock.setCollideMask(EoAUniverse.physics['collisions']['bit_masks']\
                ['bit_values']['wall'])
        
        """Init Mouse collision controler"""
        #setup our collision handler queue
        self.physics['collisions']['mouse'] = {}
        self.physics['collisions']['mouse']['prev_node'] = None
        self.physics['collisions']['mouse']['current_node'] = None
        self.physics['collisions']['mouse']['prev_target'] = None
        
        self.physics['collisions']['mouse']['cHandler'] = \
                CollisionHandlerQueue()

        self.physics['collisions']['mouse']['picker_node'] = \
                CollisionNode('mouseRay')
        
        self.physics['collisions']['mouse']['picker_node_path'] = \
                base.camera.attachNewNode(self.physics['collisions']\
                ['mouse']['picker_node'])
        
        self.physics['collisions']['mouse']['picker_node'].setFromCollideMask(\
                GeomNode.getDefaultCollideMask())
        
        self.physics['collisions']['mouse']['picker_ray']=CollisionRay()
        
        self.physics['collisions']['mouse']['picker_node'].addSolid(\
                self.physics['collisions']['mouse']['picker_ray'])
        
        base.cTrav.addCollider(self.physics['collisions']['mouse']\
                ['picker_node_path'],
                self.physics['collisions']['mouse']['cHandler'])
                
        """Show collisions if debug"""
        if DEBUG:
            base.cTrav.showCollisions(render)

"""---------------------------------------------------------------------
    Entity Functions
    --------------------------------------------------------------------"""  
class EoAEntity(EoAUniverse):
    """Entity
    Our main Entity class
    """
    
    def __init__(self, name="Unnamed", modelName="default", scale=1, 
                max_health=1, max_power=1, health=None, power=None,
                ac=1, stats={}, elementals={},
                addToWorld=True, startPos=False, modelStates=False,
                gravity_walker=False):
        """init
        Set up our Actor's attributes and function call, crete the actor
        Entity extends Panda3d's Actor"""
        
        """Set up the Actor"""
        #Call the panda3d actor init
        modelLocation = target_dir + "/models/%s" %(modelName)
        try:
            if not modelStates:
                modelStates = {"idle":target_dir + "/models/%s-idle" %(modelName),
                               "walk":target_dir + "/models/%s-walk" %(modelName)}
            else:
                modelStates = modelStates
        except:
            pass

        #Extend the actor
        self.Actor = Actor()
        self.Actor.loadModel(modelLocation)
        self.Actor.loadAnims(modelStates)
        self.Actor.loop('idle')
        
        """Set Up Entity Stats"""
        #stats
        self.max_health = max_health
        self.health = max_health
        #If the entity shouldn't be create with full health
        if health is not None:
            self.health = health
        
        self.max_power = max_power
        self.power = max_power
        #If the entity shouldn't be created with full power
        if power is not None:
            self.power = power
        #Armor class
        self.ac = ac
        
        self.stats = stats
        #If no stats are passed in, set all to 0
        if self.stats == {}:
            self.stats = {'agi':0, 'dex':0, 'int':0, 'sta':0, 'str':0, 'wis':0}

        self.elementals = elementals
        #If no elemental stats are passed in, set to 0
        if self.elementals == {}:
            self.elementals = {'dark':0, 'earth':0, 'fire':0, 'light':0,
                                'water':0, 'wind':0}
        
        """Set up entity body / items"""
        #Default body parts.  Different creatures have different parts
        self.body = {'head':None, 'chest': None, 'shoulders':None, 'back':None,
                            'arms':None, 'wrist':None, 'hands':None,
                            'fingers':None,
                            'waist':None, 'legs':None, 'feet':None,
                            'primary': None, 'secondary': None, 'ranged':None}
        
        #Our actor's inventory.
        self.inventory = []
        
        #Set the amount of money
        self.inventory_gold = 0
        
        #Equipped items. Body parts link to items in inventory
        self.equipped_items = {}
        
        #Set the name
        self.name = name
        
        """Add character to world"""
        #Add to the world if set to true(by default it is)
        #Some actors may need to be added to the game but not 
        #rendered
        if addToWorld:
            self.Actor.reparentTo(render)
            self.Actor.setScale(scale)
            
            #If startPos is not passed in, set a default position
            if not startPos:
                self.Actor.setPos(200,200,200)
            else:
                self.Actor.setPos(startPos)
               
        """Set up Entity Physics"""
        self.physics = {}
        
        """Determine if the entity is using the GravityWalker class"""
        self.physics['is_gravity_walker'] = gravity_walker
        
        #Gravity walker is for the PC controllable character (generally)
        if not self.physics['is_gravity_walker']:
            self.init_entity_physics(startPos=startPos)
        else:
            self.init_entity_physics_gravity_walker ()
    
        """Store the entity's last known coordinates
        We use this to check if the entity has moved for animations"""
        self.prevPos = tuple([int(i) for i in self.getPos()])
        
        """By default, the entity is not moving"""
        self.is_moving = False
        self.moving_buffer = 0
        
        """Show the name node"""
        self.name_gui = {}
        if not self.physics['is_gravity_walker']:
            self.init_name_node(self.name)
        else:
            self.init_name_node(self.name,nodePos='-')
            
        """Set the entity's target"""
        self.target = None
        
        #Determine if the entity is engaged with another target
        self.is_engaged = False
        
    """---------------------------------------------------------------------
        Init Functions
        --------------------------------------------------------------------"""
    """--------------------------------------
        Name Node Functions
        -------------------------------------"""
    def init_name_node(self, name, nodePos='', node_color=(1,1,1,1)):
        """Set up the name node that appears above an entity"""
        #Create the node in 2d space
        self.name_gui['name_node_2d']=aspect2d.attachNewNode(\
                            '2d_name_node_'+name)
        
        #Create the direct label
        self.name_gui['label'] = DirectLabel(parent=\
                            self.name_gui['name_node_2d'],
                            frameColor= (0,0,0,0),
                            text_fg= (1,1,1,1), 
                            #text_shadow= (1,1,1,1),
                            text_align=TextNode.ACenter,
                            text=name,
                            text_pos= (0,-1.2),
                            )
        #Set the z
        self.name_gui['name_node_2d'].setZ(-5)
        
        self.name_gui['node_parent'] = self.Actor.attachNewNode(\
                            '2d_name_node_'+name)
        
        self.name_gui['node'] = self.name_gui['label'].instanceUnderNode(\
                            self.name_gui['node_parent'],
                            '2d_name_node_'+name)
                                
        self.name_gui['node'].setScale(.5)
        
        self.name_gui['node'].setZ(self.Actor.getTightBounds()[1][2]) 
                                
        self.name_gui['node_parent'].setBillboardPointEye()
        
        """Set light for node"""
        #Turn off the shader for the name node.
        #We do this because the shader automatically turns lights 
        #into per pixel lighting, and we don't want that for our name labels
        self.name_gui['node_parent'].setShaderOff()
        
        #Create an ambient light so the name node will be one uniform light
        self.name_gui['lighting'] = {}
        self.name_gui['lighting']['ambient'] = AmbientLight('ambient')
        #Set the color...eventually, make this dynamic? Or have set colors
        #for certain NPC types / skills?
        self.name_gui['lighting']['ambient'].setColor(Vec4(node_color))
        
        #Create a node path...save it in case the user wants to disable names
        self.name_gui['lighting']['ambient_node'] = self.name_gui\
            ['node_parent'].attachNewNode(\
            self.name_gui['lighting']['ambient'].upcastToPandaNode())
         
        # If we did not call setLightOff() first, the green light would add to
        # the total set of lights on this object.  Since we do call
        # setLightOff(), we are turning off all the other lights on this
        # object first, and then turning on only the green light.
        self.name_gui['node_parent'].setLightOff()
        self.name_gui['node_parent'].setLight(self.name_gui['lighting']\
            ['ambient_node'])

        #Get the actor bounds and set the name node position
        bound_min, bound_max = self.Actor.getTightBounds()
        bound_normal = bound_max-bound_min
        
        #The gravity walker and base physics nodes have different positions,
        #so change the Z location of the name node based on the the parent node
        if nodePos != '':
            #We assume it's a gravity walker
            nodeZ = -bound_normal[2] + .9
        else:
            #Assume it's a physics node
            nodeZ = bound_normal[2] - 1.5
            
        #Set the node position
        self.name_gui['node_parent'].setPos(0,0, nodeZ)
                
    """----------------------------------------
        Entity Physics
        ---------------------------------------"""           
    def init_entity_physics(self, bit_wall=2, bit_floor=1,
                c_trav=CollisionTraverser(),
                bit_npc=3, bit_player=4, startPos=(0,0,20)):    
        """Set up the physics for the entity
        -Pass in a default CollisionTraverser, but normally one will be passed
        in"""
        c_trav = base.cTrav
        # Create a sphere physics node
        # Note: Physics Actors are separate from animated Actors!
        self.physics['collisionActor'] = render.attachNewNode(ActorNode("BoxActorNode"))
        self.Actor.reparentTo(self.physics['collisionActor'])
        
        #Set the actor position relative to the collision sphere
        self.Actor.setPos(0,0,-.5)
        # Position the spheres randomly in the air
        self.physics['collisionActor'].setPos(startPos)
        
        # Associate the default PhysicsManager for this ActorNode
        #self.physics['collisionActor'] = self.Actor
        base.physicsMgr.attachPhysicalNode(self.physics['collisionActor'].node())
        
        # Let's set some default body parameters such as mass, and randomize our mass a bit
        self.physics['collisionActor'].node().getPhysicsObject().setMass(180)
            
        # Because this object will be sending collisions(ie: acting as a From object, in Panda3d
        # terms), it needs to contain a collision node presentation, as poly-poly tests are not
        # supported in Panda3d
        sphereColNode = self.physics['collisionActor'].attachNewNode(CollisionNode('sphere-cnode'))
        sphereColSphere = CollisionSphere(0, 0, 0, .5)
        sphereColNode.node().addSolid(sphereColSphere)
        
        # We only want to be treated as a sphere for incoming collisions
        # Why do we have the wall bit set here too?  So that the player will react to this sphere
        # and be pushed out of it with its wall sphere
        cMask = BitMask32()
        cMask.setBit(2)
        cMask.setBit(3)
        sphereColNode.setCollideMask(cMask)
        
        # But, we will collide with either spheres, walls, floor, or player
        cMask.clear()
        cMask.setBit(3)
        cMask.setBit(1)
        cMask.setBit(2)
        cMask.setBit(4)
        sphereColNode.node().setFromCollideMask(cMask)
        
        # Now, to keep the spheres out of the ground plane and each other, 
        #let's attach a physics handler to them
        sphereHandler = PhysicsCollisionHandler()
        
        # Set the physics handler to manipulate the sphere actor's transform.
        sphereHandler.addCollider(sphereColNode, self.physics['collisionActor'])
        
        # This call adds the physics handler to the traverser list
        #(not related to last call to addCollider!)
        base.cTrav.addCollider(sphereColNode, sphereHandler)
        
        # Now, let's set the collision handler so that it will also do a 
        #CollisionHandlerEvent callback
        # But...wait?  Aren't we using a PhysicsCollisionHandler?
        # The reason why we can get away with this is that all 
        # CollisionHandlerXs are inherited from CollisionHandlerEvent,
        # so all the pattern-matching event handling works, too
        #sphereHandler.addInPattern('%fn-into-%in')
        sphereHandler.addOutPattern('into-%in')
        sphereHandler.addOutPattern('outof-%in')
        
        #Set the coefficients of friction for the sphere colliders, helps to
        #minimize sliding on uneven terrain
        sphereHandler.setStaticFrictionCoef(.7)
        sphereHandler.setDynamicFrictionCoef(.7)

        """Handle mouse events"""
        #Set an object tag for the current object
        self.physics['collisionActor'].setTag('mouse_obj_tag', '1')
        
        #Set a python tag that stores the current object
        self.physics['collisionActor'].setPythonTag('entity', self)

        """Attach the collisionActor to the entity root node"""
        self.physics['collisionActor'].reparentTo(EoAUniverse.nodes\
            ['entity_root'])
            
        """Turn off any lights on the object"""
        #self.physics['collisionActor'].setLightOff()
        #self.physics['collisionActor'].setLight(EoAUniverse.lights['alnp'])
        #Show the collision sphere
        if DEBUG:
            sphereColNode.show()
            
    """----------------------------------------
        Gravity Walker Physics (Mainly used for PC)
        ---------------------------------------"""    
    def init_entity_physics_gravity_walker(self):
        """Set up a gravity walker for the main character"""
        
        # Create a GravityWalker and let's set some defaults
        #Create an empty dictionary to store physics for actors
        self.physics['playerWalker'] = GravityWalker()
        
        self.physics['playerWalker'].setAvatar(self.Actor)
        self.physics['playerWalker'].setWalkSpeed(forward=5,\
            jump=15, reverse=4, rotate=90)
                        
        self.physics['playerWalker'].setWallBitMask( \
            BitMask32().bit( \
            EoAUniverse.physics['collisions']['bit_masks']['bit_values']
            ['wall']))
                        
        self.physics['playerWalker'].setFloorBitMask(\
            BitMask32().bit(EoAUniverse.physics['collisions']\
            ['bit_masks']['bit_values']['floor']))
                        
        self.physics['playerWalker'].initializeCollisions(
                base.cTrav, 
                self.Actor, avatarRadius=0.5,
                floorOffset=0.1, reach=0.5)
                        
        self.physics['playerWalker'].enableAvatarControls()
        self.physics['playerWalker'].placeOnFloor()

        # By setting the wall sphere to a player bitmask, we can have spheres 
        #we created above react against the player, since they are using a
        #CollisionPusherHandler
        self.physics['playerWalker'].cWallSphereNodePath.\
            setCollideMask(BitMask32().bit(EoAUniverse.physics['collisions']\
            ['bit_masks']['bit_values']['player']))  
            
            
        """Handle mouse events"""
        #Set an object tag for the current object
        self.Actor.setTag('mouse_obj_tag', '1')
        
        #Set a python tag that stores the current object
        self.Actor.setPythonTag('entity', self)

        """Attach the collisionActor to the entity root node"""
        self.Actor.reparentTo(EoAUniverse.nodes\
            ['entity_root'])
            
        #Show the physics indictator if DEBUG is set
        if DEBUG:
            self.physics['playerWalker'].setAvatarPhysicsIndicator(True)
        
    """---------------------------------------------------------------------
        Entity Functions
        --------------------------------------------------------------------"""  
    """----------------------------------------
        Position Functions
        ---------------------------------------"""        
    def setPos(self,x,y,z):
        if self.physics['is_gravity_walker']:
            self.Actor.setPos(x,y,z)
        else:
            self.physics['collisionActor'].setPos(x,y,z)
            
    def getPos(self):
        if self.physics['is_gravity_walker']:
            return self.Actor.getPos()
        else:
            return self.physics['collisionActor'].getPos()
                                
    """----------------------------------------
        Equip Functions
        ---------------------------------------"""
    def equip_item(self, location, modelLocation, item, itemPos, itemHpr,
                    itemScale=1):
        """
        equipItem
        
        takes in a target actor, location and item / item settings
        """
        #Set the location on the target actor
        self.body[location] = self.exposeJoint(None, 'modelRoot', 
                    modelLocation)
        
        #Create the initial model configuration
        modelSetup = (target_dir + "/models/%s" %(item), itemPos, itemHpr, 1)
        
        #Configure the model
        model = loader.loadModel(modelSetup[0]) #load the model 
        model.setPos(itemPos[0], itemPos[1], itemPos[2]) #set the position
        model.setHpr(itemHpr[0], itemHpr[1], itemHpr[2]) #set the hpr
        model.setScale(itemScale) #set the item's scale
        
        
        #Reparent the model to the exposed joint(targetActor.body)
        model.reparentTo(self.body[location])
        model.show()   
       
    def unequip_item(self, location):
        """Unequip an item at the current location.
        Add the unequipped item to the inventory"""
        pass
                 
    """----------------------------------------
        Target Functions
        ---------------------------------------"""
    def set_target(self, target=None):
        """Set our actor's target"""
        
        #Set the target
        self.target = target
        
        #Update the target box GUI element
        EoAUniverse.GUI.update_gui_element_target_box()
        
    def get_target(self):
        """Returns the actor's current target"""
        return self.target
        
    """----------------------------------------
        Damage functions
        ---------------------------------------"""
    def take_damage(self, dmg_amt=0, dmg_type=0, dmg_elemental=None, 
                    dmg_extra=0, dmg_amt_override=0):
        """Takes an amount of damage and deals it based on character's stats
        
        dmg_amt: base amount of damage to take
        dmg_type: type of damage (combat or magic...more?)
        dmg_elemental: elemental type
        dmg_extra: and extra damage effects (extra elemental dmg? etc)
        dmg_amt_override: deals X amount of damage regardless of player's stats
            should this be used much, if at all?
        """
        
        #Create variable to hold final damage amount
        final_dmg_amt = 0
        
        """Calculate dmg from physical / magic type"""
        #Check for damage type
        #COMBAT
        if dmg_type == 0:
            #Calculate damage based on character physcial stats
            #TODO 
            #   calculate
            final_dmg_amt += dmg_amt
        #MAGIC
        elif dmg_type == 1:
            #Calculate damage based on character spell stats
            #TODO 
            #   calculate
            final_dmg_amt += dmg_amt
        
        """Calculate dmg from elemental type"""
        #TODO
        # Figure out best way to do this
        
        """Other dmg stuff - need to do"""
        
        #Take damage (reduce entity health)
        self.health -= final_dmg_amt
        
        #Update GUI elements associated with the entity
        EoAUniverse.GUI.update_gui_elements()
        
    
    """----------------------------------------
        Base Functions Overrides
        ---------------------------------------"""
    def __str__(self):
        """Str override.  Overrides print function (e.g. print Entity)"""
        return self.name
        
"""---------------------------------------------------------------------------
    GUI Class
    -----------------------------------------------------------------------"""    
class EoAGUI(DirectObject):
    """Class that handles the GUI.  Eventually, we'll support GUI customization
    
    METHODS
    ---------
    update_gui()
        called when a GUI update needs to be made - e.g. when the player takes 
        damage.
        
    Set up the GUI dict and GUI nodes.  
    Some elements will be toggleable via command keys (e.g. 'i' for 
    inventory) so we set to node.hide() by default
    
    #create egg
    #egg-texture-cards is used to create animated textures essentially, but
    #for now we'll just use it to generate a card + texture at once
    #egg-texture-cards -o button_maps.egg -p 240,240 button_disabled.png            
    '''
    #Creating a CARD instead of using the egg maker
    CM=CardMaker('')
    card=base.a2dBottomLeft.attachNewNode(CM.generate())
    card.setScale(.25)
    #card.setTexture(tex)
    card.setTransparency(1)
    ost=OnscreenText(parent=base.a2dBottomLeft, font=loader.loadFont('cmss12'),
       text='press\nSPACE\nto cycle', fg=(0,0,0,1),shadow=(1,1,1,1), scale=.045)
    NodePath(ost).setPos(card.getBounds().getCenter()-ost.getBounds().getCenter())
    '''
    """
    
    def __init__(self):
        #Set up some object attributes
        self.target_box = {}
        self.inventory = {'text_nodes':{'stats':{}}}
        self.persona = {}
        
        #Call to create the GUI elements
        self.draw_gui()
    
    """=======Draw GUI==========
    DRAW GUI
    ======================="""
    def draw_gui(self):
        """-----------CREATE GUI ELEMENTS-------------------------"""
        """Elements always on screen"""
        self.load_persona()
        self.load_target_box()
       
        """Toggleable elements"""
        self.load_inventory()
       
        """------------
        Set up config key - LATER WHEN REARRANGING CODE - MOVE TO KEY CONFIG
        """
        #inventory
        self.accept ('i', self.toggle_gui_element, [self.inventory\
                ['container_node']])  # hit escape to quit!
        
    """=======Persona==========
    PERSONA SETUP
    ======================="""
    def load_persona(self):
        """Load the persona on screen GUI element that shows character info
        
        Shows name, health and power with percentages and health / power bars
        """
        #Persona Box (Rename later?)
        self.persona['container_node'] = base.a2dTopRight.\
            attachNewNode("persona_container")
            
        self.persona['persona_bg_node'] = loader.loadModel(target_dir+\
            '/gui/persona.egg')
        #Reparent to the persona container
        self.persona['persona_bg_node'].reparentTo(self.persona['container_node'])
        self.persona['container_node'].setTransparency(1)
        self.persona['container_node'].setScale(.6)
        self.persona['container_node'].setPos(-.31,0,-.32)
        
        #Person text
        self.persona['persona_name'] = OnscreenText(parent=\
            self.persona['container_node'], 
            text=EoAUniverse.entities['PC'].name,
            pos=(0,.3), scale=0.085, fg=(1,1,1,1),
            align=TextNode.ACenter, mayChange=1)
        
        """HEALTH"""
        #Text
        #y is inverted as the text is aligned to the top right
        self.persona['health_percent'] = OnscreenText(parent=\
            self.persona['container_node'], text = '', pos=(.38,.145), 
            scale=0.07,fg=(1,1,1,1), align=TextNode.ACenter, mayChange=1)
        
        #Image
        #Persona Box (Rename later?)
        #Use a DirectWaitBar, good for displaying status bars
        self.persona['health_bar'] = DirectWaitBar(text = "", 
            value=50, pos=(-.06,0,.155), scale=(.377,0,.182),
            relief=None)
        self.persona['health_bar'].setTransparency(1)
        self.persona['health_bar'].reparentTo(self.persona['container_node'])
        self.persona['health_bar'].setAlphaScale(.5)
        
        """POWER"""
        #Text
        #y is inverted as the text is aligned to the top right
        self.persona['power_percent'] = OnscreenText(parent=\
            self.persona['persona_bg_node'], text = '', pos=(.38,-.024), 
            scale=0.07,fg=(1,1,1,1), align=TextNode.ACenter, mayChange=1)
        
    """=======Target Box==========
    TARGET BOX SETUP
    ======================="""
    def load_target_box(self):
        """Loads the on screen targetbox
        
        Shows the player's target's name and a bar indicating health percentage
        """
    
        #Create a parent node for the target box and the corresponding 
        #   target text
        #The container node is simply a node that will be the parent of the 
        #   gui target box image node and the target box text node
        self.target_box['container_node'] = base.a2dTopRight.\
            attachNewNode("target_box_container")
            
        #Load the target box model (really just a card with a texture on it)
        #Make this extensible later....
        self.target_box['node_path'] = loader.loadModel(target_dir+\
            '/gui/target_box.egg')
        
        #Attach the target box to the container node
        self.target_box['node_path'].reparentTo( \
            self.target_box['container_node'])
        
        #Make sure it's fully opaque
        self.target_box['node_path'].setTransparency(1)
        self.target_box['node_path'].setAlphaScale(1)
        
        #Set the target box container position and scale of the container
        self.target_box['container_node'].setPos(-.32,0,-.7)
        self.target_box['container_node'].setScale(.6)
        
        """Target name text"""
        #Set the target box text, attach it to the container node
        #we could onscreentext here instead, but textnode gives more control   
        #Create a text node for the target text
        self.target_box['target_text'] = TextNode('gui_target_text')
        self.target_box['target_text'].setText("")
        self.target_box['target_text'].setAlign(TextNode.ACenter)

        #Create a nodepath to attach the target text to
        self.target_box['target_text_node_path'] = \
            self.target_box['container_node'].attachNewNode(\
            self.target_box['target_text'])
        #Set the scale and position
        self.target_box['target_text_node_path'].setScale(0.07)
        self.target_box['target_text_node_path'].setPos(0,0,.32)
        
        """Target health percentage"""
        self.target_box['target_health_percent'] = OnscreenText(parent=\
            self.target_box['container_node'], text = '', pos=(.37,.175), 
            scale=0.07,fg=(1,1,1,1), align=TextNode.ACenter, mayChange=1)

    """=======Invetory=========================================
    INVENTORY SETUP
    ======================="""    
    def load_inventory(self):
        """Sets up inventory - inventory comes up on key press
        
        Shows character's equipped items, inventory, money, stats, 
        elemental attributes, health / power"""

        #Create a container node to store the inventory image and text nodes in
        #   similar to above
        self.inventory['container_node'] = base.aspect2d.\
            attachNewNode("inventory_container")
            
        #Create the inventory image node and reparent it to the container
        self.inventory['node_path'] = loader.loadModel(target_dir+\
            '/gui/inventory.egg')
        self.inventory['node_path'].reparentTo(\
            self.inventory['container_node'])
            
        #Set the position and scale of the inventory image node
        self.inventory['node_path'].setTransparency(1)
        self.inventory['node_path'].setAlphaScale(1)
        
        #Set the position, sacle, and hide the iventory container node
        self.inventory['container_node'].setPos(0,0,0)
        self.inventory['container_node'].hide()
        self.inventory['container_node'].setScale(.8)
        
        """Inventory text nodes"""
        #Create a container node path to hold all the stat text nodes
        #Attach the stats text node to the stats node path
        self.inventory['text_nodes']['stats']['stats_text_nodes'] = \
            NodePath("inventory_stats_text_nodes")
        
        #Create text nodes for all the stats
        #tweak the position later, see function for more details
        self.gui_inventory_add_stat(stat='agi')
        self.gui_inventory_add_stat(stat='dex', pos=(0,0,-1.5))
        self.gui_inventory_add_stat(stat='int', pos=(0,0,-3))
        self.gui_inventory_add_stat(stat='sta', pos=(0,0,-4.6))
        self.gui_inventory_add_stat(stat='str', pos=(0,0,-6.2))
        self.gui_inventory_add_stat(stat='wis', pos=(0,0,-7.7))
        
        #reparent the stat text container node to the inventory container node
        self.inventory['text_nodes']['stats']['stats_text_nodes'].\
            reparentTo(self.inventory['container_node'])        
            
        #Scale and position the stats container node (which contains the 
        #   stats_text_nodes
        self.inventory['text_nodes']['stats']['stats_text_nodes'].\
            setScale(0.05)
        self.inventory['text_nodes']['stats']['stats_text_nodes'].\
            setPos(.22,0,-.42)
            
    """=======Add stat text nodes====
    GUI INVENTORY ADD STAT
    ======================="""
    def gui_inventory_add_stat(self, stat='', pos=(0,0,0)):
        """Function to create stat text nodes. 
        
        Need to be more extensible for other text nodes in the inventory and
        other GUI elements
        
        TODO:
            Make more extensible
        
        #Create text nodes for stats, health, power, etc
        #This is the basic process:
        #   -Create a text node for each stat
        #   -Reparent the text node to an empty container node so we can set
        #       position easier
        #   -Reparent that empty container node for the text node to another
        #       empty container node so the stat nodes are all grouped together
        """
        
        #Adds a stat text node and attaches the text node
        #Create an empty text node container for the stat
        self.inventory['text_nodes']['stats'][stat] = TextNode(\
        'inventory_stat_agi')
        
        #Set the initial text
        #Get the stat from the PC entity
        text = str(EoAUniverse.entities['PC'].stats[stat])
        self.inventory['text_nodes']['stats'][stat].setText(text)
        
        #Set alignment to the right
        self.inventory['text_nodes']['stats'][stat].setAlign(TextNode.\
            ARight)
            
        #Create empty container node path for the stat
        #   attach it to the base stats_text_nodes container which contains all
        #   these empty container nodes for individual stats
        #   Attach the text node we created to the base stat_text_nodes 
        #   container so we can position the stat_text_nodes container and 
        #   move all the stat text nodes at once
        
        self.inventory['text_nodes']['stats'][stat+'_container'] = \
            self.inventory['text_nodes']['stats']\
            ['stats_text_nodes'].attachNewNode(self.inventory\
            ['text_nodes']['stats'][stat])
        #Position the text node container
        self.inventory['text_nodes']['stats'][stat+'_container'].\
            setPos(pos)
               
    """---------------------------------------------------------------------
        GUI Functions
        --------------------------------------------------------------------"""  
    """=======Toggle GUI Element==========
    TOGGLE GUI ELEMENT
    ======================="""
    def toggle_gui_element(self, obj=None):
        """Turns on / off a GUI element"""
        
        try:
            #Toggle node being shown / hidden
            if obj.isHidden():
                obj.show()
            else:
                obj.hide()
        except:
            #Not a good idea for a catch all normally, but we don't want to 
            #break the game if we do catch something
            "Object is hidden"
            
    """=======UPDATE GUI Element=======================================
    UPDATE GUI ELEMENT
    ======================="""  
    def update_gui_elements(self, gui_element=None):
        """Updates the GUI, or a certain element if passed in"""
        
        """Update everything"""
        if gui_element is None:
            #If there is no GUI element passed in, update everything
            """Update Persona"""
            self.update_gui_element_persona()
            
            """Update target health (if any target is selected)"""
            self.update_gui_element_target_box()
                
            """Update inventory (health, power, stats, money, etc)"""   
            
        """Update certain elements"""
        
    """=======Update Persona====
    UPDATE GUI ELEMENT PERSONA
    ======================="""       
    def update_gui_element_persona(self):
        """Update the persona GUI element (top right box)"""

        #Calculate percent by taking a float of the health / power and 
        #   divide it by the max health / power then multiple by 100

        #HP percent = health / max health
        hp_percent =  ( float(EoAUniverse.entities['PC'].health) / \
                        EoAUniverse.entities['PC'].max_health ) * \
                        100

        #Power percent = power / max power
        power_percent = ( float(EoAUniverse.entities['PC'].power) / \
                        EoAUniverse.entities['PC'].max_power) * \
                        100

        #Display a string representation of the percent converted to an int
        self.persona['health_percent'].setText(str(int(hp_percent)))
        self.persona['power_percent'].setText(str(int(power_percent)))
        
    """=======Update GUI Target Box====
    UPDATE GUI ELEMENT TARGET BOX
    ======================="""
    def update_gui_element_target_box(self):
        """Update the target box target text and health"""
        
        if EoAUniverse.entities['PC'].target is not None:
            #Get and display target's health
            target_health = ( float(EoAUniverse.entities['PC'].target.health) /\
                        EoAUniverse.entities['PC'].target.max_health) * \
                        100
            
            #Update the target box target name text
            self.target_box['target_text'].setText(EoAUniverse.entities['PC'].\
                    target.name)  
                    
            #Update the target box percentage text
            self.target_box['target_health_percent'].setText(str(int(\
                target_health)))
        
        else:
            #If no target, clear all text
            self.target_box['target_text'].setText("")
            self.target_box['target_health_percent'].setText("")
            
def null():
    #empty dummy func
    pass