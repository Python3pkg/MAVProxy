#!/usr/bin/env python

"""
  MAVProxy horizon indicator.
"""
import multiprocessing
import time

class HorizonIndicator():
    '''
    A horizon indicator for MAVProxy.
    '''
    def __init__(self,title='MAVProxy: Horizon Indicator'):
        self.title  = title
        # Create Pipe to send attitude information from module to UI
        self.child_pipe_recv,self.parent_pipe_send = multiprocessing.Pipe(duplex=False)
        self.close_event = multiprocessing.Event()
        self.close_event.clear()
        self.child = multiprocessing.Process(target=self.child_task)
        self.child.start()
        self.child_pipe_recv.close()

    def child_task(self):
        '''child process - this holds all the GUI elements'''
        self.parent_pipe_send.close()
        
        from .wx_loader import wx
        from .wxhorizon_ui import HorizonFrame
        # Create wx application
        app = wx.App(False)
        app.frame = HorizonFrame(state=self, title=self.title)
        app.frame.SetDoubleBuffered(True)
        app.frame.Show()
        app.MainLoop()
        self.close_event.set()   # indicate that the GUI has closed

    def close(self):
        '''Close the window.'''
        self.close_event.set()
        if self.is_alive():
            self.child.join(2)

    def is_alive(self):
        '''check if child is still going'''
        return self.child.is_alive()

if __name__ == "__main__":
    # test the console
    multiprocessing.freeze_support()
    horizon = HorizonIndicator()
    while horizon.is_alive():
        print('test')
        time.sleep(0.5)
