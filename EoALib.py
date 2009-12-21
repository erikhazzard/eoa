'''EoA
End of Ages

This file contains the majority EoA's library classes and functions

'''
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

'''Set target directory'''
targetDir = os.path.abspath(sys.path[0])
targetDir = Filename.fromOsSpecific(targetDir).getFullpath()


DEBUG = False
'''---------------------------------------------------------------------------
    Universe Functions
    -----------------------------------------------------------------------'''    
class EoAUniverse(DirectObject):
    #Set up the physics
    physics = {'collisions': \
                            {'bit_masks': \
                                {'bit_values':{}} \
                            }, \
                'gravity':{} \
                }
    
    environment = ''
    
    nodes = {}

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
            ground.setCollideMask(BitMask32().bit(EoAUniverse.physics['collisions']\
                            ['bit_masks']['bit_values']['floor']))
        
        for rock in EoAUniverse.environment.findAllMatches('**/Rock*'):
            rock.setCollideMask(EoAUniverse.physics['collisions']['bit_masks']\
                            ['bit_values']['wall'])
        
        '''Init Mouse collision controler'''
        #setup our collision handler queue
        self.physics['collisions']['mouse_cHandler'] = CollisionHandlerQueue()

        self.physics['collisions']['mouse_picker_node'] = \
                CollisionNode('mouseRay')
        
        self.physics['collisions']['mouse_picker_np'] = \
                base.camera.attachNewNode(self.physics['collisions']\
                ['mouse_picker_node'])
        
        self.physics['collisions']['mouse_picker_node'].setFromCollideMask(\
                GeomNode.getDefaultCollideMask())
        
        self.physics['collisions']['picker_ray']=CollisionRay()
        
        self.physics['collisions']['mouse_picker_node'].addSolid(\
                self.physics['collisions']['picker_ray'])
        
        base.cTrav.addCollider(self.physics['collisions']['mouse_picker_np'],
                self.physics['collisions']['mouse_cHandler'])
                
        '''Show collisions if debug'''
        if DEBUG:
            base.cTrav.showCollisions(render)

'''---------------------------------------------------------------------
    Entity Functions
    --------------------------------------------------------------------'''  
class Entity(Actor, EoAUniverse):
    '''Entity
    Our main Entity class
    Extends Panda3d's Actor
    '''
    def __init__(self, name="Unnamed", modelName="default", scale=1, health=0,
                power=0, addToWorld=True, startPos=False, modelStates=False,
                gravity_walker=False):
        '''init
        Set up our Actor's attributes and function call, crete the actor
        Entity extends Panda3d's Actor'''
        
        '''Set up the Actor'''
        #Call the panda3d actor init
        modelLocation = targetDir + "/models/%s" %(modelName)
        try:
            if not modelStates:
                modelStates = {"idle":targetDir + "/models/%s-idle" %(modelName),
                               "walk":targetDir + "/models/%s-walk" %(modelName)}
            else:
                modelStates = modelStates
        except:
            pass

        #Extend the actor
        self.Actor = Actor()
        self.Actor.loadModel(modelLocation)
        self.Actor.loadAnims(modelStates)
        self.Actor.loop('idle')
        
        '''Set Up Entity Stats'''
        #stats
        self.health = 0
        self.power = 0
        
        #Default body parts.  Different creatures have different parts
        self.body = {'head':None, 'chest': None, 'shoulders':None, 'back':None,
                            'arms':None, 'hands':None, 
                            'waist':None, 'legs':None, 'feet':None,
                            'primary': None, 'secondary': None}
        
        #Our actor's inventory.
        self.inventory = []
        
        #Equipped items. Body parts link to items in inventory
        self.equippedItems = {}
        
        #Set the name
        self.name = name
        
        '''Add character to world'''
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
               
        '''Set up Entity Physics'''
        self.physics = {}
        
        '''Determine if the entity is using the GravityWalker class'''
        self.physics['is_gravity_walker'] = gravity_walker
        
        #Gravity walker is for the PC controllable character (generally)
        if not self.physics['is_gravity_walker']:
            self.init_physics(startPos=startPos)
        else:
            self.init_physics_gravity_walker()
    
        '''Store the entity's last known coordinates
        We use this to check if the entity has moved for animations'''
        self.prevPos = tuple([int(i) for i in self.getPos()])
        
        '''By default, the entity is not moving'''
        self.is_moving = False
        self.moving_buffer = 0
        
        '''Show the name node'''
        self.name_gui = {}
        if not self.physics['is_gravity_walker']:
            self.init_name_node(self.name)
        else:
            self.init_name_node(self.name,nodePos='-')
    '''---------------------------------------------------------------------
        Init Functions
        --------------------------------------------------------------------'''
    '''--------------------------------------
        Name Node Functions
        -------------------------------------'''
    def init_name_node(self, name, nodePos=''):
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
                
    '''----------------------------------------
        Entity Physics
        ---------------------------------------'''           
    def init_physics(self, bit_wall=2, bit_floor=1,
                c_trav=CollisionTraverser(),
                bit_npc=3, bit_player=4, startPos=(0,0,20)):    
        '''Set up the physics for the entity
        -Pass in a default CollisionTraverser, but normally one will be passed
        in'''
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

        '''Handle mouse events'''
        self.physics['collisionActor'].setTag('myObjectTag', '1')
        
        """Attach the collisionActor to the entity root node"""
        self.physics['collisionActor'].reparentTo(EoAUniverse.nodes\
            ['entity_root'])
        
        #Show the collision sphere
        if DEBUG:
            sphereColNode.show()
            
    '''----------------------------------------
        Gravity Walker Physics (Mainly used for PC)
        ---------------------------------------'''    
    def init_physics_gravity_walker(self):
        '''Set up a gravity walker for the main character'''
        
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
                
        #Show the physics indictator if DEBUG is set
        if DEBUG:
            self.physics['playerWalker'].setAvatarPhysicsIndicator(True)
        
    '''---------------------------------------------------------------------
        Entity Functions
        --------------------------------------------------------------------'''  
    '''----------------------------------------
        Position Functions
        ---------------------------------------'''        
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
                
                
    '''----------------------------------------
        Equip Functions
        ---------------------------------------'''
    def equip_item(self, location, modelLocation, item, itemPos, itemHpr,
                    itemScale=1):
        '''
        equipItem
        
        takes in a target actor, location and item / item settings
        '''
        #Set the location on the target actor
        self.body[location] = self.exposeJoint(None, 'modelRoot', 
                    modelLocation)
        
        #Create the initial model configuration
        modelSetup = (targetDir + "/models/%s" %(item), itemPos, itemHpr, 1)
        
        #Configure the model
        model = loader.loadModel(modelSetup[0]) #load the model 
        model.setPos(itemPos[0], itemPos[1], itemPos[2]) #set the position
        model.setHpr(itemHpr[0], itemHpr[1], itemHpr[2]) #set the hpr
        model.setScale(itemScale) #set the item's scale
        
        
        #Reparent the model to the exposed joint(targetActor.body)
        model.reparentTo(self.body[location])
        model.show()   
       
    def unequip_item(self, location):
        '''Unequip an item at the current location.
        Add the unequipped item to the inventory'''
        pass
            

       
    '''----------------------------------------
        Target Functions
        ---------------------------------------'''
    def set_target(self, target):
        '''Set our actor's target'''
        pass
        
    def get_target(self):
        '''Returns the actor's current target'''
        pass
        
       