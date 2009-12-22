import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
from pandac.PandaModules import *
 
# Add some text
bk_text = "DirectOptionMenu Demo"
textObject = OnscreenText(text = bk_text, pos = (0.85,0.85), 
scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
 
# Add some text
output = ""
textObject = OnscreenText(text = output, pos = (0.95,-0.95), 
scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
 
# Callback function to set text
def itemSel(arg):
	if(arg != "Add"): #no need to add an element
		output = "Item Selected is: "+arg
		textObject.setText(output)
	else: #add an element
		tmp_menu = menu['items']
		new_item = "item"+str(len(tmp_menu))
		tmp_menu.insert(-1,new_item) #add the element before add
		menu['items'] = tmp_menu	
		#set the status message
		output = "Item Added is: "+new_item
		textObject.setText(output)
 
# Create a frame
menu = DirectOptionMenu(text="options", scale=0.1,items=["item1","item2","item3","Add"],
initialitem=2,highlightColor=(0.65,0.65,0.65,1),command=itemSel,textMayChange=1)
 
# Procedurally select a item
menu.set(0)
 
# Run the tutorial
run()