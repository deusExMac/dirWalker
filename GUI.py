#
#
#
# tzagara|v0.3@13/04/2024




import sys
import time
import datetime

import requests
import customtkinter as ctk

# TODO: How to properly deal with circular imports?
# See https://stackoverflow.com/questions/7336802/how-to-avoid-circular-imports-in-python
import functionality



        
def doGUIOperation(op='', query='', win=None, progressLabel=None, statusLabel=None, cfg={}):

    
    cfg['guiwindow'] = win
    cfg['guiprogress'] = progressLabel
    cfg['guistatus'] = statusLabel

    if op=='search':
       sandbox.search(query=f'{query}', criteria=cfg)
    elif op=='export':
         sandbox.export(cfg)

    # Small delay before closing window to give
    # a better glimpse on the numbers or messages. 
    time.sleep(0.7)
    
    closeWindow(win)


    
def doSearch(query='', win=None, progressLabel=None, statusLabel=None, cfg={}):

    
    cfg['guiwindow'] = win
    cfg['guiprogress'] = progressLabel
    cfg['guistatus'] = statusLabel
    
    search(query=f'{query}', criteria=cfg)

    # Small delay before closing window to give
    # a better glimpse on the numbers or messages. 
    time.sleep(0.7)
    
    closeWindow(win)


   

    

def closeWindow(w=None):
    if w is not None:
       #print('>>> destroying...')
       w.quit()
       w.destroy()




    
def progressCommand(op='export', q='', config={}):

   # light, dark and System supported
   ctk.set_appearance_mode("System")
   ctk.set_default_color_theme("blue")

   # Create main window  of app
   root = ctk.CTk()
   root.geometry("550x130")
   root.title('Search progress')

   frame = ctk.CTkFrame(master=root)
   frame.pack(pady=10, padx=70, fill="both", expand=True)


   # Create elements of main window

   # Progress label (current directory being scanned)   
   progressLbl = ctk.CTkLabel(master=frame, text=".....", font=("Roboto", 14) )
   progressLbl.pack(pady=10, padx=40, anchor="w")

   # Status (how many found)
   statusLbl = ctk.CTkLabel(master=frame, text="Found: 0",  text_color='red', font=("Roboto", 14) )
   statusLbl.pack(pady=5, padx=40, anchor="w")
   
   
   root.after(2, doGUIOperation, op, q, root, progressLbl, statusLbl, config)
   
   # Start the GUI
   root.mainloop()






if __name__ == '__main__':
   progressCommand('search', 'pdf')
