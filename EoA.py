'''EoA
End of Ages

This file contains the majority EoA's library classes and functions

'''

'''Import everything'''
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

from pandac.PandaModules import *


class EoAActor(Actor):
    '''Actor
    Our main actor class'''
    def __init__(self, name="Unnamed", modelName="default", scale=.2, health=0, power=0, addToWorld=True, startPos=False, modelStates=False ):
        '''init
        Set up our Actor's attributes and function call, crete the actor
        EoAActor extends Panda3d's Actor'''
        
        '''Extend Actor'''
        #Call the panda3d actor init
        modelLocation = "models/%s" % (modelName)
        try:
            if not modelStates:
                modelStates = {"run":"models/%s-run" % (modelName),
                           "walk":"models/%s-walk" % (modelName)}
            else:
                modelStates = modelStates
        except:
            pass
            
        Actor.__init__(self, modelLocation, modelStates)
        
        #stats
        self.health = 0
        self.power = 0
        
        #Our actor's inventory.
        self.inventory = []
        
        #Default body parts.  Different creatures have different parts
        self.body = {'head':None, 'chest': None, 'shoulders':None, 
                            'arms':None, 'hands':None, 
                            'legs':None, 'feet':None,
                            'primary': None, 'secondary': None}
        
        #Equipped items. Body parts link to items in inventory
        self.equippedItems = {}
        
        #Set the name
        self.name = name
        
        '''Add character to world'''
        #Add to the world if set to true (by default it is)
        #Some actors may need to be added to the game but not 
        #rendered
        if addToWorld:
            self.reparentTo(render)
            self.setScale(scale)
            
            #If startPos is not passed in, set a default position
            if not startPos:
                self.setPos(200,200,200)
            else:
                self.setPos(startPos)
            
       
    def equipItem(self, location, modelLocation, item, itemPos, itemHpr, itemScale=1):
        '''
        equipItem
        
        takes in a target actor, location and item / item settings
        '''
        #Set the location on the target actor
        self.body[location] = self.exposeJoint(None, 'modelRoot', modelLocation)
        
        #Create the initial model configuration
        modelSetup = ("models/%s" % (item), itemPos, itemHpr, 1)
        
        #Configure the model
        model = loader.loadModel(modelSetup[0]) #load the model 
        model.setPos(itemPos[0], itemPos[1], itemPos[2]) #set the position
        model.setHpr(itemHpr[0], itemHpr[1], itemHpr[2]) #set the hpr
        model.setScale(itemScale) #set the item's scale
        
        
        #Reparent the model to the exposed joint (targetActor.body)
        model.reparentTo(self.body[location])
        model.show()   
       
    def unEquipItem(self, location):
        '''Unequip an item at the current location.
        Add the unequipped item to the inventory'''
        pass
            
    def setTarget(self, target):
        '''Set our actor's target'''
        pass
        
    def getTarget(self):
        '''Returns the actor's current target'''
        pass
        
    
    
    