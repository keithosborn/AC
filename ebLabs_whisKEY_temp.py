# coding: utf-8

# this is a small change

# will this work?

import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import string
import colorsys
import maya.api.OpenMaya as OpenMaya
import math
import os
import json
from itertools import groupby
import copy
import traceback

__author__ = "Eric Bates, ebLabs.com, eblabs-tech.com"
__copyright__ = "Copyright 2015, Eric Bates"
__credits__ = ["Eric Bates"]
__maintainer__ = "Eric Bates"
__email__ = "eric@eric-bates.com"
__status__ = "Production"

'''
todo
* remove boring keys, classic style (full curves)
* in/out compatibility with groupmove tool?
* sandblaster slider
* add curve scale tool, pivot, amount to scale +-
* multiply, toggle for apply all/transforms only
* filter selection -remove keyed/non-keyed
'''


'''
1146 <type 'exceptions.Exception'> float division by zero
'''

'''
# Error: 'NoneType' object is not iterable
# Traceback (most recent call last):
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 1843, in rekeyOnKeys
#     Functions.rekeyOnKeys(objects=objects, matchLast=matchLast)
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 1258, in rekeyOnKeys
#     specialKeyTickTimes = cls.getSpecialKeyTickTimes(objects=specialKeyTimeTemplateObjects)
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 1352, in getSpecialKeyTickTimes
#     for a in keyableAttributes:
# TypeError: 'NoneType' object is not iterable # 

'''

'''
# Traceback (most recent call last):
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 4988, in slider_realtime_modifiers
#     self.slider_realtime(*args, **kwargs)
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 6378, in slider_realtime
#     self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 5078, in slider_realtime_standard
#     self.slider_exec(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)
#   File "/u/ecb/Pictures/ebLabs-workshop/whisKEY2/ebLabs_whisKEY.py", line 4965, in slider_exec
#     cmds.setAttr(a, newValue, clamp=True)
# RuntimeError: setAttr: The attribute 'GOBSMALLFACE01:bs_main2_ctrl.rotateX' is locked or connected and cannot be modified. # 
'''
'''
Traceback (most recent call last):
  File "/u/ecb/Public/eblabs/ebLabs_whisKEY.py", line 5586, in collectData
    ratio = (midTime - minTime) / (maxTime - minTime)
ZeroDivisionError: float division by zero
'''

'''
2015-10-14
    - set tangents, change to mel command
2015-09-22
    - use short attribute names, its way simpler!
    - updating all widgets to use buffered channels 
2015-09-18
    - more options for removing boring keys
    - progress bar for clean subframe/boring keys, also can cancel
    - cleanup collapse buttons
    - allow world space to work with just one key
    - fix pin selections with nothing selected
v prev
    - multiply now works with everything natively except scale/vis
    - key buttons to key highlighted channels, or all
    - rekey tools to use highlighted channels
    - added collapse buttons
    - added quick undo buttons
    - added ctrl slide for adjusting multipliers
    - fixed remove profiles
    - add ranges for rekeying operations
    - presets for worldspace and snapshot
    - allow for more channels when selected in the multiply slider
    - add collapse buttons
    - added move up/down
'''

# setup window container
class window:
    version = '2016-01-24'

    @classmethod
    def load(cls):
        # setup window
        windowName = 'whisKEY_Pro'
        if (cmds.window(windowName, exists=True)):
            cmds.deleteUI(windowName, window=True)
        if(cmds.windowPref(windowName, exists=True)):
            cmds.windowPref(windowName, remove=True)
        cls.window = cmds.window(windowName, widthHeight=(270, 400), title=windowName, bgc=[.7] * 3)

        # main form
        cls.mainScrollLayout = cmds.scrollLayout(childResizable=True, horizontalScrollBarThickness=16, verticalScrollBarThickness=16, bgc=[.25] * 3)
        cls.mainLayoutContainerForm = cmds.formLayout(parent=cls.mainScrollLayout)

        '''
        # menubar
        menuBar = cmds.menuBarLayout(parent = cls.mainLayoutContainerForm, bgc = [.3] * 3)
        widgetMenu = cmds.menu(parent = menuBar, label = 'Widgets')
        cmds.menu(widgetMenu, edit = True, postMenuCommand = partial(cls.setupFileMenu, parent = widgetMenu))
        '''


        # main column layout
        cls.mainColumnLayout = cmds.columnLayout(parent=cls.mainLayoutContainerForm, adjustableColumn=True, columnAttach=['both', 1], rowSpacing=2)

        # layout
        '''
        cmds.formLayout(cls.mainLayoutContainerForm, edit = True, attachForm = [(menuBar, 'top', 0)])
        cmds.formLayout(cls.mainLayoutContainerForm, edit = True, attachForm = [(menuBar, 'left', 0)])
        cmds.formLayout(cls.mainLayoutContainerForm, edit = True, attachNone = [(menuBar, 'bottom')])
        cmds.formLayout(cls.mainLayoutContainerForm, edit = True, attachForm = [(menuBar, 'right', 0)])
        '''

        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachForm=[(cls.mainColumnLayout, 'top', 0)])
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachForm=[(cls.mainColumnLayout, 'left', 0)])
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachNone=[(cls.mainColumnLayout, 'bottom')])
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachForm=[(cls.mainColumnLayout, 'right', 0)])


        # set version
        Functions.setVersion(cls.version)        
        
        # add widgets to the UI
        widget_base.setWidgetParent(parent=cls.getParent())
        widget_base.addWidgetsFromPrefs()

        # launch window
        cmds.showWindow(cls.window)

        # set focus
        cmds.setFocus(cls.window)
        
        # resize
        cls.resizeUI()

    @classmethod
    def resizeUI(cls, *args, **kwargs):
        #
        command = partial(cls.resizeUI_deferred)
        cmds.evalDeferred(command)

    @classmethod
    def resizeUI_deferred(cls, *args, **kwargs):
        # manual resize
        fudgeFactor = 12

        scrollLayoutHeight = cmds.formLayout(cls.mainLayoutContainerForm, query=True, height=True)
        scrollLayoutHeight += fudgeFactor  # add back in fudge factor

        # resize window
        cmds.window(cls.window, edit=True, height=scrollLayoutHeight)

    @classmethod
    def addWidgets(cls, *args, **kwargs):
        # get main ui parent
        parent = cls.getParent()        

        # check prefs first
        version, widgetData = Functions.retreivePrefs()

        # if there isnt widget data, get from defaults
        if not widgetData: # or version != cls.version:
            widgetData = cls.getDefaultWidgetData()
                        
        # load in all UI items
        for w in widgetData:
            # unpack data
            widgetDescription = w['description']
            widgetType = w['widgetType']
            widgetState = w['state']
            widgetExpandedState = True
            try:
                widgetExpandedState = w['expanded']
            except:
                pass

            # type
            if widgetType == 'inbetween':
                # create new item
                newItem = widget_tween(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'extras':
                # create new item
                newItem = widget_extras(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'worldSpace':
                # create new item
                newItem = widget_worldSpace(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'classic':
                # create new item
                newItem = widget_classic(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'curveOptions':
                # create new item
                newItem = widget_curveOptions(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'snapshot':
                # create new item
                newItem = widget_snapshot(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'principles':
                # create new item
                newItem = widget_principles(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'tools':
                # create new item
                newItem = widget_tools(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

        # resize UI
        cmds.evalDeferred(cls.resizeUI)

    @classmethod
    def getDefaultWidgetData(cls, *args, **kwargs):
        # 
        widgetData = widget_base.getDefaultWidgetData()
        return widgetData

    @classmethod
    def resetPrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')           
        # reset prefs
        Functions.clearPrefs(profile=profile)

    @classmethod
    def getParent(cls):
        return cls.mainColumnLayout

    @classmethod
    def addItem(cls, addItem, *args, **kwargs):
        # # add item
        widget_base.addItem(addItem)

        # store prefs
        cls.storePrefs()

        # resize UI
        cmds.evalDeferred(cls.resizeUI)

    @classmethod
    def storePrefs(cls, *args, **kwargs):
        widget_base.storePrefs()

class Functions():

    # set default prefs path
    prefsFilepath = os.path.normpath(os.path.join(cmds.internalVar(userAppDir=True), 'scripts', 'eblabs_prefs', 'whiskey.prefs'))
    version = 1
    activeProfile = 'default'
    profilesData = {}
    
    @classmethod
    def quickUndo(cls, *args, **kwargs): 
        command = partial(cls.quickUndo_wrapped)
        cmds.evalDeferred(command)   
    
    @classmethod
    def quickUndo_wrapped(cls, *args, **kwargs):
        try:
            # disable UI
            cls.suspendUI(True)
            
            # undo
            cmds.undo()
            
        except Exception, e:
            print 236, e
        finally:
            # enable UI
            cls.suspendUI(False)

    @classmethod
    def quickRedo(cls, *args, **kwargs): 
        command = partial(cls.quickRedo_wrapped)
        cmds.evalDeferred(command)   
            
    @classmethod
    def quickRedo_wrapped(cls, *args, **kwargs):
        try:
            # disable UI
            cls.suspendUI(True)
            
            # undo
            cmds.redo()
            
        except Exception, e:
            print 255, e
        finally:
            # enable UI
            cls.suspendUI(False)
    
    @classmethod
    def smashBaker(cls, selected, startTime, endTime, *args, **kwargs):
        # confirm with user
        count = 0
        if selected:
            count = len(selected)
        message = 'Smash Bake Selected {0} Objects?'.format(count)
        confirm = cmds.confirmDialog(title='Smash Bake', message=message, button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if confirm == 'Yes':
            try:
                # set base layer as current
                rootLayer = cmds.animLayer( query=True, root=True)
                if rootLayer:
                    allLayers = cmds.ls(type='animLayer')
                    for l in allLayers:
                        state = False
                        if l == rootLayer: 
                            state = True
                        cmds.animLayer(l, edit=True, selected=state)
                            
                # setup
                timeRange = [startTime, endTime+1]
                currentTime = cmds.currentTime(query=True)
                data = {}
                if selected:
    
                    # disable UI
                    cls.suspendUI(True)
    
                    # get attr list
                    attributeList = []
                    for s in selected:
                        attributes = cmds.listAttr(s, scalar=True, keyable=True, unlocked=True)
                        if attributes:
                            for a in attributes:
                                attribute = '{0}.{1}'.format(s, a)
                                attributeList.append(attribute)
                        else:
                            print 'SKIPPING, NO ATTRS FOR: ', s
    
                    # store anim
                    for f in range(timeRange[0], timeRange[1]):
                        cmds.currentTime(f, edit=True)
                        data[f] = {}
                        for a in attributeList:
                            data[f][a] = cmds.getAttr(a)
    
                    # break connections
                    for a in attributeList:
                        if cmds.connectionInfo(a, isDestination=True):
                            destination = cmds.connectionInfo(a, getExactDestination=True)
                            try:
                                source = cmds.connectionInfo(destination, sourceFromDestination=True)
                                cmds.disconnectAttr(source, destination)
                            except:
                                cmds.delete(destination, inputConnectionsAndNodes=True)
    
                    # add back animation
                    for f in data.keys():
                        # cmds.currentTime(f, edit=True)
                        for a in data[f].keys():
                            value = data[f][a]
                            cmds.setKeyframe(a, value=value, time=f)
                            '''
                            value = data[f][a]
                            cmds.setAttr(a, value)
                            cmds.setKeyframe(a)
                            '''
    
                    # refresh
                    cmds.currentTime(currentTime, edit=True)
    
                    # remove object from animation layers
                    for a in attributeList:
                        animLayers = cmds.listConnections(a, type='animLayer')
                        if animLayers:
                            for l in animLayers:
                                cmds.animLayer(l, edit=True, removeAttribute=a)
            except:
                pass
            finally:
                cls.suspendUI(False)
    
    @classmethod
    def queryTimeRange(cls, *args, **kwargs):
        checkHighlighted = False
        if 'checkHighlighted' in kwargs:
            checkHighlighted = kwargs.pop('checkHighlighted')
        #
        startTime = int(cmds.playbackOptions(q=True, animationStartTime=True))
        endTime = int(cmds.playbackOptions(q=True, animationEndTime=True))

        # highlighted ranges
        if checkHighlighted:
            rangeStart, rangeEnd = str(cmds.timeControl(mel.eval('$tmpVar=$gPlayBackSlider'), query=True, range=True)).replace('"', '').split(':')
            rangeStart = float(rangeStart)
            rangeEnd = float(rangeEnd) - 1  # seems to add a frame
            if (rangeEnd - rangeStart) > 1:
                startTime = rangeStart
                endTime = rangeEnd

        # return
        return  startTime, endTime

    @classmethod
    def getHighlightedRange(cls, *args, **kwargs):
        # highlighted ranges
        rangeStart, rangeEnd = str(cmds.timeControl(mel.eval('$tmpVar=$gPlayBackSlider'), query=True, range=True)).replace('"', '').split(':')
        rangeStart = float(rangeStart)
        rangeEnd = float(rangeEnd) - 1  # seems to add a frame
        if (rangeEnd - rangeStart) > 1:
            return [rangeStart, rangeEnd]    
        else:
            return False
        
    @classmethod
    def removeProfile(cls, profile, *args, **kwargs):   
        # get data
        profilesData = cls.getProfilesData()
        
        # remove profile
        removed = False
        if profile in profilesData.keys():
            removed = profilesData.pop(profile, False)
        
        # store data
        if removed:
            cls.setProfilesData(profilesData)
        
    
    @classmethod
    def newProfile(cls, profile, data, *args, **kwargs):   
        # copy attributes
        profile = str(profile)
        data = copy.deepcopy(data)
        
        # set active profile
        cls.setActiveProfile(profile)      
        
        # append to profile data
        profilesData = cls.getProfilesData()  
        try:
            profilesData[profile]
        except:
            profilesData[profile] = {}
        # set data
        profilesData[profile]['data'] = data
        profilesData[profile]['version'] = Functions.getVersion()
        # store to memory
        cls.setProfilesData(profilesData)
        
    @classmethod
    def getProfiles(cls):
        profilesData = cls.getProfilesData()
        return profilesData.keys()
    
    @classmethod
    def setActiveProfile(cls, profile):
        cls.activeProfile = str(profile)

    @classmethod
    def getActiveProfile(cls):
        try:
            cls.activeProfile
        except Exception, e:
            cls.activeProfile = 'default'       
        return cls.activeProfile    
    
    @classmethod
    def setProfilesData(cls, data):
        cls.profilesData = copy.deepcopy(data)

    @classmethod
    def getProfilesData(cls):
        try:
            cls.profilesData
        except:
            cls.profilesData = {}
        # make sure a default profile is in there
        if 'default' not in cls.profilesData.keys():
            cls.profilesData['default'] = {}
            cls.profilesData['default']['data'] = [] 
        return copy.deepcopy(cls.profilesData)

    @classmethod
    def groupDuplicates(cls, values, *args, **kwargs): 
        #
        if not values:
            return False

        """
        from itertools import groupby
        L = [0, 0, 0, 3, 3, 2, 5, 2, 6, 6]
        grouped_L = [(k, sum(1 for i in g)) for k,g in groupby(L)]
        grouped_L
        >>
          [(0, 3), (3, 2), (2, 1), (5, 1), (2, 1), (6, 2)]
        
        """
        return [(k, sum(1 for i in g)) for k, g in groupby(values)]

    @classmethod
    def cleanSubframeKeys(cls, *args, **kwargs): 
        # pull variables
        selection = False
        if 'selection' in kwargs:
            selection = kwargs.pop('selection')             
        
        # confirm with user
        count = 0
        if selection:
            count = len(selection)
        message = 'Clean Subframe Keys for {0} Objects?'.format(count)
        confirm = cmds.confirmDialog(title='Clean Subframe Keys?', message=message, button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if confirm == 'Yes':
 
    
            if not selection:
                return False
            
            # add shapes to the selection list
            checkShapes = cmds.listRelatives(selection, shapes=True, fullPath=True)
            if checkShapes:
                selection += checkShapes
            
            # add connections
            selection = list(set(selection))
            #print 546, selection
            connections = cmds.listConnections(selection,  d=False, s=True)
            if connections:
                connections = list(set(connections))
                selection += connections
           
            # setup
            selection = list(set(selection))
            selectedChannels = False #done bother with this
            #selectedChannels = cls.getSelectedChannels(selection=selection)
            removalStats = {}
            removalStats['keysCleaned'] = 0
    
            # prep progress bar
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
            cmds.progressBar( gMainProgressBar,
                                edit=True,
                                beginProgress=True,
                                isInterruptable=True,
                                status='whisKEY Processing...',
                                maxValue=len(selection) )
            
            
            # nodes
            try:
                for s in selection:
                    #
                    cmds.progressBar(gMainProgressBar, edit=True, step=1)
                    if not cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
                        #
                        if cmds.keyframe(s, query=True, keyframeCount=True):
                            attributes = cls.listAttributes(s, filterEnums=False)
                            # isolate selected channels
                            if selectedChannels:
                                attributes = list(set(attributes) & set(selectedChannels))
                            
                            # attributes
                            for a in attributes:
                                # long attribute name
                                attribute = '{0}.{1}'.format(s, a)
                                
                                # get curve nodes
                                curveNodes = cmds.findKeyframe(s, curve=True, at=a)
                                if curveNodes:
                                    for curveNode in curveNodes:
                                        timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                                        # if there are keys:
                                        if timesValues: 
                                        
                                            # breakdown lists
                                            times = []
                                            values = []
                                            wholeTimes = set()
                                            subframeTimes = set()
                                            for t, v in timesValues:
                                                times.append(t)
                                                wholeTimes.add(int(float(t) + 0.5))
                                                values.append(v)
                                                if not float(t).is_integer():
                                                    subframeTimes.add(t)
                                                    removalStats['keysCleaned'] += 1
                                                    
                                            
                                            # diff a list of times that need keyframes set
                                            newTimes = list(wholeTimes - set(times))
                                            for t in newTimes:
                                                cmds.setKeyframe(curveNode, insert=True, time=tuple([t, t]))
                                            
                                            # remove subframe keys
                                            for t in  subframeTimes:
                                                cmds.cutKey(curveNode, time=tuple([t, t]))
            except:
                pass
            finally:
                # finish progress
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

            # print stats
            print 'ebLabs_whisKEY:Clean Subframe Keys Info:', removalStats                    
                                
    @classmethod
    def removeBoringKeys(cls, *args, **kwargs): 
        # pull variables
        selection = False
        if 'selection' in kwargs:
            selection = kwargs.pop('selection')        
        regions = False
        if 'regions' in kwargs:
            regions = kwargs.pop('regions')        
        
        if not selection:
            return False
        
        # confirm with user
        count = 0
        selectedChannels = False
        count = len(selection)
        selectedChannels = cls.getSelectedChannels(selection=selection)  
                  
        message = []
        message += ['Remove Boring Keys for {0} Objects?'.format(count)]   
        if selectedChannels:
            message += ['Using selected channels, [{0}]'.format('], ['.join(selectedChannels))]      
        confirm = cmds.layoutDialog(ui=partial(cls.removeBoringKeysPrompt, '\n'.join(message)))
        
        if 'True' in confirm:
            
            # setup options
            leaveFirstKey = ''
            if confirm == 'TrueLeaveFirst':
                leaveFirstKey = True
            elif confirm == 'TrueLeaveNone':
                leaveFirstKey = False
               
            # setup
            removalStats = {}
            removalStats['keysRemoved'] = 0
            
            # prep progress bar
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
            cmds.progressBar( gMainProgressBar,
                                edit=True,
                                beginProgress=True,
                                isInterruptable=True,
                                status='whisKEY Processing...',
                                maxValue=len(selection) )
            
            # nodes
            try:
                for s in selection:
                    # progress bar
                    cmds.progressBar(gMainProgressBar, edit=True, step=1)
                    if not cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
                        
                        # attributes
                        attributes = cls.listAttributes(s, filterEnums=False)
                        # isolate selected channels
                        if selectedChannels:
                            attributes = list(set(attributes) & set(selectedChannels))
                        
                        # attributes
                        for a in attributes:
                            # long attribute name
                            attribute = '{0}.{1}'.format(s, a)
                            
                            # get curve nodes
                            curveNodes = cmds.findKeyframe(s, curve=True, at=a)
                            if curveNodes:
                                for curveNode in curveNodes:
                                    timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                                    
                                    # breakdown lists
                                    times = []
                                    values = []
                                    for t, v in timesValues:
                                        times.append(t)
                                        values.append(v)
                                    
                                    # group duplicates
                                    groupedValues = cls.groupDuplicates(values)
                                            
                                    # for the case when ALL the keys are boring
                                    if len(groupedValues) == 1:
                                        if leaveFirstKey:
                                            # just keep first key
                                            if len(times) == 1:
                                                # just one key, leave it
                                                pass
                                            else:
                                                # cut everything after the first key
                                                secondKey = times[1]
                                                lastKey = times[-1]
                                                cmds.cutKey(curveNode, time = (secondKey, lastKey))
                                        else:
                                            cmds.cutKey(curveNode)
                                    
                                    # remove boring sections
                                    else:
                                        # set fixed tangents for bookends of boring sections, generate list of frames to delete
                                        index = 0  # first loop will ADD and inxex will become 0 based 
                                        previousGroupWasBoring = False
                                        indicesForRemoval = []
                                        for value, count in  groupedValues:
                                            # sync index
                                            countRange = range(count)
                                            for c in countRange:
                                                # set fixed tangents for firsts
                                                if c == 0:
                                                    if previousGroupWasBoring or count > 1:
                                                        cmds.keyTangent(curveNode, edit=True, inTangentType='fixed', outTangentType='fixed', index=(index, index))
                
                                                # after first in group AND there is two or more in boring group
                                                if count >= 2 and c >= 1:
                                                    # also skip the last item in the group
                                                    if c < countRange[-1]:
                                                        indicesForRemoval.append(index)
                                                # 
                                                index += 1
                                                        
                                            # history tracking
                                            if count > 1:
                                                previousGroupWasBoring = True
                                            else:
                                                previousGroupWasBoring = False
                                        
                                        # cut indices
                                        for i in sorted(indicesForRemoval, reverse=True):
                                            cmds.cutKey(curveNode, index=tuple([i, i]))
                                        
                                        # remove remaining keys if only one left
                                        if not leaveFirstKey:
                                            timesValues = [] 
                                            try:
                                                timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                                            except:
                                                pass
                                            if timesValues and len(timesValues) == 1:
                                                cmds.cutKey(curveNode)
                                            
                                        # stats
                                        removalStats['keysRemoved'] += len(indicesForRemoval)
            except:
                pass
            finally:
                # finish progress
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
            
            # print stats
            print 'ebLabs_whisKEY:Remove Boring Keys Info:', removalStats
    
    @classmethod
    def removeBoringKeysPrompt(cls, message):
        # Get the dialog's formLayout.
        form = cmds.setParent(query=True)
        cmds.formLayout(form, e=True, width=300)
        
        # message text
        text = cmds.text(l=message)
        
        checkbox = cmds.checkBox( label='Leave first keys?', value=True )

        def dismiss(value, *args, **kwargs):
            #add in checkbox info
            if value == 'True':
                checkboxValue = cmds.checkBox(checkbox, query=True, value=True )
                if checkboxValue:
                    value = 'TrueLeaveFirst'
                else:
                    value = 'TrueLeaveNone'
            cmds.layoutDialog( dismiss=value )        
        
        # buttons
        trueButton = cmds.button(l='Yes', c=partial(dismiss, 'True') )
        falseButton = cmds.button(l='No', c=partial(dismiss, 'Cancel') )
        
        padding = 10
        
        cmds.formLayout(form, edit=True, attachForm=[(text, 'top', padding)])
        cmds.formLayout(form, edit=True, attachForm=[(text, 'left', 0)])
        cmds.formLayout(form, edit=True, attachNone=[(text, 'bottom')])
        cmds.formLayout(form, edit=True, attachForm=[(text, 'right', 0)])
        
        cmds.formLayout(form, edit=True, attachControl=[(checkbox, 'top', padding, text)])
        cmds.formLayout(form, edit=True, attachForm=[(checkbox, 'left', padding)])
        cmds.formLayout(form, edit=True, attachNone=[(checkbox, 'bottom')])
        cmds.formLayout(form, edit=True, attachForm=[(checkbox, 'right', 0)])

        cmds.formLayout(form, edit=True, attachControl=[(falseButton, 'top', padding, checkbox)])
        cmds.formLayout(form, edit=True, attachForm=[(falseButton, 'left', padding)])
        cmds.formLayout(form, edit=True, attachNone=[(falseButton, 'bottom')])
        cmds.formLayout(form, edit=True, attachPosition=[(falseButton, 'right', padding, 50)])     

        cmds.formLayout(form, edit=True, attachControl=[(trueButton, 'top', padding, checkbox)])
        cmds.formLayout(form, edit=True, attachControl=[(trueButton, 'left', padding, falseButton)])
        cmds.formLayout(form, edit=True, attachNone=[(trueButton, 'bottom')])
        cmds.formLayout(form, edit=True, attachForm=[(trueButton, 'right', padding)])
        
    


    @classmethod
    def getAttributeType(cls, controlObject, attribute):
        if cmds.objExists(controlObject):
            # enum
            if attribute in cmds.attributeInfo(controlObject, enumerated=True):
                return 'enum'
            # bool
            if attribute in cmds.attributeInfo(controlObject, bool=True):
                return 'bool'
            # number, other
            if attribute in cmds.attributeInfo(controlObject, allAttributes=True):
                return 'other'
        # else
        return False

    @classmethod
    def findMatchingObjectsInNamespace(cls, *args, **kwargs): 
        # pull variables
        node = False
        if 'node' in kwargs:
            node = kwargs.pop('node')   
        namespaces = False
        if 'namespaces' in kwargs:
            namespaces = kwargs.pop('namespaces') 
        
        # setup
        matchingNodes = []
        nodeNamespace = Functions.getNamespaces(nodes=[node])[0]
        
        #   
        for ns in namespaces:
            potentialNode = node.replace(nodeNamespace, ns)
            if cmds.objExists(potentialNode):
                matchingNodes.append(potentialNode)
        return matchingNodes
    
    @classmethod
    def getNamespaces(cls, *args, **kwargs):
        # pull variables
        nodes = False
        if 'nodes' in kwargs:
            nodes = kwargs.pop('nodes')        
        #
        # build list of namespaces
        namespaces = []        
        if nodes:

            for n in nodes:
                # split up bars |, and return last
                n = n.split('|')[-1]
        
                # split up colons : remove last
                n = n.split(':')
                del n[-1]
        
                # add back in : colons
                n = ':'.join(n)  # + ':'
        
                # add to namespace list
                namespaces.append(n)
        #
        return namespaces
    
    @classmethod
    def setKeyType(cls, keyType, *args, **kwargs):  
        
        # setup
        outTangent = keyType
        inTangent = keyType
        selection = cmds.ls(sl=True)
        
        
        # set types
        if (keyType == 'auto' or keyType == 'spline' or keyType == 'clamped' or keyType == 'step' or keyType == 'linear' or keyType == 'flat' or keyType == 'plateau'):
            # override for stepped
            if(inTangent == 'step'):
                inTangent = 'linear'
            
            # set global tangents
            #cmds.keyTangent(g=True, edit=True, inTangentType=inTangent)
            #cmds.keyTangent(g=True, edit=True, outTangentType=outTangent)
            '''
            this needs to be MEL
            '''
            mel.eval('keyTangent -global -itt {0};'.format(inTangent))
            mel.eval('keyTangent -global -ott {0};'.format(outTangent))
            
            # set tangents on selection
            if selection:
                cmds.keyTangent(selection, outTangentType=outTangent)
                if inTangent != 'step':
                    cmds.keyTangent(selection, inTangentType=inTangent)
        elif keyType == 'free':
            # set global tangent type
            cmds.keyTangent(g=True, edit=True, weightedTangents=True)
            
            # set keys on selection object
            if selection:
                cmds.keyTangent(selection, animation='objects', edit=True, weightedTangents=True)
                cmds.keyTangent(selection, animation='objects', edit=True, weightLock=False)
        
        # set global tangent types


    @classmethod
    def listAttributes(cls, node, *args, **kwargs):    
        # pull variables
        filterEnums = True
        if 'filterEnums' in kwargs:
            filterEnums = kwargs.pop('filterEnums')
        
        # setup
        attributes = []
        
        # get attributes
        keyableAttributes = cmds.listAttr(node, keyable=True, unlocked=True, scalar=True, visible=True, shortNames=True)
        if keyableAttributes:
            for a in keyableAttributes:
                try:
                    # get long name
                    # a = cmds.attributeQuery(a, node=node, ln=True)
                    
                    # check types
                    isEnum = False
                    if cmds.attributeQuery(a, node=node, enum=True):
                        isEnum = True
                    
                    # filter types
                    if filterEnums and isEnum:
                        continue

                except:
                    pass
                

                #
                attributes.append(a)
        # 
        return attributes
    
    @classmethod
    def getRelativePosition(cls, node, attribute, time, *args, **kwargs):
        # get list of all key indicies
        allKeys = cmds.keyframe(node, query=True, at=attribute)
        if allKeys:
            allKeys = sorted(allKeys)
            firstKeytime = allKeys[0]
            lastKeyTime = allKeys[-1]
            
            # check position
            if time == firstKeytime:
                relativePosition = 'First'
                return relativePosition
            elif time == lastKeyTime:
                relativePosition = 'Last'
                return relativePosition        
            elif time < firstKeytime:
                relativePosition = 'Before'
                return relativePosition 
            elif time > lastKeyTime:
                relativePosition = 'After'
                return relativePosition 
            # do this check last
            elif time in allKeys:
                relativePosition = 'OnKey'
                return relativePosition
            else:
                relativePosition = 'InKeys'
                return relativePosition
    
    @classmethod
    def getKeyFrameAtOffsetInfo(cls, node, attribute, offset, *args, **kwargs):
        # global proc float ebLabs_whisKEY2_beforeAfterKeyFrameNumber(string $object, string $attribute, int $check)
        #
        offsetTime = False
        offsetValue = False
        
        # get current time
        currentFrame = cmds.currentTime(query=True)
        
        # relative position
        '''
        'Before', 'First','OnKey', 'InKeys', 'Last', 'After'
        '''
        relativePosition = Functions.getRelativePosition(node, attribute, currentFrame)

        # all keys
        sourceKeys = cmds.keyframe(node, query=True, at=attribute)
        referenceKeys = list(sourceKeys)
        if currentFrame not in referenceKeys:
            referenceKeys.append(currentFrame)
            referenceKeys = sorted(referenceKeys)
        
        # get current key index from referenceKey list
        currentKeyIndex = referenceKeys.index(currentFrame)
        
        # get offset value from referenceKey list
        indexLookup = currentKeyIndex + offset
        indexLookup = int(Functions.clamp(indexLookup, 0, len(referenceKeys) - 1))
        offsetTime = referenceKeys[indexLookup]
        
        # clamp offsetTime
        offsetTime = Functions.clamp(offsetTime, min(sourceKeys), max(sourceKeys))
        
        # get local key index
        localIndex = sourceKeys.index(offsetTime)
        
        # get return values
        offsetTime = cmds.keyframe(node, query=True, at=attribute, index=(localIndex, localIndex))[0]
        offsetValue = cmds.getAttr('{0}.{1}'.format(node, attribute), time=offsetTime)
        
        #
        return offsetTime, offsetValue
    
    @classmethod
    def getBoundingBoxSize(node, *args, **kwargs):
        radius = 0
        if cmds.objExists(node):
            # get object type
            objectType = cmds.objectType(node)
            # get bounding box radius
            if objectType == 'joint':
                radius = cmds.getAttr(node + '.radius') * 2
            else:
                boundingBox = cmds.exactWorldBoundingBox(node, ignoreInvisible=True)
                dimensions = [abs(boundingBox[0] - boundingBox[3]), abs(boundingBox[1] - boundingBox[4]), abs(boundingBox[2] - boundingBox[5])]
                radius = sum(dimensions) / 3
        # error check small results
        if radius > 0.0001:
            return radius
        else:
            return 1   
    
    @classmethod
    def getAverageBoundingBoxSize(cls, nodes, *args, **kwargs):
        averageSize = False
        if nodes:
            averageSize = 0
            runningSum = 0
            for n in nodes:
                runningSum += cls.getBoundingBoxSize(n)
            averageSize = runningSum / len(nodes)
        return averageSize

    @classmethod
    def getActiveCamera(cls, *args, **kwargs):
        # camera info
        modelPanel = cmds.getPanel(withFocus=True)
        cameraName = None
        cameraShape = None
        isCameraPanel = False
        try:
            cameraName = cmds.modelEditor(modelPanel, query=True, camera=True)
            if cmds.objectType(cameraName) == 'transform':
                shapeCheck = cmds.listRelatives(cameraName, shapes=True, fullPath=True)[0]
                if cmds.objectType(shapeCheck) == 'camera':
                    cameraShape = shapeCheck

            elif cmds.objectType(cameraName) == 'camera':
                cameraShape = cameraName
                cameraName = cmds.listRelatives(cameraShape, parent=True, fullPath=True)[0]

            if cmds.objectType(cameraShape) == 'camera':
                isCameraPanel = True
                # cameraName = cameraName.split('|')[-1]
        except:
            pass
        #
        return cameraName

    @classmethod
    def setVersion(cls, version):
        cls.version = version

    @classmethod
    def getVersion(cls):
        return cls.version

    @classmethod
    def loadDataFromFile(cls, filename, *args, **kwargs):
        data = None
        try:
            filePath = open(filename, 'r')
            data = json.loads(filePath.read())
            filePath.close()
        except:
            pass
        return data

    @classmethod
    def writeDataToFile(cls, filePath, dictionary):
        filePathRoot = os.path.split(filePath)[0]
        if not os.path.exists(filePathRoot):
            os.makedirs(filePathRoot)

        fileObject = open(filePath, 'w')
        data = json.dumps(dictionary, sort_keys=True, indent=4)
        fileObject.write(data)
        fileObject.close()

    @classmethod
    def clearPrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')  
        
        # clear active profile
        profilesData = cls.getProfilesData()
        profilesData[profile] = {}
        cls.setProfilesData(profilesData)
        
        # store data
        widgetData = []
        cls.storePrefs(widgetData, profile=profile)
        # overwrite data with nothing
        # cls.writeDataToFile(cls.prefsFilepath, profilesData)

    @classmethod
    def retreivePrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')  
        
        # get prefs from file
        try:
            # get active profile
            data = cls.loadDataFromFile(cls.prefsFilepath)
            # get data and store to FUNCTIONS
            activeProfile = data['activeProfile']
            if profile:
                activeProfile = profile
            profilesData = data['data']            
            cls.setActiveProfile(activeProfile)
            cls.setProfilesData(profilesData)
            # get data for return
            widgetData = profilesData[activeProfile]['data']
            version = profilesData[activeProfile]['version']
            return version, widgetData
        except:
            return False, False

    @classmethod
    def storePrefs(cls, widgetData, *args, **kwargs):
        command = partial(cls.storePrefs_deferred, widgetData)
        cmds.evalDeferred(command)

    @classmethod
    def storePrefs_deferred(cls, widgetData, *args, **kwargs):
        profile = cls.getActiveProfile()
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')        
        # get all prefs
        profilesData = cls.getProfilesData()
        
        # store prefs to data file
        try:
            profilesData[profile]
        except:
            profilesData[profile] = {}
        try:
            profilesData[profile]['data']
        except Exception, e:
            print 868, e
            print 863, 'profilesData', type(profilesData), profilesData
            print 863, 'profilesData[profile]', type(profilesData[profile]), profilesData[profile]
            print 864, 'profile', type(profile), profile
            profilesData[profile]['data'] = {}  
        # set data and version per profile
        profilesData[profile]['data'] = widgetData
        profilesData[profile]['version'] = cls.getVersion()
        
        # store data internally as well
        cls.setProfilesData(profilesData)
        
        # store data
        data = {}
        data['data'] = profilesData
        data['version'] = cls.getVersion()
        data['activeProfile'] = profile
        
        # write data
        cls.writeDataToFile(cls.prefsFilepath, data)

    @classmethod
    def worldToLocalPoint(cls, point, node):
        matrix = cmds.getAttr (node + ".parentInverseMatrix")
        localPointX = (point[0] * matrix[0]) + (point[1] * matrix[4]) + (point[2] * matrix[8]) + matrix[12]
        localPointY = (point[0] * matrix[1]) + (point[1] * matrix[5]) + (point[2] * matrix[9]) + matrix[13]
        localPointZ = (point[0] * matrix[2]) + (point[1] * matrix[6]) + (point[2] * matrix[10]) + matrix[14]
        return [localPointX, localPointY, localPointZ]

    @classmethod
    def decompMatrix(cls, node, matrix):
        '''
        Decomposes a MMatrix in new api. Returns an list of translation,rotation,scale in world space.
        '''
        # Rotate order of object
        rotOrder = cmds.getAttr('{0}.rotateOrder'.format(node))
        
        # Puts matrix into transformation matrix
        mTransformMtx = OpenMaya.MTransformationMatrix(matrix)
        
        # Translation Values
        trans = mTransformMtx.translation(OpenMaya.MSpace.kWorld)
        
        # Euler rotation value in radians
        eulerRot = mTransformMtx.rotation()
        
        # Reorder rotation order based on ctrl.
        eulerRot.reorderIt(rotOrder)
        
        # Find degrees
        angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]
        
        # Find world scale of our object.
        scale = mTransformMtx.scale(OpenMaya.MSpace.kWorld)
        
        # Return Values
        return [trans.x, trans.y, trans.z] + angles + scale

    @classmethod
    def rekeyOnKeys(cls, *args, **kwargs):
        # pull variables
        objects = None
        if 'objects' in kwargs:
            objects = kwargs.pop('objects')
        matchLast = False
        if 'matchLast' in kwargs:
            matchLast = kwargs.pop('matchLast')
        
        # safe suspend
        try:
            if objects:
                # get current time
                currentTime = cmds.currentTime(query=True)    
                
                # get highlighted channels
                highlightedChannels = Functions.getSelectedChannels()
                if not highlightedChannels:
                    highlightedChannels = None #need to be None to work with maya commands, false doesnt work
                
               
                # collect some info
                specialKeyTimeTemplateObjects = objects
                keyTimeTemplateObjects = objects
                
                # match last overrides
                if matchLast:
                    specialKeyTimeTemplateObjects = objects[-1:]
                    keyTimeTemplateObjects = objects[-1:]
                
                # get special key ticks
                specialKeyTickTimes = cls.getSpecialKeyTickTimes(objects=specialKeyTimeTemplateObjects)
                
                # get list of keytimes for keying
                keyTimes = [] 
                keyTimes = cmds.keyframe(keyTimeTemplateObjects, query=True, attribute=highlightedChannels)
                if keyTimes:
                    keyTimes = list(set(keyTimes))
                
                # get all keytimes
                '''
                use all channels for this part
                '''
                allKeyTimes = []
                allKeyTimes = cmds.keyframe(objects, query=True, attribute=None)
                if allKeyTimes:
                    allKeyTimes = list(set(allKeyTimes))
    
                # set scope of keying
                objectsToProcess = objects
                if matchLast:
                    '''
                    allow for cleaning up keys on a single object
                    '''
                    if objectsToProcess and len(objectsToProcess)==1:
                        objectsToProcess = objects
                    else:
                        objectsToProcess = objects[:-1]
    
                # get highlighted frame range
                highlightedRange = cls.getHighlightedRange()
                if highlightedRange:
                    # trim keytimes
                    trimmed = []
                    for f in keyTimes:
                        if highlightedRange[0] <= f <= highlightedRange[1]:
                            trimmed.append(f)
                    keyTimes = sorted(trimmed)
                
                # disable view
                cls.suspendUI(True)
                
                # set keys
                for f in keyTimes:
                    # go to time, set keyframe
                    cmds.currentTime(f, edit=True)
                    
                    # matchLast overrides
                    if matchLast or not highlightedChannels:
                        '''
                        for matchlast when channels are highlighted, 
                        just use the highlighed channels for defining what the key times to set are,
                        however, set keys for all the obj attributes 
                        '''
                        cmds.setKeyframe(objectsToProcess)
                    else:
                        cmds.setKeyframe(objectsToProcess, attribute=highlightedChannels)
                
                # set special keyTick colors
                for f in specialKeyTickTimes:
                    cmds.keyframe(objectsToProcess, time=(f, f), tickDrawSpecial=True, animation='objects',  attribute=highlightedChannels)
    
                # remove keys if nessasary
                if matchLast:
                    for f in allKeyTimes:
                        if f not in keyTimes:
                            '''
                            use all channels for this part
                            '''
                            cmds.cutKey(objectsToProcess, time=(f, f), clear=True)
                
                # return to previous time
                cmds.currentTime(currentTime, edit=True)
        #
        finally:
            # enable view
            # cls.enableMayaUI(setState=True, ignoreWindow=window.window, method='suspend')
            cls.suspendUI(False)

    @classmethod
    def getSpecialKeyTickTimes(cls, *args, **kwargs):
        # pull variables
        objects = None
        if 'objects' in kwargs:
            objects = kwargs.pop('objects')
        
        if objects:
            # setup
            specialKeyTicks = []

            # iterate through objects
            for s in objects:
                keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)

                # go through attributes
                for a in keyableAttributes:
                    # get info about attributes
                    attribute = '{0}.{1}'.format(s, a)

                    # check if there are any existing keys
                    keyframeCount = cmds.keyframe(attribute, query=True)
                    if keyframeCount:
                        curveNode = cmds.keyframe(attribute, query=True, name=True)[0]
                        keyFrameList = cmds.keyframe(curveNode, query=True)

                        # check through unchecked frames for special key ticks
                        uncheckedFrames = list(set(keyFrameList) - set(specialKeyTicks))
                        for f in uncheckedFrames:
                            index = keyFrameList.index(f)
                            querySpecialKeyTick = cmds.getAttr('{0}.kyts[{1}]'.format(curveNode, index))
                            if querySpecialKeyTick:
                                specialKeyTicks.append(f)
            # return
            return specialKeyTicks

    @classmethod
    def setKeyframe(cls, *args, **kwargs):
        # pull variables
        objects = None
        if 'objects' in kwargs:
            objects = kwargs.pop('objects')
        special = None
        if 'special' in kwargs:
            special = kwargs.pop('special')
        useHighlighted = True
        if 'useHighlighted' in kwargs:
            useHighlighted = kwargs.pop('useHighlighted')            

        # set useHighlighted
        highlightedChannels = False
        if useHighlighted:
            highlightedChannels = Functions.getSelectedChannels(objects)
        
        # set keyframe
        if objects:
            if highlightedChannels:
                cmds.setKeyframe(objects, attribute = highlightedChannels)
            else:
                cmds.setKeyframe(objects)
        
        # set special key tick color
        if special:
            currentTime = cmds.currentTime(query=True)
            cmds.keyframe(objects, time=(currentTime, currentTime), tickDrawSpecial=True, animation='objects')

    @classmethod
    def validateText(cls, text, *args, **kwargs):
        if not text:
            return False
        validCharacters = "-_.(){0}{1}".format(string.ascii_letters, string.digits)
        validatedCharacters = []
        for c in text:
            # replace space with underscore
            if c == ' ':
                c = '_'
            # filter non valid characters
            if c in validCharacters:
                validatedCharacters.append(c)
        # return result
        validatedText = ''.join(validatedCharacters)
        return validatedText

    @classmethod
    def getStringFromUser(cls):
        # prompt user for a description
        description = False
        result = cmds.promptDialog(
            title='Enter Text',
            message='Enter Text:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel',
            text='')

        if result == 'OK':
            query = cmds.promptDialog(query=True, text=True)
            validateText = Functions.validateText(query)
            if validateText:
                description = validateText
        return description

    @classmethod
    def getDescription(cls):
        # prompt user for a description
        description = False
        result = cmds.promptDialog(
            title='Share Folder Description',
            message='Enter Description:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel',
            text='')

        if result == 'OK':
            query = cmds.promptDialog(query=True, text=True)
            validateText = Functions.validateText(query)
            if validateText:
                description = validateText
        return description

    @classmethod
    def clamp(cls, n, minn, maxn):
        return max(min(maxn, n), minn)

    @classmethod
    def getSelectedChannels(cls, selection=False):
        if not selection:
            selection = cmds.ls(sl=True, type = ['transform', 'joint'])
        if selection:
            # query channelbox
            selectedChannels = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)

            #
            if not selectedChannels:
                return None

            # fix to long names, makes it easier later on with whitelists, etc
            """
            longNames = []
            for c in selectedChannels:
                longName = cmds.attributeQuery(c, node=selection[-1], ln=True)
                longNames.append(longName)
            #
            return longNames
            """
            return selectedChannels

    @classmethod
    def suspendUI(cls, state, *args, **kwargs):
        try:
            # temporarily turn off the undo queue
            cmds.undoInfo(stateWithoutFlush=False)
            
            # playblast wrapped
            cls.suspendUI_wrapped(state, *args, **kwargs)
        except Exception, e:
            print Exception, e
            cmds.warning('Suspend UI Failed')
        finally:
            # turn undos back on
            cmds.undoInfo(stateWithoutFlush=True)        

    @classmethod
    def suspendUI_wrapped(cls, state):
        # False
        if state == True:
            try:
                # get selection
                selected = cmds.ls(sl=True)
                allPanels = cmds.getPanel(type='modelPanel')
                cmds.select(clear=True)
                
                # setup isolated object tracking
                cls.suspendIsolatedObjects = {}
                
                # go through panels
                for panel in allPanels:
                    # store per view isolated objects
                    viewSet = cmds.isolateSelect(panel, q=True, viewObjects=True)
                    setMembers = False
                    if viewSet:
                        setMembers = cmds.sets(viewSet, q=True)
                        cls.suspendIsolatedObjects[panel] = setMembers
                    
                    # isolate none
                    cmds.isolateSelect(panel, state=1)
                    
                cmds.select(selected)
                mel.eval("paneLayout -e -manage false $gMainPane")
            except Exception, e:
                print 1137, e
                cmds.warning('Suspend UI Not Activating Properly Mate.')
                mel.eval("paneLayout -e -manage true $gMainPane")
                allPanels = cmds.getPanel(type='modelPanel')
                for panel in allPanels:
                    cmds.isolateSelect(panel, state=False)

        # True
        if state == False:
            mel.eval("paneLayout -e -manage true $gMainPane")
            allPanels = cmds.getPanel(type='modelPanel')
            for panel in allPanels:
                # restore panel
                cmds.isolateSelect(panel, state=False)
                
                # restore previous state
                try:
                    if panel in cls.suspendIsolatedObjects.keys():
                        if cls.suspendIsolatedObjects[panel]:
                            cmds.isolateSelect(panel, state=True)
                            for n in cls.suspendIsolatedObjects[panel]:
                                cmds.isolateSelect(panel, addDagObject=n)
                except Exception, e:
                    print 1292, e


    """
    @classmethod
    def enableMayaUI(cls, **kwargs):
        '''
        cls.enableMayaUI(setState = False, ignoreWindow = window.window, method = 'disable' )
        '''
        #
        setState = True
        if 'setState' in kwargs:
            setState = kwargs.pop('setState')
        ignoreWindow = ''
        if 'ignoreWindow' in kwargs:
            ignoreWindow = kwargs.pop('ignoreWindow')
        method = 'disable'
        if 'method' in kwargs:
            method = kwargs.pop('method')

        '''
        About the method toggle:
        'suspend' setting is fast, but might prevent maya from updating nodes. This may or not be a problem.
        'disable' is another method of hiding mayas viewports while processing, allows for all nodes to be evaluated properly
        'isolate' beta, isolating NONE in all views
        '''

        # set window name
        windowName = 'ebLabs UI Restore'

        def toggleUI(setState, ignoreWindow, method, *args):
            # toggle  UI
            windowName = 'ebLabs_UIFIX'
            if method == 'suspend':
                cmds.refresh(suspend=not setState)
            elif method == 'disable':
                windows = cmds.lsUI(type='window')
                gMainPane = mel.eval('global string $gMainPane; $ebLabs_spaces_temp = $gMainPane;')
                for window in windows:
                    if window != "MayaWindow" and window != "CommandWindow" and window != ignoreWindow and window != windowName:
                        try:
                            cmds.window(window, edit=True, iconify=(not setState))
                        except:
                            pass
                cmds.paneLayout(gMainPane, edit=True, manage=setState)
            elif method == 'isolate':
                modelPanels = cmds.getPanel(type='modelPanel')
                cmds.select(clear=True)
                for modelPanel in modelPanels:
                    try:
                        cmds.isolateSelect(modelPanel, state=(not setState))
                    except:
                        pass

            if setState:
            # remove UI
                if (cmds.window(windowName, exists=True)):
                    cmds.deleteUI(windowName, window=True)
                if(cmds.windowPref(windowName, exists=True)):
                    cmds.windowPref(windowName, remove=True)
                # force a refresh
                cmds.currentTime(cmds.currentTime(query=True))

        def safetyPopup(setState, ignoreWindow, method):
            # clear any remaining UIs before launching a new one
            windowName = 'ebLabs_UIFIX'
            if (cmds.window(windowName, exists=True)):
                cmds.deleteUI(windowName, window=True)
            if(cmds.windowPref(windowName, exists=True)):
                cmds.windowPref(windowName, remove=True)

            # launch the popup
            window = cmds.window(windowName, widthHeight=(200, 100), title='ebLabs UI Restore')
            cmds.columnLayout(adjustableColumn=True)
            cmds.text(label='\nSomethings Broken\n\nClick to restore UI, \nif there are any errors\n')
            cmds.button(label='RestoreUI', c=partial(toggleUI, True, ignoreWindow, method))
            cmds.showWindow(window)

            # remove popup
            if setState == True:
                if (cmds.window(windowName, exists=True)):
                    cmds.deleteUI(windowName, window=True)
                if(cmds.windowPref(windowName, exists=True)):
                    cmds.windowPref(windowName, remove=True)
                # force a refresh
                cmds.currentTime(cmds.currentTime(query=True))


        # toggle UI and run safety popup
        toggleUI(setState, ignoreWindow, method)
        safetyPopup(setState, ignoreWindow, method)
    """

class widget_base:
    """ Define Common Functions for widgets
    """
    instances = []

    def __init__(self, *args, **kwargs):
        # pull args
        parent = self.getWidgetParent()

        description = 'Inbetween'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # store instance
        self.instances.append(self)

        # setup the UI
        labelVisible = False
        collapsable = False
        collapse = False
        if not expandedState:
            labelVisible = True
            collapsable = True
            collapse = True
        self.mainContainer = cmds.frameLayout(parent=parent, labelVisible=labelVisible, collapsable=collapsable, collapse=collapse)  # font = 'smallPlainLabelFont', 

        # setup frame commands
        cmds.frameLayout(self.mainContainer, edit=True, expandCommand=partial(self.expandMainContainer))

        # formatting layout
        formattingLayout = cmds.formLayout(parent=self.mainContainer)

        # inside formatting layout
        self.formLayout = cmds.formLayout(parent=formattingLayout, bgc=[0.95] * 3)
        spacerFormlayout = cmds.formLayout(parent=formattingLayout, height=2, bgc=[0.95] * 3)

        cmds.formLayout(formattingLayout, edit=True, attachForm=[(self.formLayout, 'top', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(self.formLayout, 'left', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachNone=[(self.formLayout, 'bottom')])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(self.formLayout, 'right', 0)])

        cmds.formLayout(formattingLayout, edit=True, attachControl=[(spacerFormlayout, 'top', 0, self.formLayout)])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(spacerFormlayout, 'left', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachNone=[(spacerFormlayout, 'bottom')])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(spacerFormlayout, 'right', 0)])

        # setup right click menu
        popupMenu = cmds.popupMenu(parent=self.mainContainer)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.widgetMenu, parent=popupMenu))

        # setup data containers
        self.data = {}
        self.widgetType = ''
        self.widgetState = ''

        # slider defaults
        self.enableSlider = True

    def multiplierChangeUpdateText(self, *args, **kwargs):
        sliderWidget = False
        if 'sliderWidget' in kwargs:
            sliderWidget = kwargs.pop('sliderWidget')
        element = False
        if 'element' in kwargs:
            element = kwargs.pop('element')
                    
        # format description x1.00
        value = sliderWidget.getMultiplier()
        text = "{0:.2f}x".format(value)
        
        # set text label
        self.setTextLabel(element, text)

    def setTextLabel(self, element, text, *args, **kwargs):
        # set text
        cmds.text(element, edit=True, label=text)

    @classmethod
    def addItem(cls, addItem, *args, **kwargs):
        # this is the dispatcher that calls in all the other UI elements

        # get layout parent
        parent = cls.getWidgetParent()
        
        # construct widgets
        if addItem == 'inbetween':
            newItem = widget_tween(parent=parent)
        if addItem == 'extras':
            newItem = widget_extras(parent=parent)   
        if addItem == 'worldSpace':
            newItem = widget_worldSpace(parent=parent)  
        if addItem == 'curveOptions':
            newItem = widget_curveOptions(parent=parent)   
        if addItem == 'snapshot':
            newItem = widget_snapshot(parent=parent)   
        if addItem == 'principles':
            newItem = widget_principles(parent=parent)   
        if addItem == 'classic':
            newItem = widget_classic(parent=parent)  
        if addItem == 'tools':
            newItem = widget_tools(parent=parent)    
                                       
            
        # store prefs
        cls.storePrefs()

        # resize UI
        window.resizeUI()
        
    @classmethod
    def getWidgetParent(cls, *args, **kwargs):
        try:
            cls.widgetParent
        except:
            cls.widgetParent = False
        return cls.widgetParent
    
    @classmethod
    def setWidgetParent(cls, parent, *args, **kwargs):
        cls.widgetParent = parent

    def addPostCommand(self, command, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        if command:
            self.postCommands.append(command)

    def clearPostCommands(self, *args, **kwargs):
        self.postCommands = []

    def onPost(self, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        for c in self.postCommands:
            c()

    def addPreCommand(self, command, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        if command:
            self.preCommands.append(command)

    def clearPreCommands(self, *args, **kwargs):
        self.preCommands = []

    def onPre(self, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        for c in self.preCommands:
            c()

    def addChangeCommand(self, command, *args, **kwargs):
        try:
            self.changeCommands
        except:
            self.changeCommands = []

        if command:
            self.changeCommands.append(command)

    def clearChangeCommands(self, *args, **kwargs):
        self.changeCommands = []

    def onChange(self, debug=False, *args, **kwargs):
        if debug:
            print debug, len(self.changeCommands)
        try:
            self.changeCommands
        except Exception, e:
            self.changeCommands = []

        for c in self.changeCommands:
            c()

    def rekeyOnKeys(self, *args, **kwargs):
        matchLast = False
        if 'matchLast' in kwargs:
            matchLast = kwargs.pop('matchLast')

        # get selection
        objects = self.getSelected()

        # send to rekey selection function
        Functions.rekeyOnKeys(objects=objects, matchLast=matchLast)

    def setKeyframe(self, *args, **kwargs):
        special = False
        if 'special' in kwargs:
            special = kwargs.pop('special')
        # get selection
        objects = self.getSelected()

        # set keyframe
        Functions.setKeyframe(objects=objects, special=special)

    def setKeysPopupMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        special = False
        if 'special' in kwargs:
            special = kwargs.pop('special')

        # clean up
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)

        # rekey selection
        specialString = ''
        '''
        if special:
            specialString = ' [Special Key Color]'
        '''
        cmds.menuItem(parent=parent, label='Rekey Selection' + specialString, command=partial(self.rekeyOnKeys))
        cmds.menuItem(parent=parent, label='Rekey To Match Last Selected' + specialString, command=partial(self.rekeyOnKeys, matchLast=True))

    def expandMainContainer(self, *args, **kwargs):
        #
        cmds.frameLayout(self.mainContainer, edit=True, labelVisible=False, collapsable=False, collapse=False)

        # resize UI
        window.resizeUI()

        # store prefs
        self.storePrefs()

    def moveWidget(self, direction, *args, **kwargs):
        # get current index
        index = self.getInstanceIndex()
        
        # number of instances
        instances = self.getInstances()
        instancesCount = len(instances)
        
        # figure out new index position
        newIndex = int(Functions.clamp(index + direction, 0, instancesCount))
        
        # remove instance
        popped = instances.pop(index)
        
        # add back in 
        instances.insert(newIndex, popped)
        
        # push back instance data
        self.setInstances(instances)
        
        #store prefs
        self.storePrefs()
        
        # rebuild 
        currentProfile = Functions.getActiveProfile()
        self.switchToProfile(currentProfile)

    def collapseMainContainer(self, *args, **kwargs):
        #
        cmds.frameLayout(self.mainContainer, edit=True, labelVisible=True, collapsable=True, collapse=True)

        # resize UI
        window.resizeUI()

        # store prefs
        self.storePrefs()

    def getWidgetExpandedState(self, *args, **kwargs):
        state = cmds.frameLayout(self.mainContainer, query=True, collapse=True)
        return not state

    def getInstanceIndex(self, *args, **kwargs):
        index = self.instances.index(self)
        return index

    def widgetMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')

        # clean up
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)

        # get widget name
        description = self.getDescription()

        # tools
        toolsSubmenu = cmds.menuItem(parent=parent, subMenu=True, label='Tools')
        cmds.menuItem(parent=toolsSubmenu, label='Rekey Selection', command=partial(self.rekeyOnKeys))
        cmds.menuItem(parent=toolsSubmenu, label='Rekey To Match Last Selected', command=partial(self.rekeyOnKeys, matchLast=True))
        cmds.menuItem(parent=toolsSubmenu, divider=True)
        cmds.menuItem(parent=toolsSubmenu, label='Clean Subframe Keys', command=partial(self.cleanSubframeKeys))
        cmds.menuItem(parent=toolsSubmenu, label='Remove Boring Keys', command=partial(self.removeBoringKeys, regions=False))
        cmds.menuItem(parent=toolsSubmenu, divider=True)
        # smashbake
        startTime, endTime = Functions.queryTimeRange()
        selected = cmds.ls(sl=True)
        label = 'Smash Bake: {0}-{1}'.format(startTime, endTime)
        cmds.menuItem(parent=toolsSubmenu, label=label, command=partial(Functions.smashBaker, selected, startTime, endTime))
        
        # cmds.menuItem(parent=toolsSubmenu, label='Remove Boring Key Sections', command = partial(self.removeBoringKeys, regions=True))

        profilesMenu = cmds.menuItem(parent=parent, subMenu=True, label='Profiles')        
        cmds.menuItem(profilesMenu, edit=True, postMenuCommand=partial(self.profilesMenuPostCommand, parent=profilesMenu))
        
        # add widgets
        # addWidgetsSubmenu = cmds.menuItem(parent = parent, subMenu=True, label='Add Widget')
        # cmds.menuItem(parent = addWidgetsSubmenu, label='Add Inbetween Widget', command=partial(self.addItem, 'inbetween'))
        # cmds.menuItem(divider=True)

        # info
        widgetCollapseState = self.getWidgetExpandedState()
        cmds.menuItem(parent=parent, label='/\\ (move up)', command=partial(self.moveWidget, -1))
        cmds.menuItem(parent=parent, label='\\/ (move down)', command=partial(self.moveWidget, 1))
        cmds.menuItem(parent=parent, label='Collapse Widget', command=partial(self.collapseMainContainer), enable=widgetCollapseState)
        cmds.menuItem(parent=parent, divider=True)
        
        # add
        addWidgetsSubmenu = cmds.menuItem(parent=parent, subMenu=True, label='Add Widget')
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Classic Widget', command=partial(self.addItem, 'classic'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Inbetween Widget', command=partial(self.addItem, 'inbetween'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add World Space Widget', command=partial(self.addItem, 'worldSpace'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Extras Widget', command=partial(self.addItem, 'extras'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Snapshot Widget', command=partial(self.addItem, 'snapshot'))
        cmds.menuItem(parent=addWidgetsSubmenu, divider=True)
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Tools Widget', command=partial(self.addItem, 'tools'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Options Widget', command=partial(window.addItem, 'curveOptions'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Animation Principles', command=partial(window.addItem, 'principles'))        
        # remove
        cmds.menuItem(parent=parent, label='Remove Widget: ' + description, command=partial(self.removeWidget))

        # advanced
        cmds.menuItem(parent=parent, divider=True)
        advancedSubmenu = cmds.menuItem(parent=parent, subMenu=True, label='Advanced')
        cmds.menuItem(parent=advancedSubmenu, label='Resize UI', command=partial(window.resizeUI))
        activeProfile = Functions.getActiveProfile()
        cmds.menuItem(parent=advancedSubmenu, label='Reset "{0}" Prefs'.format(activeProfile), command=partial(window.resetPrefs, profile=activeProfile))
        cmds.menuItem(parent=advancedSubmenu, label='Print Widget Info', command=partial(self.printInfo))
      
    def profilesMenuPostCommand(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')

        # clean up
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)

        # New Profile
        cmds.menuItem(parent=parent, label='New Profile', command=partial(self.createNewProfile))
        cmds.menuItem(parent=parent, divider=True)
        
        # switch to profile
        currentProfile = Functions.getActiveProfile()
        profiles = Functions.getProfiles()
        for p in profiles:
            cmds.menuItem(parent=parent, label='Switch To: ' + p, enable=not (p == currentProfile), command=partial(self.switchToProfile, p))
        cmds.menuItem(parent=parent, divider=True)
        
        # remove profile
        profilesRemove = cmds.menuItem(parent=parent, subMenu=True, label='Remove Profile')
        for p in profiles: 
            cmds.menuItem(parent=profilesRemove, label='Remove: ' + p, enable=not (p == currentProfile), command=partial(self.removeProfile, p))        
    
    def switchToProfile(self, profile, *args, **kwargs): 
        command = partial(self.switchToProfile_deferred, profile)   
        cmds.evalDeferred(command)
    
    def switchToProfile_deferred(self, profile, *args, **kwargs):        
        # rebuild UI
        instances = self.getInstances()
        self.clearWidgets(instances=instances)
        
        # set profile
        Functions.setActiveProfile(profile)

        # rebuild
        # window.load()
        self.addWidgetsFromPrefs(profile=profile)
    
    @classmethod
    def addWidgetsFromPrefs(cls, *args, **kwargs):    
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')              
        
        # check prefs first
        version, widgetData = Functions.retreivePrefs(profile=profile)

        # if there isnt widget data, get from defaults
        if not widgetData or version != Functions.getVersion():
            widgetData = cls.getDefaultWidgetData()
                        
        # get UI parent
        parent = cls.getWidgetParent()
        
        # load in all UI items
        for w in widgetData:
            # unpack data
            widgetDescription = w['description']
            widgetType = w['widgetType']
            widgetState = w['state']
            widgetExpandedState = True
            try:
                widgetExpandedState = w['expanded']
            except:
                pass

            # type
            if widgetType == 'inbetween':
                # create new item
                newItem = widget_tween(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'extras':
                # create new item
                newItem = widget_extras(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'worldSpace':
                # create new item
                newItem = widget_worldSpace(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'classic':
                # create new item
                newItem = widget_classic(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'curveOptions':
                # create new item
                newItem = widget_curveOptions(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'snapshot':
                # create new item
                newItem = widget_snapshot(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

            # type
            if widgetType == 'principles':
                # create new item
                newItem = widget_principles(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
    
                # type
            if widgetType == 'tools':
                # create new item
                newItem = widget_tools(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

    
    @classmethod
    def getDefaultWidgetData(cls, *args, **kwargs):
        # setup data container
        widgetData = []

        # 
        data = {}
        data['widgetType'] = 'principles'
        data['description'] = 'Animation Principles'
        data['expanded'] = False        
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        # widgetData.append(data)  

        # 
        data = {}
        data['widgetType'] = 'classic'
        data['description'] = 'Classic'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        widgetData.append(data)      
        
        # 
        data = {}
        data['widgetType'] = 'inbetween'
        data['description'] = 'Inbetween'
        data['expanded'] = True
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        # widgetData.append(data)  

        # 
        data = {}
        data['widgetType'] = 'extras'
        data['description'] = 'Extras'
        data['expanded'] = True
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        # widgetData.append(data)

        # 
        data = {}
        data['widgetType'] = 'worldSpace'
        data['description'] = 'World Space'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        # widgetData.append(data)   

        # 
        data = {}
        data['widgetType'] = 'snapshot'
        data['description'] = 'Snapshot'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        # widgetData.append(data)       

        # 
        data = {}
        data['widgetType'] = 'curveOptions'
        data['description'] = 'Curve Options'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        widgetData.append(data)   
        
        # 
        data = {}
        data['widgetType'] = 'tools'
        data['description'] = 'Tools'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        #widgetData.append(data)           
         
        # return
        return widgetData

    @classmethod
    def clearWidgets(cls, *args, **kwargs):
        instances = cls.getInstances()
        if 'instances' in kwargs:
            instances = kwargs.pop('instances')        
        # remove all widgets without saving
        for i in instances:
            i.removeWidget(storePrefs=False)    

    def removeProfile(self, profile, *args, **kwargs):
        #
        Functions.removeProfile(profile) 
        #
        self.storePrefs()

    def createNewProfile(self, *args, **kwargs):        
        # get new profile name from the user
        profile = Functions.getStringFromUser()
        if profile:
            data = self.getCurrentState()
            Functions.newProfile(profile, data)
            self.storePrefs()
        
    def cleanSubframeKeys(self, *args, **kwargs):
        # get selection
        selection = self.getSelected()
        # run command
        Functions.cleanSubframeKeys(selection=selection)
        
    def removeBoringKeys(self, *args, **kwargs):
        regions = False
        if 'regions' in kwargs:
            regions = kwargs.pop('regions')
        # get selection
        selection = self.getSelected()
        # run command
        Functions.removeBoringKeys(selection=selection, regions=regions)

    def getMainContainer(self, *args, **kwargs):
        return self.mainContainer

    def removeWidget(self, *args, **kwargs):
        storePrefs = True 
        if 'storePrefs' in kwargs:
            storePrefs = kwargs.pop('storePrefs')         
        command = partial(self.removeWidget_deferred, storePrefs=storePrefs)
        cmds.evalDeferred(command)

    def removeWidget_deferred(self, storePrefs, *args, **kwargs):
        storePrefs = True
        if 'storePrefs' in kwargs:
            storePrefs = kwargs.pop('storePrefs')           

        # get UI element to delete
        layout = self.getMainContainer()
        cmds.deleteUI(layout, layout=True)

        # remove instance
        try:
            self.instances.remove(self)
        except:
            pass

        # store prefs
        if storePrefs:
            self.storePrefs()
        
        # resize
        window.resizeUI()  # subtractHeight=height


    @classmethod
    def getCurrentState(cls, *args, **kwargs):
        # build a list of all of the widget data
        widgetList = []

        # iterate through current widgets
        for instance in cls.getInstances():
            data = {}
            data['description'] = instance.getDescription()
            data['widgetType'] = instance.getType()
            data['state'] = instance.getState()
            data['expanded'] = instance.getWidgetExpandedState()
            widgetList.append(data)
        # return
        return widgetList

    def getState(self):
        """
        This will get overwritten to collect data specific to each widget
        """
        return {}
    
    def setState(self, stateData):
        """
        This will get overwritten to collect data specific to each widget
        """
        pass    

    def getType(self):
        return self.widgetType

    @classmethod
    def printInfo(cls, *args, **kwargs):
        """ print info about the widgets
        """
        widgetData = cls.getCurrentState()
        print 175, 'widgetData'
        for w in widgetData:
            print w

    @classmethod
    def storePrefs(cls, *args, **kwargs):
        # pull args
        debugging = False
        if 'debugging' in kwargs:
            debugging = kwargs.pop('debugging')
            
        # get state
        widgetData = cls.getCurrentState()
        
        # store to prefs
        Functions.storePrefs(widgetData)

    @classmethod
    def setInstances(cls, instances):
        cls.instances = instances

    @classmethod
    def getInstances(cls):
        return cls.instances

    def setDescription(self, description):
        '''
        This is for setting the description text in the widget, its optional
        '''
        self.description = description
        try:
            self.descriptionWidget.overrideDescription(self.description)
        except:
            pass
        # also set the framelayout label
        try:
            cmds.frameLayout(self.mainContainer, edit=True, label=self.description)
        except:
            pass

    def getDescription(self):
        try:
            self.description
        except:
            self.description = ''
        return self.description

    def getLayout(self):
        return self.formLayout

    def getLayoutWidth(self):
        return cmds.formLayout(self.formLayout, query=True, width=True)

    def setLayoutWidth(self, w):
        return cmds.formLayout(self.formLayout, edit=True, width=w)

    def getSelected(self):
        selection = []
        # check for pinned selections
        if self.getPinState():
            selection = self.getBufferSelection()
        else:
            selection = cmds.ls(sl=True, type = ['transform', 'joint'], long=True)
        return selection
    
    def getSelectedChannels(self, *args, **kwargs):
        selection = []
        # check for pinned channel selections
        if self.getPinState():
            selection = self.getBufferChannels()
                    
        if not selection:
            selection = Functions.getSelectedChannels( *args, **kwargs)
        
        return selection

    def setWidgetType(self, widgetType):
        self.widgetType = widgetType

    
    def pinSelectionPopupMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')

        # clean up
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)
        
        # get pinned state
        state = self.getPinState()
        
        # info
        if state:
            bufferSelection = self.getBufferSelection()
            bufferCount = len(bufferSelection)
            storedChannels = self.getBufferChannels()
            storedChannelsString = ''
            storedChannelCount = 0
            if storedChannels:
                storedChannelsString = '], ['.join(storedChannels)
                storedChannelCount = len(storedChannels)
            
            cmds.menuItem(label='Info: {0} Stored Objects'.format(bufferCount), enable=False)
            cmds.menuItem(label='Info: {0} Stored Channels: [{1}]'.format(storedChannelCount, storedChannelsString), enable=False)
            cmds.menuItem(divider=True)
        
        # add remove objects
        count = 0
        selected = cmds.ls(sl=True)
        if selected:
            count = len(selected)
        
        cmds.menuItem(label='Add Selected {0} Object(s)'.format(count), enable=state, command=partial(self.modifySelectionBuffer, 'add'))
        cmds.menuItem(label='Remove Selected {0} Object(s)'.format(count), enable=state, command=partial(self.modifySelectionBuffer, 'remove'))
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Set Highlighted Channels'.format(count), enable=state, command=partial(self.storeHighlightedChannels, 'add'))
        cmds.menuItem(divider=True)
        # selection options
        cmds.menuItem(label='Select Objects', enable=state, command=partial(self.selectObjects, forSelectedNamespace=False))
        cmds.menuItem(label='Select Objects For selection Namespace', enable=state, command=partial(self.selectObjects, forSelectedNamespace=True))

    def storeHighlightedChannels(self, *args, **kwargs):
        highlightedChannels = Functions.getSelectedChannels()  
        self.setBufferChannels(highlightedChannels)

        # store prefs
        self.storePrefs()        

    def modifySelectionBuffer(self, action, *args, **kwargs):
        # get buffer
        currentBuffer = self.getSelected()
        
        if action == 'add':
            currentBuffer = list(set(currentBuffer) | set(cmds.ls(sl=True)))
        elif action == 'remove':
            currentBuffer = list(set(currentBuffer) - set(cmds.ls(sl=True)))
        
        # store buffer
        self.bufferSelection = currentBuffer
        
        # update button
        try:
            selectionCount = len(self.bufferSelection)
            description = '{0} Objects'.format(str(selectionCount))
            self.pinSelectionToggle.overrideDescription(description)
        except:
            pass
        
        # store prefs
        self.storePrefs()


    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')

        # A state
        if state:
            # set pin state
            self.setPinState(False)
            
            # reselect previous objects
            bufferSelection = self.getBufferSelection()
            if bufferSelection:
                cmds.select(bufferSelection)
            
            # clear selected channels
            self.setBufferChannels([])

        # B state
        else:

            # set pin state
            self.setPinState(True)            
            
            # allow for defalts to come through
            if not onInit:
                self.setBufferSelection(cmds.ls(sl=True))

            # attempt to change description
            try:
                selectionCount = len(self.bufferSelection)
                description = '{0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except:
                pass

        # store prefs
        self.storePrefs()


    def selectObjects(self, *args, **kwargs):
        forSelectedNamespace = False
        if 'forSelectedNamespace' in kwargs:
            forSelectedNamespace = kwargs.pop('forSelectedNamespace')

        # setup
        toSelect = []
        
        # for regular selection based on buffer
        if not forSelectedNamespace:
            # get standard selection
            toSelect = self.getSelected()
        
        # for special override selection
        elif forSelectedNamespace:
            # setup namespace behavior
            selection = cmds.ls(sl=True)
            selectedNamespaces = set(Functions.getNamespaces(nodes=selection))
            bufferNodes = self.getSelected()
            bufferNamespaces = set(Functions.getNamespaces(nodes=bufferNodes))
            
            for bufferNode in bufferNodes:
                # if nothing selection apply to original OR something with same namespace selection
                if not selection or selectedNamespaces == bufferNamespaces:
                    # no change
                    toSelect += [bufferNode]
                elif selectedNamespaces != bufferNamespaces:
                    toSelect += Functions.findMatchingObjectsInNamespace(node=bufferNode, namespaces=selectedNamespaces)

        # make selection
        cmds.select(clear=True)
        for s in toSelect:
            if cmds.objExists(s):
                cmds.select(s, add=True)

    def setPinState(self, state):
        self.pinState = state

    def getPinState(self):
        try:
            self.pinState
        except:
            self.pinState = False
        return self.pinState        

    def setBufferSelection(self, selection):
        if selection:
            self.bufferSelection = selection

    def getBufferSelection(self):
        try:
            self.bufferSelection
        except:
            self.bufferSelection = []
        return self.bufferSelection

    def setBufferChannels(self, selection):
        self.bufferChannels = selection

    def getBufferChannels(self):
        try:
            self.bufferChannels
        except:
            self.bufferChannels = []
        return self.bufferChannels    

    def onDescriptionChange(self, description, *args, **kwargs):
        # store new description
        self.setDescription(description)
        
        # store prefs
        self.storePrefs()

class widget_tween(widget_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Inbetween'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('inbetween')


    def setState(self, stateData):
        # unpack data
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass
        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass
        try:
            self.setUseAllLayersState(stateData['useAllLayersState'])
        except:
            pass
        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass         
    
    def setUseAllLayersState(self, state):
        self.useAllLayersState = state

    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True
        return self.useAllLayersState

    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)  # , bgc = [0.95]*3
        
        # set default colors
        buttonBGC = [0.95] * 3

        # add tween slider
        self.sliderTween = slider_tween(parent=layoutContainer)
        sliderTweenUI = self.sliderTween.getLayout()
        self.sliderTween.getSelected = self.getSelected
        self.sliderTween.getUseAllLayersState = self.getUseAllLayersState
        self.sliderTween.getSelectedChannels = self.getSelectedChannels
        
        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        # descriptionWidgetLayout = cmds.text(parent = layoutContainer, width=5, height = 20, bgc = [1]*3)

        # layers selection toggle
        ADescription = 'Anim Layers'
        BDescription = 'Isolate Layer'
        ACommand = partial(self.onToggleLayersButton, True)
        BCommand = partial(self.onToggleLayersButton, False)
        startState = self.getUseAllLayersState()
        self.layerToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        layerToggleButton = self.layerToggle.getLayout()

        # pin selection toggle
        startState = not self.getPinState()  # flipping the bool
        ADescription = 'Pin Selection'
        
        # for working with rebuilds, setup an initial description if nessasry
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass
        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)

        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()

        # special right click menu pin selection toggle
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))

        # preset buttons
        easyTweenButton = cmds.button(parent=layoutContainer, label='Easy Tween', width=5, height=22, command=partial(self.sliderTween.useSetValueCommand), bgc=buttonBGC)

        # check keyframe colors
        h, s, v = cmds.displayRGBColor('timeSliderKey', query=True, hueSaturationValue=True)
        keyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, .5, .8)
        h, s, v = cmds.displayRGBColor('timeSliderTickDrawSpecial', query=True, hueSaturationValue=True)
        specialKeyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, .5, .8)

        # make buttons
        size = 22
        # regular key colors
        setKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe), annotation='Set Key on Objects', height=size, width=size, bgc=keyframeColor_rgb , label='')
        # setup right click menu
        popupMenu = cmds.popupMenu(parent=setKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=False))

        # special key colors
        setSpecialKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe, special=True), annotation='Set Colored Key on Objects', height=size, width=size, bgc=specialKeyframeColor_rgb , label='')
        # setup right click menu
        popupMenu = cmds.popupMenu(parent=setSpecialKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=True))

        # presets
        presetLayout = cmds.formLayout(parent=layoutContainer)
        value = 0
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton1 = cmds.button(parent=presetLayout, annotation='Previous', label='Prev', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.1
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton2 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.25
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton3 = cmds.button(parent=presetLayout, annotation='1/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.5
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton4 = cmds.button(parent=presetLayout, annotation='Half', label='Half', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.75
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton5 = cmds.button(parent=presetLayout, annotation='3/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.9
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton6 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 1
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton7 = cmds.button(parent=presetLayout, annotation='Next', label='Next', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)

        padding = 1
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton1, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1, 'left', padding, 0)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton1, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1, 'right', padding, 20)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton2, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2, 'left', padding, 20)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton2, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2, 'right', padding, 30)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton3, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3, 'left', padding, 30)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton3, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3, 'right', padding, 40)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton4, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4, 'left', padding, 40)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton4, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4, 'right', padding, 60)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton5, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5, 'left', padding, 60)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton5, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5, 'right', padding, 70)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton6, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6, 'left', padding, 70)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton6, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6, 'right', padding, 80)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton7, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7, 'left', padding, 80)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton7, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7, 'right', padding, 100)])

        # layout
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout, 'right', 0, layerToggleButton)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(layerToggleButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(layerToggleButton, 'right', 0, pinSelectionButton)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setKeyButton, 'top', 1, layerToggleButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(setKeyButton, 'left', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'right')])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton, 'top', 1, pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton, 'left', 2, setKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'right')])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton, 'top', 1, pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton, 'left', 2, setSpecialKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(easyTweenButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(easyTweenButton, 'right', 1)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderTweenUI, 'top', 5, easyTweenButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderTweenUI, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetLayout, 'top', 5, sliderTweenUI)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'right', 0)])
        
    '''
    def onDescriptionChange(self, description, *args, **kwargs):
        # store new description
        self.setDescription(description)
        
        # store prefs
        self.storePrefs()
    '''

    def getState(self):
        # collect some data
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        data['useAllLayersState'] = self.useAllLayersState
        # return
        return data

    def onToggleLayersButton(self, state, *args, **kwargs):
        # A state
        if state:
            self.useAllLayersState = True

        # B state
        else:
            self.useAllLayersState = False

        # store prefs
        self.storePrefs(debugging='onToggleLayersButton')

    '''
    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        
        # A state
        if state:
            self.setPinState(False)

            # reselect previous objects
            if self.bufferSelection:
                cmds.select(self.bufferSelection)

        # B state
        else:
            # allow for defalts to come through
            if not onInit:
                self.bufferSelection = cmds.ls(sl=True)

            # attempt to change description
            try:
                selectionCount = len(self.bufferSelection)
                description = '{0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except:
                pass
            # self.pinSelectionToggle.overrideDescription(description)
            self.setPinState(True)

        # store prefs
        self.storePrefs(debugging='onPinSelectionButton')
    '''


class widget_snapshot(widget_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Snapshot'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        # print json.dumps(self.getDataBuffer(), sort_keys=True, indent=4)
        
        # construct UI elements
        self.setupUI()
        
        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('snapshot')
        
        # set slider internal data
        self.setInitialSliderState()
        
    def setInitialSliderState(self):
        # set data if enabled on startup
        if self.getPinState():
            # clear pose data
            self.slider.clearData()
            
            # set data to slider
            data = self.getDataBuffer()
            self.slider.setSnapshotData(data)

            # enable slider
            self.slider.setSliderState(True) 
        else:
            # disnable slider
            self.slider.setSliderState(False)       

    def setState(self, stateData):
        # unpack data
        try:
            self.setPinState(stateData['pinState'])
        except:
            self.setPinState(False)
        try:
            self.setDataBuffer(stateData['bufferData'])
        except:
            self.setDataBuffer([])
        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass             

    def getState(self):
        # collect some data
        data = {}
        data['pinState'] = self.pinState
        data['bufferData'] = self.getDataBuffer()
        data['bufferChannels'] = self.getBufferChannels()
        # return
        return data

    def setDataBuffer(self, data):
        self.bufferData = data
        
        # also set selection buffer
        if data:
            selection = data.keys()
            self.setBufferSelection(selection)

    def getDataBuffer(self):
        try:
            self.bufferData
        except:
            self.bufferData = []
        return self.bufferData

    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)  # , bgc = [0.95]*3
        
        # set default colors
        buttonBGC = [0.95] * 3

        # add slider
        self.slider = slider_snapshot(parent=layoutContainer)
        sliderElement = self.slider.getLayout()
        self.slider.getSelected = self.getSelected
        self.slider.getSelectedChannels = self.getSelectedChannels
        
        # add apply pose button
        height = 15
        value = 1
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        applyFullButton = cmds.button(parent=layoutContainer, label='Appy Pose', width=5, height=height, command=partial(self.slider.presetCommand, value), bgc=buttonBGC)
        
        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()

        # snapshot toggle
        startState = not self.getPinState()  # flipping the bool
        ADescription = 'Capture Pose'
        
        # for working with rebuilds, setup an initial description if nessasry
        BDescription = 'Pose Stored'
        # if not startState:
        try:
            selectionCount = len(self.getDataBuffer())
            BDescription = 'Pose Stored, {0} Objects'.format(str(selectionCount))
        except:
            pass
        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()

        # special right click menu pin selection toggle
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))

        # layout
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(descriptionWidgetLayout, 'right', 0, 33)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(pinSelectionButton, 'left', 0, descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderElement, 'top', 5, pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderElement, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderElement, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(sliderElement, 'right', 10, 66)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(applyFullButton, 'top', 5, pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(applyFullButton, 'left', 0, 66)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(applyFullButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(applyFullButton, 'right', 2)])
        
    '''
    def onDescriptionChange(self, description, *args, **kwargs):
        # store new description
        self.setDescription(description)
        
        # store prefs
        self.storePrefs()
    '''

    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        
        # A state
        if state:
            self.setPinState(False)
            
            # clear pose data
            self.slider.clearData()
            
            # disable slider
            self.slider.setSliderState(False)

        # B state
        else:
            # store pose
            self.slider.collectSnapshotData()
            
            # store slider data
            data = self.slider.getSnapshotData()
            self.setDataBuffer(data)
            
            #
            self.setPinState(True)
            
            # enable slider
            self.slider.setSliderState(True)   
            
            try:
                # attempt to change description
                selectionCount = len(self.getDataBuffer())
                description = 'Pose Stored, {0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except Exception, e:
                print 1990, e         

        # store prefs
        self.storePrefs(debugging='onPinSelectionButton')

class widget_extras(widget_base): 
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'extras'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('extras')

    def setState(self, stateData):
        # unpack data
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass
        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass
        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass         

    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        # cmds.formLayout(layoutContainer, edit = True, bgc = [0.95]*3)
        
        # set default colors
        buttonBGC = [0.95] * 3

        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), changeCommand=changeCommand, collapseCommand=collapseCommand, width=60)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        
        # pin selection toggle
        startState = not self.getPinState()  # flipping the bool
        ADescription = 'Pin Selection'
        
        # for working with rebuilds, setup an initial description if nessasry
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass
        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()
        
        # special right click menu pin selection toggle
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))
        
        # extras
        miniSlidersLayout = cmds.formLayout(parent=layoutContainer)
        size = 22
        
        #
        sliderA = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=.1, bgc=buttonBGC)  # , dragCommand=partial(self.slider_realtime, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish), 
        # sliderB = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=.1, bgc=buttonBGC)  # , dragCommand=partial(self.slider_realtime, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish), 
        # sliderC = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=.1, bgc=buttonBGC)  # , dragCommand=partial(self.slider_realtime, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish), 
        sliderA_label = cmds.text(parent=miniSlidersLayout, label='Multiply', bgc=buttonBGC, height=size, width=5, align='center')
        sliderB_label = cmds.text(parent=miniSlidersLayout, label='PosePusher', bgc=buttonBGC, height=size, width=5, align='center')
        sliderC_label = cmds.text(parent=miniSlidersLayout, label='In<>Out', bgc=buttonBGC, height=size, width=5, align='center')

        # posePusher slider
        self.posePusher = slider_PosePusher(parent=miniSlidersLayout)
        posePusherUI = self.posePusher.getLayout()
        self.posePusher.getSelected = self.getSelected  
        self.posePusher.getSelectedChannels = self.getSelectedChannels     
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.posePusher, element=sliderB_label)
        self.posePusher.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderB_label, 'PosePusher')
        self.posePusher.addMultiplierPostCommand(command)            
        
        
        # in out slider
        self.sliderInOut = slider_inOut(parent=miniSlidersLayout)
        sliderInOutUI = self.sliderInOut.getLayout()
        self.sliderInOut.getSelected = self.getSelected
        self.sliderInOut.getSelectedChannels = self.getSelectedChannels     
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderInOut, element=sliderC_label)
        self.sliderInOut.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderC_label, 'In<>Out')
        self.sliderInOut.addMultiplierPostCommand(command)     
        
        # multiply slider
        self.sliderMultiply = slider_multiply(parent=miniSlidersLayout)
        sliderMultiplyUI = self.sliderMultiply.getLayout()
        self.sliderMultiply.getSelected = self.getSelected   
        self.sliderMultiply.getSelectedChannels = self.getSelectedChannels     
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderMultiply, element=sliderA_label)
        self.sliderMultiply.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderA_label, 'Multiply')
        self.sliderMultiply.addMultiplierPostCommand(command)  


        padding = 1
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderA_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label, 'left', padding, 0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderA_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label, 'right', padding, 33)])

        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderB_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label, 'left', padding, 34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderB_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label, 'right', padding, 66)])
        
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderC_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label, 'left', padding, 67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderC_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label, 'right', padding, 100)])        

        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderMultiplyUI, 'top', 0, sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI, 'left', padding, 0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderMultiplyUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI, 'right', padding, 33)])

        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(posePusherUI, 'top', 0, sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI, 'left', padding, 34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(posePusherUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI, 'right', padding, 66)])

        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderInOutUI, 'top', 0, sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI, 'left', padding, 67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderInOutUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI, 'right', padding, 100)]) 

        # layout
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout, 'right', 0, pinSelectionButton)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(miniSlidersLayout, 'top', 2, descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(miniSlidersLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'right', 0)])

    '''
    def onDescriptionChange(self, description, *args, **kwargs):
        # store new description
        self.setDescription(description)
        
        # store prefs
        self.storePrefs()
    '''

    def getState(self):
        # collect some data
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        # return
        return data

    """
    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        
        # A state
        if state:
            self.setPinState(False)

            # reselect previous objects
            if self.bufferSelection:
                cmds.select(self.bufferSelection)

        # B state
        else:
            # allow for defalts to come through
            if not onInit:
                self.bufferSelection = cmds.ls(sl=True)

            # attempt to change description
            try:
                selectionCount = len(self.bufferSelection)
                description = '{0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except:
                pass
            # self.pinSelectionToggle.overrideDescription(description)
            self.setPinState(True)

        # store prefs
        self.storePrefs(debugging='onPinSelectionButton')
    """

      
class widget_tools(widget_base): 
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'tools'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('tools')
        
        # update timeRange
        self.refreshTimeRange()

    def setState(self, stateData):
        pass
        """
        # unpack data
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass
        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass
        """

    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        
        #spacer
        spacerHeight = 2
        
        # column layout
        columnLayout = cmds.columnLayout(parent=layoutContainer, adjustableColumn=True, columnAttach=['both', 1], rowSpacing=2)
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(columnLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(columnLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(columnLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(columnLayout, 'right', 0)])
        
        # add items
        height = 18
        
        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=columnLayout, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        #descriptionWidgetLayout = self.descriptionWidget.getLayout()

        # other buttons
        cmds.button(parent=columnLayout, label='Rekey Selection', bgc=[.6] * 3, height=height, command=partial(self.rekeyOnKeys))
        cmds.button(parent=columnLayout, label='Rekey Selection To Match Last Selected', bgc=[.6] * 3, height=height, command=partial(self.rekeyOnKeys, matchLast=True))
        cmds.formLayout(parent=columnLayout, height=spacerHeight)
        cmds.button(parent=columnLayout, label='Clean Subframe Keys', bgc=[.6] * 3, height=height, command=partial(self.cleanSubframeKeys))
        cmds.button(parent=columnLayout, label='Remove Boring Keys', bgc=[.6] * 3, height=height, command=partial(self.removeBoringKeys, regions=False))
        cmds.formLayout(parent=columnLayout, height=spacerHeight)
        # smash bake
        smashBakeLayout = cmds.formLayout(parent=columnLayout, width=5, bgc=[.6] * 3, height=height)
        self.startFrameField = cmds.intField(parent=smashBakeLayout, width=5, bgc=[.3] * 3, height=height)
        self.endFrameField = cmds.intField(parent=smashBakeLayout, width=5, bgc=[.3] * 3, height=height)
        bakeButton = cmds.button(parent=smashBakeLayout, label='Smash Bake', width=5, height=height, command=partial(self.smashBakeButton))
        
        # smash bake popup
        popupMenu = cmds.popupMenu(parent=smashBakeLayout)
        cmds.popupMenu(popupMenu, edit=True, button=3, postMenuCommand=partial(self.smashBakeOptionsPopup, parent=popupMenu))

        # smash bake layout
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(bakeButton, 'top', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(bakeButton, 'left', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachNone=[(bakeButton, 'bottom')])
        cmds.formLayout(smashBakeLayout, edit=True, attachPosition=[(bakeButton, 'right', 0, 50)])

        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(self.startFrameField, 'top', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachControl=[(self.startFrameField, 'left', 0, bakeButton)])
        cmds.formLayout(smashBakeLayout, edit=True, attachNone=[(self.startFrameField, 'bottom')])
        cmds.formLayout(smashBakeLayout, edit=True, attachPosition=[(self.startFrameField, 'right', 0, 75)])    

        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(self.endFrameField, 'top', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachControl=[(self.endFrameField, 'left', 0, self.startFrameField)])
        cmds.formLayout(smashBakeLayout, edit=True, attachNone=[(self.endFrameField, 'bottom')])
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(self.endFrameField, 'right', 0)])  
        
        # quick undo
        cmds.formLayout(parent=columnLayout, height=spacerHeight)
        quickUndosLayout = cmds.formLayout(parent=columnLayout, width=5, bgc=[.6] * 3, height=height)
        undoButton = cmds.button(parent=quickUndosLayout, label='Quick Undo', bgc=[.8] * 3, height=height, command=partial(Functions.quickUndo))
        redoButton = cmds.button(parent=quickUndosLayout, label='Quick Redo', bgc=[.4] * 3, height=height, command=partial(Functions.quickRedo))
        
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(undoButton, 'top', 0)])
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(undoButton, 'left', 0)])
        cmds.formLayout(quickUndosLayout, edit=True, attachNone=[(undoButton, 'bottom')])
        cmds.formLayout(quickUndosLayout, edit=True, attachPosition=[(undoButton, 'right', 0, 50)])    

        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(redoButton, 'top', 0)])
        cmds.formLayout(quickUndosLayout, edit=True, attachControl=[(redoButton, 'left', 0, undoButton)])
        cmds.formLayout(quickUndosLayout, edit=True, attachNone=[(redoButton, 'bottom')])
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(redoButton, 'right', 0)])  

    def onCollapseButtonPress(self, *args, **kwargs):
        # reset collapse state
        cmds.frameLayout( self.collapseButton, edit=True,  collapse=False)
        #cmds.evalDeferred(command)

        # run command
        self.collapseMainContainer()

    def smashBakeButton(self, *args, **kwargs):
        # default to defaults
        startTime, endTime = Functions.queryTimeRange()
        #
        try:
            startTime = cmds.intField(self.startFrameField, query=True, value=startTime)
            endTime = cmds.intField(self.endFrameField, query=True, value=endTime)
        except:
            pass
        #
        selected = cmds.ls(sl=True)
        

        #
        Functions.smashBaker(selected, startTime, endTime)

    def smashBakeOptionsPopup(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')

        # clean up
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)

        # menu buttons
        cmds.menuItem(parent=parent, label='Refresh Time Range', command=partial(self.refreshTimeRange))

    def refreshTimeRange(self, *args, **kwargs):
        checkHighlighted = False
        if 'checkHighlighted' in kwargs:
            checkHighlighted = kwargs.pop('checkHighlighted')
        
        startTime, endTime = Functions.queryTimeRange(checkHighlighted=checkHighlighted)
        #
        cmds.intField(self.startFrameField, edit=True, value=startTime)
        cmds.intField(self.endFrameField, edit=True, value=endTime)
        
class widget_worldSpace(widget_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'World Space'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('worldSpace')

    def setState(self, stateData):
        # unpack data
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass
        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass
        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass         
    
    '''
    def setUseAllLayersState(self, state):
        self.useAllLayersState = state
    
    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True
        return self.useAllLayersState
    '''

    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)  # , bgc = [0.95]*3
        
        # set default colors
        buttonBGC = [0.95] * 3

        # add 
        self.sliderWorldSpace = slider_worldSpace(parent=layoutContainer)
        sliderWorldSpaceUI = self.sliderWorldSpace.getLayout()
        self.sliderWorldSpace.getSelected = self.getSelected
        self.sliderWorldSpace.getSelectedChannels = self.getSelectedChannels 

        # presets
        height = 15
        value = 0
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton1 = cmds.button(parent=layoutContainer, annotation='Previous', label='Prev', width=5, height=height, command=partial(self.sliderWorldSpace.presetCommand, value), bgc=buttonBGC)
        value = 1
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton2 = cmds.button(parent=layoutContainer, annotation='Next', label='Next', width=5, height=height, command=partial(self.sliderWorldSpace.presetCommand, value), bgc=buttonBGC)
        
        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, collapseCommand=collapseCommand, description=self.getDescription(), changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()

        # pin selection toggle
        startState = not self.getPinState()  # flipping the bool
        ADescription = 'Pin Selection'
        
        # for working with rebuilds, setup an initial description if nessasry
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass
        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)

        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()

        # special right click menu pin selection toggle
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))

        # layout
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout, 'right', 0, pinSelectionButton)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetButton1, 'top', 5, descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetButton1, 'left', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetButton1, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(presetButton1, 'right', 0, 20)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetButton2, 'top', 5, descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(presetButton2, 'left', 0, 80)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetButton2, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetButton2, 'right', 2)])        

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderWorldSpaceUI, 'top', 5, descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderWorldSpaceUI, 'left', 5, presetButton1)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderWorldSpaceUI, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderWorldSpaceUI, 'right', 5, presetButton2)])

    '''
    def onDescriptionChange(self, description, *args, **kwargs):
        # store new description
        self.setDescription(description)
        
        # store prefs
        self.storePrefs()
    '''

    def getState(self):
        # collect some data
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        # data['useAllLayersState'] = self.useAllLayersState
        # return
        return data

    '''
    def easyTweenCommand(self, *args, **kwargs):
        try:
            # set values
            self.slider_realtime(useSetValue=True)
        except Exception, e:
            print 444, Exception, e
        finally:
            # close command
            self.slider_realtime_finish()
    
    def tweenPresetCommand(self, value, *args, **kwargs):
        try:
            # set values
            self.slider_realtime(overrideRatio=value)
        except Exception, e:
            print 444, Exception, e
        finally:
            # close command
            self.slider_realtime_finish()
    '''

    '''
    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        
        # A state
        if state:
            self.setPinState(False)

            # reselect previous objects
            if self.bufferSelection:
                cmds.select(self.bufferSelection)

        # B state
        else:
            # allow for defalts to come through
            if not onInit:
                self.bufferSelection = cmds.ls(sl=True)

            # attempt to change description
            try:
                selectionCount = len(self.bufferSelection)
                description = '{0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except:
                pass
            # self.pinSelectionToggle.overrideDescription(description)
            self.setPinState(True)

        # store prefs
        self.storePrefs(debugging='onPinSelectionButton')
    '''


class widget_classic(widget_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Inbetween'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('classic')

    def setState(self, stateData):
        # unpack data
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass
        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass
        try:
            self.setUseAllLayersState(stateData['useAllLayersState'])
        except:
            pass
        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass        
    
    def setUseAllLayersState(self, state):
        self.useAllLayersState = state

    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True
        return self.useAllLayersState

    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)  # , bgc = [0.95]*3
        
        # set default colors
        buttonBGC = [0.95] * 3

        # add tween slider
        self.sliderTween = slider_tween(parent=layoutContainer)
        sliderTweenUI = self.sliderTween.getLayout()
        self.sliderTween.getSelected = self.getSelected
        self.sliderTween.getUseAllLayersState = self.getUseAllLayersState
        self.sliderTween.getSelectedChannels = self.getSelectedChannels

        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        # descriptionWidgetLayout = cmds.text(parent = layoutContainer, width=5, height = 20, bgc = [1]*3)

        # layers selection toggle
        ADescription = 'Anim Layers'
        BDescription = 'Isolate Layer'
        ACommand = partial(self.onToggleLayersButton, True)
        BCommand = partial(self.onToggleLayersButton, False)
        startState = self.getUseAllLayersState()
        self.layerToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        layerToggleButton = self.layerToggle.getLayout()

        # pin selection toggle
        startState = not self.getPinState()  # flipping the bool
        ADescription = 'Pin Selection'
        
        # for working with rebuilds, setup an initial description if nessasry
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass
        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)

        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()

        # special right click menu pin selection toggle
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))

        # preset buttons
        easyTweenButton = cmds.button(parent=layoutContainer, label='Easy Tween', width=5, height=22, command=partial(self.sliderTween.useSetValueCommand), bgc=buttonBGC)

        # check keyframe colors
        h, s, v = cmds.displayRGBColor('timeSliderKey', query=True, hueSaturationValue=True)
        keyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, .5, .8)
        h, s, v = cmds.displayRGBColor('timeSliderTickDrawSpecial', query=True, hueSaturationValue=True)
        specialKeyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, .5, .8)

        # make buttons
        size = 22
        # regular key colors
        setKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe), annotation='Set Key on Objects', height=size, width=size, bgc=keyframeColor_rgb , label='')
        # setup right click menu
        popupMenu = cmds.popupMenu(parent=setKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=False))

        # special key colors
        setSpecialKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe, special=True), annotation='Set Colored Key on Objects', height=size, width=size, bgc=specialKeyframeColor_rgb , label='')
        # setup right click menu
        popupMenu = cmds.popupMenu(parent=setSpecialKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=True))

        # presets
        presetLayout = cmds.formLayout(parent=layoutContainer)
        value = 0
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton1 = cmds.button(parent=presetLayout, annotation='Previous', label='Prev', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.1
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton2 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.25
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton3 = cmds.button(parent=presetLayout, annotation='1/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.5
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton4 = cmds.button(parent=presetLayout, annotation='Half', label='Half', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.75
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton5 = cmds.button(parent=presetLayout, annotation='3/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.9
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton6 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 1
        value = ((value * 2) - 1)  # convert to -1 to 1 range
        presetButton7 = cmds.button(parent=presetLayout, annotation='Next', label='Next', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)

        padding = 1
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton1, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1, 'left', padding, 0)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton1, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1, 'right', padding, 20)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton2, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2, 'left', padding, 20)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton2, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2, 'right', padding, 30)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton3, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3, 'left', padding, 30)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton3, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3, 'right', padding, 40)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton4, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4, 'left', padding, 40)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton4, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4, 'right', padding, 60)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton5, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5, 'left', padding, 60)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton5, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5, 'right', padding, 70)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton6, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6, 'left', padding, 70)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton6, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6, 'right', padding, 80)])

        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton7, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7, 'left', padding, 80)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton7, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7, 'right', padding, 100)])

        # presets
        miniSlidersLayout = cmds.formLayout(parent=layoutContainer)
        
        #
        sliderA = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=.1, bgc=buttonBGC)  # , dragCommand=partial(self.slider_realtime, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish), 
        # sliderB = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=.1, bgc=buttonBGC)  # , dragCommand=partial(self.slider_realtime, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish), 
        # sliderC = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=.1, bgc=buttonBGC)  # , dragCommand=partial(self.slider_realtime, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish), 
        sliderA_label = cmds.text(parent=miniSlidersLayout, label='Multiply', bgc=buttonBGC, height=size, width=5, align='center')
        sliderB_label = cmds.text(parent=miniSlidersLayout, label='PosePusher', bgc=buttonBGC, height=size, width=5, align='center')
        sliderC_label = cmds.text(parent=miniSlidersLayout, label='In<>Out', bgc=buttonBGC, height=size, width=5, align='center')

        # posePusher slider
        self.posePusher = slider_PosePusher(parent=miniSlidersLayout)
        posePusherUI = self.posePusher.getLayout()
        self.posePusher.getSelected = self.getSelected 
        self.posePusher.getSelectedChannels = self.getSelectedChannels      
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.posePusher, element=sliderB_label)
        self.posePusher.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderB_label, 'PosePusher')
        self.posePusher.addMultiplierPostCommand(command)            
        
        
        # in out slider
        self.sliderInOut = slider_inOut(parent=miniSlidersLayout)
        sliderInOutUI = self.sliderInOut.getLayout()
        self.sliderInOut.getSelected = self.getSelected
        self.sliderInOut.getSelectedChannels = self.getSelectedChannels  
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderInOut, element=sliderC_label)
        self.sliderInOut.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderC_label, 'In<>Out')
        self.sliderInOut.addMultiplierPostCommand(command)     
        
        # multiply slider
        self.sliderMultiply = slider_multiply(parent=miniSlidersLayout)
        sliderMultiplyUI = self.sliderMultiply.getLayout()
        self.sliderMultiply.getSelected = self.getSelected
        self.sliderMultiply.getSelectedChannels = self.getSelectedChannels          
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderMultiply, element=sliderA_label)
        self.sliderMultiply.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderA_label, 'Multiply')
        self.sliderMultiply.addMultiplierPostCommand(command)  


        padding = 1
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderA_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label, 'left', padding, 0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderA_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label, 'right', padding, 33)])

        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderB_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label, 'left', padding, 34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderB_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label, 'right', padding, 66)])
        
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderC_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label, 'left', padding, 67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderC_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label, 'right', padding, 100)])        

        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderMultiplyUI, 'top', 0, sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI, 'left', padding, 0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderMultiplyUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI, 'right', padding, 33)])

        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(posePusherUI, 'top', 0, sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI, 'left', padding, 34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(posePusherUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI, 'right', padding, 66)])
        
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderInOutUI, 'top', 0, sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI, 'left', padding, 67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderInOutUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI, 'right', padding, 100)]) 

        # layout
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout, 'right', 0, layerToggleButton)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(layerToggleButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(layerToggleButton, 'right', 0, pinSelectionButton)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setKeyButton, 'top', 1, layerToggleButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(setKeyButton, 'left', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'right')])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton, 'top', 1, pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton, 'left', 2, setKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'right')])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton, 'top', 1, pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton, 'left', 2, setSpecialKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(easyTweenButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(easyTweenButton, 'right', 1)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderTweenUI, 'top', 5, easyTweenButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderTweenUI, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetLayout, 'top', 5, sliderTweenUI)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(miniSlidersLayout, 'top', 5, presetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(miniSlidersLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'right', 0)])        
        
    '''
    def onDescriptionChange(self, description, *args, **kwargs):
        # store new description
        self.setDescription(description)
        
        # store prefs
        self.storePrefs()
    '''

    def getState(self):
        # collect some data
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        data['useAllLayersState'] = self.useAllLayersState
        # return
        return data

    def onToggleLayersButton(self, state, *args, **kwargs):
        # A state
        if state:
            self.useAllLayersState = True

        # B state
        else:
            self.useAllLayersState = False

        # store prefs
        self.storePrefs(debugging='onToggleLayersButton')

    '''
    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        
        # A state
        if state:
            self.setPinState(False)

            # reselect previous objects
            if self.bufferSelection:
                cmds.select(self.getBufferSelection())

        # B state
        else:
            # allow for defalts to come through
            if not onInit:
                self.bufferSelection = cmds.ls(sl=True)

            # attempt to change description
            try:
                selectionCount = len(self.bufferSelection)
                description = '{0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except:
                pass
            # self.pinSelectionToggle.overrideDescription(description)
            self.setPinState(True)

        # store prefs
        self.storePrefs(debugging='onPinSelectionButton')
        '''


class widget_curveOptions(widget_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Curve Options'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('curveOptions')


    def setupUI(self):
        # get main layout container
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)  # , bgc = [0.95]*3
        
        # set default colors
        buttonBGC = [0.95] * 3

        # setup button info
        curveOptionButtons = []

        buttonInfo = 'CollapseButton'
        curveOptionButtons.append(buttonInfo)
        
        buttonInfo = {}
        buttonInfo['image'] = 'autoTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'auto')
        buttonInfo['annotation'] = 'set to auto tangents'
        curveOptionButtons.append(buttonInfo)
        
        buttonInfo = {}
        buttonInfo['image'] = 'splineTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'spline')
        buttonInfo['annotation'] = 'set to spline tangents'
        curveOptionButtons.append(buttonInfo)       

        buttonInfo = {}
        buttonInfo['image'] = 'clampedTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'clamped')
        buttonInfo['annotation'] = 'set to clamped tangents'
        curveOptionButtons.append(buttonInfo) 

        buttonInfo = {}
        buttonInfo['image'] = 'linearTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'linear')
        buttonInfo['annotation'] = 'set to linear tangents'
        curveOptionButtons.append(buttonInfo) 

        buttonInfo = {}
        buttonInfo['image'] = 'flatTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'flat')
        buttonInfo['annotation'] = 'set to flat tangents'
        curveOptionButtons.append(buttonInfo) 

        buttonInfo = {}
        buttonInfo['image'] = 'stepTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'step')
        buttonInfo['annotation'] = 'set to step tangents'
        curveOptionButtons.append(buttonInfo)                         

        buttonInfo = {}
        buttonInfo['image'] = 'plateauTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'plateau')
        buttonInfo['annotation'] = 'set to plateau tangents'
        curveOptionButtons.append(buttonInfo)  

        buttonInfo = {}
        buttonInfo['image'] = 'freeTangentWeight.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'free')
        buttonInfo['annotation'] = 'set to free tangents handles'
        curveOptionButtons.append(buttonInfo) 
        
        # create buttons
        buttonObjects = []
        iconSize = 23
        for buttonInfo in curveOptionButtons:
            if buttonInfo == 'CollapseButton':
                command = partial(self.onCollapseButtonPress)
                color = [1] * 3  
                self.collapseButton = cmds.button(parent=layoutContainer, label='-', height=iconSize, width=iconSize, command = command, bgc=color, annotation='* Click To Collapse Widget')

                # self.collapseButton = cmds.frameLayout(parent=layoutContainer, width = iconSize, height=iconSize, bgc=[1] * 3, collapse=False, collapsable=True, labelVisible = True, label = '', collapseCommand=partial(self.onCollapseButtonPress))
                buttonObjects.append(self.collapseButton)
            
            else:
                buttonImage = buttonInfo['image']
                buttonCommand = buttonInfo['command']
                buttonAnnotation = buttonInfo['annotation'] 
                # auto tangent was introduced in maya 2012, so this will allow for some backwards compatibility
                try:
                    newButton = cmds.iconTextButton(parent=layoutContainer, image1=buttonImage, width=iconSize, height=iconSize, command=buttonCommand, ann=buttonAnnotation)
                    buttonObjects.append(newButton)
                except:
                    pass
        
        # layout buttons
        buttonCount = len(buttonObjects)
        for i, b in enumerate(buttonObjects):
            leftOffset = i * 100 / buttonCount
            cmds.formLayout(layoutContainer, edit=True, attachForm=[(b, 'top', 0)])
            cmds.formLayout(layoutContainer, edit=True, attachPosition=[(b, 'left', 0, leftOffset)])
            cmds.formLayout(layoutContainer, edit=True, attachNone=[(b, 'bottom')])
            cmds.formLayout(layoutContainer, edit=True, attachNone=[(b, 'right')])

    def onCollapseButtonPress(self, *args, **kwargs):
        # reset collapse state
        # cmds.frameLayout( self.collapseButton, edit=True,  collapse=False)
        #cmds.evalDeferred(command)

        # run command
        self.collapseMainContainer()

class widget_principles(widget_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Principles of Animation'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False, 'bufferSelection': [], 'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')

        # inherit class
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)

        # set state data
        self.setState(stateData)
        
        # construct UI elements
        self.setupUI()

        # set description
        self.setDescription(description)

        # set widget type
        self.setWidgetType('principles')
    
    def setupUI(self):

        # get main layout container
        layoutContainer = self.getLayout()
        #cmds.formLayout(layoutContainer, edit=True)  # , bgc = [0.95]*3
        
        # make list
        infoText = 'Welcome To whisKEY Pro\n\n'
        infoText += '* Right click anywhere to check out the main menu.\n'
        infoText += '\n'                
        infoText += 'Principles of Animation'
        infoText += '\n'
        infoText += '1 .Squash\'n stretch\n'
        infoText += '2 .Anticipation\n'
        infoText += '3 .Staging\n'
        infoText += '4 .Straight ahead and pose to pose\n'
        infoText += '5 .Follow through and overlap\n'
        infoText += '6 .Spacing\n'
        infoText += '7 .Arcs\n'
        infoText += '8 .Secondary action\n'
        infoText += '9 .Timing\n'
        infoText += '10.Exaggeration\n'
        infoText += '11.Solid drawing\n'
        infoText += '12.Appeal\n'
        infoText += '\n'
        infoText += '\n'
        infoText += 'And dont forget,\n'        
        infoText += '      ____ \n'
        infoText += '     |    | ebLabs \n'
        infoText += '     |    | whisKEY Pro\n'
        infoText += '     |____| \n'
        infoText += '     |    | (C)Eric Bates\n'
        infoText += '     (    ) 2015\n'
        infoText += '     )    ( eblabs-tech.com\n'
        infoText += '   .\'      `. \n'
        infoText += '  /          \\\n'
        infoText += ' |------------|\n'
        infoText += ' |JACK DANIELS|\n'
        infoText += ' |    ----    |\n'
        infoText += ' |   (No.7)   |\n'
        infoText += ' |    ----    |\n'
        infoText += ' | Tennessee  |\n'
        infoText += ' |  WHISKEY   |\n'
        infoText += ' |  40% Vol.  |\n'
        infoText += ' |------------|\n'
        infoText += ' |____________|\n'
        infoText += '\n'
            
        # info box
        self.infoBox = cmds.scrollField(parent=layoutContainer, wordWrap=True, editable=False, text=infoText)
        
        # widget text
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        
        # layout
        cmds.formLayout(layoutContainer, edit=True, height=100)

        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'right', 0)])

        cmds.formLayout(layoutContainer, edit=True, attachControl=[(self.infoBox, 'top', 0, descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(self.infoBox, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(self.infoBox, 'bottom', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(self.infoBox, 'right', 0)])


class button_toggleSwitch():
    '''
    button_toggleSwitch(parent = None, ADescription = '', BDescription = '', ACommand = '', BCommand = '', startState = True)
    '''
    def __init__(self, *args, **kwargs):
        #
        state = True

        # pull variables
        parent = None
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        startState = True
        if 'startState' in kwargs:
            startState = kwargs.pop('startState')            
        ADescription = ''
        if 'ADescription' in kwargs:
            ADescription = kwargs.pop('ADescription')
        BDescription = ''
        if 'BDescription' in kwargs:
            BDescription = kwargs.pop('BDescription')
        ACommand = False
        if 'ACommand' in kwargs:
            ACommand = kwargs.pop('ACommand')
        BCommand = False
        if 'BCommand' in kwargs:
            BCommand = kwargs.pop('BCommand')
        width = 75
        if 'width' in kwargs:
            width = kwargs.pop('width')
        height = 18
        if 'height' in kwargs:
            height = kwargs.pop('height')

        # setup
        if parent:
            cmds.setParent(parent)

        # add ui elements
        description = ADescription
        self.form = cmds.formLayout(parent=parent, height=height)
        # self.description = cmds.text(label=description, align='center')
        self.toggleButton = cmds.button(recomputeSize=False, width=width, height=1, command=partial(self.pressButton, ADescription, BDescription, ACommand, BCommand))

        # activate button
        self.setState(startState)
        self.pressButton = self.pressButton(ADescription, BDescription, ACommand, BCommand, onInit=True)

        # setup UI
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'left', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'right', 0)])

    def pressButton(self, ADescription, BDescription, ACommand, BCommand, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        
        # get state
        state = self.getState()

        # color toggles
        color = []
        if state:
            color = [.7, .7, .7]
            description = ADescription
            command = ACommand
        if not state:
            color = [.2, .2, .2]
            description = BDescription
            command = BCommand

        # set colors
        cmds.button(self.toggleButton, edit=True, bgc=color, label=description)

        # set toggle
        self.setState(not state)

        # run command
        if not onInit:
            if command:
                command(onInit=onInit)

    def overrideDescription(self, description, *args, **kwargs):
        cmds.button(self.toggleButton, edit=True, label=description)

    def setState(self, state, *args, **kwargs):
        self.state = state

    def getState(self, *args, **kwargs):
        return self.state

    def getLayout(self, *args, **kwargs):
        return self.form


class button_textToggle():
    def __init__(self, *args, **kwargs):
        # pull variables
        parent = None
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        self.description = ''
        if 'description' in kwargs:
            self.description = kwargs.pop('description')
        changeCommand = False
        if 'changeCommand' in kwargs:
            changeCommand = kwargs.pop('changeCommand')
        collapseCommand = False
        if 'collapseCommand' in kwargs:
            collapseCommand = kwargs.pop('collapseCommand')            
        width = 75
        if 'width' in kwargs:
            width = kwargs.pop('width')
        height = 18
        if 'height' in kwargs:
            height = kwargs.pop('height')            

        # setup
        if parent:
            cmds.setParent(parent)

        # add ui elements
        self.form = cmds.formLayout(parent=parent, height=height)
        command = partial(partial(self.onCollapseButtonPress, collapseCommand))
        color = [1] * 3  
        self.collapseButton = cmds.button(parent=self.form, label='-', height=height, width=height, command = command, bgc=color, annotation='* Click To Collapse Widget')
        #self.collapseButton = cmds.frameLayout(parent=self.form, width = 23, bgc=[1] * 3, collapse=False, collapsable=True, labelVisible = True, label = '', collapseCommand=partial(self.onCollapseButtonPress, collapseCommand))
        self.button = cmds.button(parent=self.form, label=self.description, bgc=[1] * 3, command=partial(self.onButtonPress), height=1)
        self.textField = cmds.textField(parent=self.form, text=self.description, bgc=[.3] * 3, visible=False, height=1)

        # input signals
        cmds.textField(self.textField, edit=True, alwaysInvokeEnterCommandOnReturn=True)
        cmds.textField(self.textField, edit=True, changeCommand=partial(self.onTextChange, changeCommand=changeCommand))
        cmds.textField(self.textField, edit=True, enterCommand=partial(self.onTextChange, changeCommand=changeCommand))

        # setup UI
        cmds.formLayout(self.form, edit=True, attachForm=[(self.collapseButton, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.collapseButton, 'left', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.collapseButton, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachNone=[(self.collapseButton, 'right')])
        
        cmds.formLayout(self.form, edit=True, attachForm=[(self.button, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachControl=[(self.button, 'left', 0, self.collapseButton)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.button, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.button, 'right', 0)])

        cmds.formLayout(self.form, edit=True, attachForm=[(self.textField, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachControl=[(self.textField, 'left', 0, self.collapseButton)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.textField, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.textField, 'right', 0)])        

    def onCollapseButtonPress(self, collapseCommand, *args, **kwargs):
        # reset collapse state
        # cmds.frameLayout( self.collapseButton, edit=True,  collapse=False)
        #cmds.evalDeferred(command)

        # run command
        if collapseCommand:
            try:
                collapseCommand()
            except Exception, e:
                print 3915, e

    def onButtonPress(self, *args, **kwargs):
        # deactivate button
        cmds.button(self.button, edit=True, visible=False)
        
        # enable text field
        cmds.textField(self.textField, edit=True, visible=True)
        
        # set focus
        cmds.setFocus(self.textField)

    def onTextChange(self, *args, **kwargs):
        # pull args
        changeCommand = False
        if 'changeCommand' in kwargs:
            changeCommand = kwargs.pop('changeCommand')
            
        # get new description
        self.description = cmds.textField(self.textField, query=True, text=True)
        
        # validate text
        self.description = self.validateText(self.description)
        
        # hide text field
        hideCommnad = partial(cmds.textField, self.textField, edit=True, visible=False)
        cmds.evalDeferred(hideCommnad)
        # cmds.textField(self.textField, edit=True, visible = False)
        
        # set button label and reactivate
        cmds.button(self.button, edit=True, visible=True)
        cmds.button(self.button, edit=True, label=self.description)
        
        # enable text field
        cmds.textField(self.textField, edit=True, visible=True)
        
        # run command
        if changeCommand:
            changeCommand(self.description)

    def getLayout(self, *args, **kwargs):
        return self.form
    
    def getDescription(self):
        return self.description
    
    def overrideDescription(self, description, *args, **kwargs):
        # set internal data
        self.description = description
        
        # set all ui elements
        cmds.textField(self.textField, edit=True, text=self.description)
        cmds.button(self.button, edit=True, label=self.description)
        
        # set to button display
        hideCommnad = partial(cmds.textField, self.textField, edit=True, visible=False)
        cmds.evalDeferred(hideCommnad)
        cmds.button(self.button, edit=True, visible=True)

    @classmethod
    def validateText(cls, text, *args, **kwargs):
        if not text:
            return False
        validCharacters = " -_.(){0}{1}".format(string.ascii_letters, string.digits)
        validatedCharacters = []
        for c in text:
            '''
            # replace space with underscore
            if c == ' ':
                c = '_'
            '''
            # filter non valid characters
            if c in validCharacters:
                validatedCharacters.append(c)
        # return result
        validatedText = ''.join(validatedCharacters)
        return validatedText


class slider_base:
    """ Define Common Functions for sliders
    """
    instances = []

    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'sliderType'
        if 'sliderType' in kwargs:
            sliderType = kwargs.pop('sliderType')
        self.showMultiplier = False
        if 'showMultiplier' in kwargs:
            self.showMultiplier = kwargs.pop('showMultiplier')
            
        # init multiplier variable
        self.setMultiplier(1.0)
        
        # store instance
        self.instances.append(self)
        
        # set type
        self.setSliderType(sliderType)

        # setup the layout
        self.formLayout = cmds.formLayout(parent=parent, bgc=[0.95] * 3) 

        # set default colors
        buttonBGC = [0.95] * 3

        # make the slider
        self.slider = cmds.floatSlider(parent=self.formLayout, width=5, min=-1, max=1, value=0, step=.1, dragCommand=partial(self.slider_realtime_modifiers, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish_modifiers), bgc=buttonBGC)

        # add multiplier popup
        if self.showMultiplier:
            popupMenu = cmds.popupMenu(parent=self.slider)
            cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.multiplierPopupMenu, parent=popupMenu))
            # add dragger contexts
            # cmds.floatSlider(self.slider, edit=True, dragCallback = partial(self.multiplyDragger_onInitialDrag, self), dropCallback = partial(self.multiplyDragger_onDrop, self))

        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'top', 0)])
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'left', 0)])
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'bottom', 0)])
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'right', 0)])

        # slider defaults
        self.enableSlider = True
    """
    def multiplyDragger_onDrop(self, *args, **kwargs):
        print 'multiplyDragger_onDrop', args, kwargs
        # restore previous context
        # Functions.restorePreviousContext()

    def multiplyDragger_onInitialDrag(self, *args, **kwargs):
        print 'multiplyDragger_onInitialDrag', args, kwargs
        
        # start dragger tool
        Functions.storePreviousContext()
        Functions.ValueDragContextStartTool()
    """    

    def setSliderState(self, state, *args, **kwargs):
        cmds.floatSlider(self.slider, edit=True, enable=state)

    def multiplierPopupMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')

        # clean up
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)

        # current power readout
        multiplier = self.getMultiplier()
        powerMessage = ("Current Power: x{0:.2f}".format(round(multiplier, 2)))
        
        # actions
        cmds.menuItem(parent=parent, label=powerMessage)
        cmds.menuItem(parent=parent, label='Increase Power', command=partial(self.increaseMultiplier))
        cmds.menuItem(parent=parent, label='Decrease Power', command=partial(self.decreaseMultiplier))
        cmds.menuItem(parent=parent, label='Reset Power', command=partial(self.resetMultiplier))

    def increaseMultiplier(self, *args, **kwargs):
        # double multiplier
        self.multiplier = self.multiplier * 2
        # fix if zero
        if self.multiplier == 0:
            self.multiplier = 1

    def decreaseMultiplier(self, *args, **kwargs):
        # double multiplier
        self.multiplier = self.multiplier / 2
        # fix if zero
        if self.multiplier == 0:
            self.multiplier = 1
    
    def resetMultiplier(self, value, *args, **kwargs):
        self.multiplier = 1
    
    def setMultiplier(self, value, *args, **kwargs):
        self.multiplier = value

    def getMultiplier(self, *args, **kwargs):
        try:
            self.multiplier
        except:
            self.multiplier = 1
        return self.multiplier

    def useSetValueCommand(self, *args, **kwargs):
        try:
            # set values
            self.slider_realtime(useSetValue=True)
        except Exception, e:
            print 444, Exception, e
        finally:
            # close command
            self.slider_realtime_finish()

    def presetCommand(self, value, *args, **kwargs):
        try:
            # set values
            self.slider_realtime(overrideRatio=value)
        except Exception, e:
            print 444, Exception, e
        finally:
            # close command
            self.slider_realtime_finish()

    def getBufferSelection(self):
        try:
            self.bufferSelection
        except:
            self.bufferSelection = []
        return self.bufferSelection

    def setBufferSelection(self, selection):
        if selection:
            self.bufferSelection = selection

    def getSelectedChannels(self, *args, **kwargs):
        '''
        overwrite this in widgets if needed
        '''
        selection = Functions.getSelectedChannels(*args, **kwargs)
        
        return selection
    
    def getSelected(self):
        selection = []
        # check for pinned selections
        if self.pinState:
            selection = self.bufferSelection
        else:
            selection = cmds.ls(sl=True, type = ['transform', 'joint'])
        return selection    

    def setBufferChannels(self, selection):
        self.bufferChannels = selection

    def getBufferChannels(self):
        try:
            self.bufferChannels
        except:
            self.bufferChannels = []
        return self.bufferChannels   

    def setPinState(self, state):
        self.pinState = state

    def getPinState(self):
        try:
            self.pinState
        except:
            self.pinState = False
        return self.pinState

    def setUseAllLayersState(self, state):
        self.useAllLayersState = state

    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True
        return self.useAllLayersState

    def addPostCommand(self, command, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        if command:
            self.postCommands.append(command)

    def clearPostCommands(self, *args, **kwargs):
        self.postCommands = []

    def onPost(self, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        for c in self.postCommands:
            c()

    def addPreCommand(self, command, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        if command:
            self.preCommands.append(command)

    def clearPreCommands(self, *args, **kwargs):
        self.preCommands = []

    def onPre(self, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        for c in self.preCommands:
            c()

    def addChangeCommand(self, command, *args, **kwargs):
        try:
            self.changeCommands
        except:
            self.changeCommands = []

        if command:
            self.changeCommands.append(command)

    def clearChangeCommands(self, *args, **kwargs):
        self.changeCommands = []

    def onChange(self, debug=False, *args, **kwargs):
        if debug:
            print debug, len(self.changeCommands)
        try:
            self.multiplierChangeCommands
        except Exception, e:
            self.multiplierChangeCommands = []
        
        # run commands
        for c in self.multiplierChangeCommands:
            c()

    def addMultiplierChangeCommand(self, command, *args, **kwargs):
        try:
            self.multiplierChangeCommands
        except:
            self.multiplierChangeCommands = []

        if command:
            self.multiplierChangeCommands.append(command)

    def clearMultiplierChangeCommands(self, *args, **kwargs):
        self.multiplierChangeCommands = []

    def onMultiplierChange(self, debug=False, *args, **kwargs):
        if debug:
            print debug, len(self.multiplierChangeCommands)
        try:
            self.multiplierChangeCommands
        except Exception, e:
            self.multiplierChangeCommands = []

        # get slider value
        value = self.getSliderValue()
        
        # run commands
        for c in self.multiplierChangeCommands:
            c(value)            

    def addMultiplierPostCommand(self, command, *args, **kwargs):
        try:
            self.multiplierPostCommands
        except:
            self.multiplierPostCommands = []

        if command:
            self.multiplierPostCommands.append(command)

    def clearMultiplierPostCommands(self, *args, **kwargs):
        self.multiplierPostCommands = []

    def onMultiplierPost(self, debug=False, *args, **kwargs):
        if debug:
            print debug, len(self.multiplierPostCommands)
        try:
            self.multiplierPostCommands
        except Exception, e:
            self.multiplierPostCommands = []

        # get slider value
        value = self.getSliderValue()
        
        # run commands
        for c in self.multiplierPostCommands:
            c(value) 

    def getSliderType(self):
        return self.sliderType

    def getLayout(self):
        return self.formLayout

    def collectData(self):
        """
        This will get overwritten to collect data specific to each widget
        """
        pass

    def clearData(self):
        self.data = {}

    def getSliderValue(self):
        """
        return the slider value
        """
        value = cmds.floatSlider(self.slider, query=True, value=True)
        return value

    def slider_exec(self, *args, **kwargs):
        """
        This will perform the actual execution of the data and slider
        """
        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')              

        # get data
        data = self.data
        if data:
            # setup slider value
            sliderValue = self.getSliderValue()
            if type(overrideRatio) != bool:
                sliderValue = overrideRatio
    
            # setup slider related varaibles
            sliderValue = Functions.clamp(sliderValue, -1, 1)
            sliderPos = Functions.clamp(sliderValue, 0, 1)
            sliderNeg = abs(Functions.clamp(sliderValue, -1, 0))
            ratio = (sliderValue + 1) / 2
            ratioInverted = 1 - ratio
            sliderMult = 1.0

            # iterate over data
            '''
            structure
            object.attribute
                         >prevValue
                         >nextValue
                         >currentValue
                         >setValue
                         >isBoring
                         >isIgnored
            
            '''
            for a in data.keys():
                # gather up data
                isBoring = True
                try:
                    '''
                    to optimize performance, isBoring attributes may not have all the the data needed to continue
                    if thats the case the rest of this is simply skipped
                    '''
                    isBoring = data[a]['isBoring']
                except:
                    pass

                # set attributes
                if not isBoring:
                    isIgnored = data[a]['isIgnored']

                    if not isIgnored:
                        # unpack the remaining data
                        prevValue = data[a]['prevValue']
                        nextValue = data[a]['nextValue']
                        currentValue = data[a]['currentValue']
                        setValue = data[a]['setValue']
                        attributeType = data[a]['type']


                        # add in setvalue overwrite
                        newValue = 0
                        if useSetValue:
                            newValue = setValue
                        else:
                            if attributeType != 'enum':
                                # calculate new value
                                if fromCurrentValue:
                                    # blend from current value
                                    newValue = currentValue + ((prevValue - currentValue) * sliderNeg) + ((nextValue - currentValue) * sliderPos)
                                else:
                                    # blend ignoring the current value
                                    newValue = (prevValue * ratioInverted) + (nextValue * ratio)
                            else:
                                # for enums
                                if fromCurrentValue:
                                    # for enums
                                    if sliderValue > 0.5:
                                        newValue = nextValue
                                    elif sliderValue < -0.5:
                                        newValue = prevValue
                                    else:
                                        newValue = currentValue
                                else:
                                    if sliderValue >= 0:
                                        newValue = nextValue
                                    elif sliderValue < 0:
                                        newValue = prevValue
                                    else:
                                        newValue = currentValue
    
                        # set value
                        if newValue != currentValue:
                            cmds.setAttr(a, newValue, clamp=True)

    def slider_realtime_modifiers(self, *args, **kwargs):
                
        # check modifiers, avoid repeatedly checking
        try:
            self.modifierChecked
        except:
            self.modifierChecked = False
        if not self.modifierChecked:
            self.mods = cmds.getModifiers()
            self.modifierChecked = True
        """
        isCtrl = (self.mods & 4) > 0
        isShift = (self.mods & 1) > 0
        isAlt = (self.mods & 8) > 0
        """
        
        if self.showMultiplier and (self.mods & 4) > 0:  # check for control key
            # edit multiplier
            self.editMultiplier_realtime()
        else:
            # pass through
            self.slider_realtime(*args, **kwargs)
        

    def slider_realtime(self, *args, **kwargs):
        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')               

        # run the standard realtime process
        self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)


    def slider_realtime_finish_modifiers(self, *args, **kwargs):
                
        # check modifiers, avoid repeatedly checking
        self.modifierChecked = False
        
        if self.showMultiplier and (self.mods & 4) > 0:  # check for control key
            # edit multiplier
            self.editMultiplier_finish()
        else:
            # pass through
            self.slider_realtime_finish(*args, **kwargs)

    def editMultiplier_realtime(self, *args, **kwargs):
        # get slider value normalize back to 0-1
        value = (((self.getSliderValue() + 1) / 2) ** 2) * 10
        
        # calculate new power
        self.setMultiplier(value)
        
        # run multiplier change commands
        self.onMultiplierChange()        

    def editMultiplier_finish(self, *args, **kwargs):
        # reset slider
        self.resetSlider()
        
        # run post commands
        self.onMultiplierPost()
    
    def slider_realtime_finish(self, *args, **kwargs):
        # abstract this to allow for alternates
        self.slider_realtime_finish_standard()    
    
    def slider_realtime_standard(self, *args, **kwargs):
        """
        This will be the main realtime slider system
        """
        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')              

        # setup loop control
        try:
            self.isFirstLoop
        except:
            self.isFirstLoop = True

        # allow for disabling realtime sliders
        if self.enableSlider:
            if self.isFirstLoop:
                # open new undo chunk
                cmds.undoInfo(openChunk=True)

                # get auto key state
                self.autoKeyState = cmds.autoKeyframe(query=True, state=True)
                cmds.autoKeyframe(edit=True, state=False)

                # indicate that the first loop has happened, reset in non-realtime function
                self.isFirstLoop = False

                # collect data once
                self.collectData()

            # run apply in scene
            self.slider_exec(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)


    def slider_realtime_finish_standard(self, *args, **kwargs):
        """
        This will close the realtime slider functionality
        """

        # indicate slider is finished
        self.isFirstLoop = True

        # set autokeyframe state
        if self.autoKeyState:
            # key all objects
            self.keyAll()

            # turn autokey back on
            cmds.autoKeyframe(edit=True, state=True)

        # close the undo chunk
        cmds.undoInfo(closeChunk=True)

        # reset slider
        self.resetSlider()

    def keyAll(self, *args, **kwargs):
        keyableList = self.data.keys()
        if keyableList:
            cmds.setKeyframe(keyableList)

    def resetSlider(self):
        cmds.floatSlider(self.slider, edit=True, value=0)

    def setSliderType(self, sliderType):
        self.sliderType = sliderType

class slider_tween(slider_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'tweenSlider'

        # inherit class
        slider_base.__init__(self, parent=parent, sliderType=sliderType)

    def collectData(self):
        '''
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        # set wait cursor
        cmds.waitCursor(state=True)
        
        # start fresh
        data = {}
        
        try:

            # get selection and some info
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)

            # iterate through objects
            for s in selection:
                keyableAttributes = Functions.listAttributes(s)
                # keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)

                # go through attributes
                if keyableAttributes:
                    for a in keyableAttributes:
                        # check against highlighted channels
                        if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                            # get info about attributes
                            attribute = '{0}.{1}'.format(s, a)
    
                            # start data entry with initial isBoring attribute
                            data[attribute] = {}
    
                            # keyframe count
                            keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                            isBoring = False
                            if not keyFrameCount >= 2:
                                isBoring = True
    
                            if not isBoring:
                                # current value
                                currentValue = cmds.getAttr(attribute, time=currentTime)
    
                                # get neighboring keys
                                prevKeyFrame = cmds.findKeyframe(s, which='previous', at=a)
                                nextKeyFrame = cmds.findKeyframe(s, which='next', at=a)
    
                                # get neighboring key values
                                prevValue = cmds.getAttr(attribute, t=prevKeyFrame)
                                nextValue = cmds.getAttr(attribute, t=nextKeyFrame)
    
                                # additional boring check
                                if prevValue == nextValue == currentValue:
                                    isBoring = True
    
                                if not isBoring:
                                    # calculate easy tween value
                                    minTime = prevKeyFrame
                                    maxTime = nextKeyFrame
                                    midTime = Functions.clamp(currentTime, minTime, maxTime)
                                    ratio = (midTime - minTime) / (maxTime - minTime)
                                    ratioInverted = 1 - ratio
    
                                    # assign to setValue
                                    setValue = (prevValue * ratioInverted) + (nextValue * ratio)
    
                                    # is ignored to False
                                    isIgnored = False
    
                                    # store to data
                                    data[attribute]['prevValue'] = prevValue
                                    data[attribute]['nextValue'] = nextValue
                                    data[attribute]['currentValue'] = currentValue
                                    data[attribute]['type'] = Functions.getAttributeType(s, a)
                                    data[attribute]['setValue'] = setValue
                                    data[attribute]['isBoring'] = isBoring
                                    data[attribute]['isIgnored'] = isIgnored

        except Exception, e:
            print 1146, Exception, e
        finally:
            # store data to class instance
            self.data = data
            # turn off wait cursor
            cmds.waitCursor(state=False)

    def slider_realtime(self, *args, **kwargs):
        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')            

        # split functions for using/not using all Anim Layers
        if self.getUseAllLayersState():
            # run the standard realtime process
            self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)
        else:
            self.slider_realtime_layers(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish(self, *args, **kwargs):
        # split functions for using/not using all Anim Layers
        if self.getUseAllLayersState():
            # run the standard realtime post process
            self.slider_realtime_finish_standard()
        else:
            self.slider_realtime_finish_layers()

    def slider_realtime_layers(self, *args, **kwargs):
        """
        This will be the main realtime slider system
        """

        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')                

        # setup loop control
        try:
            self.isFirstLoop
        except:
            self.isFirstLoop = True

        # allow for disabling realtime sliders
        if self.enableSlider:
            if self.isFirstLoop:
                # open new undo chunk
                cmds.undoInfo(openChunk=True)

                # get auto key state
                self.autoKeyState = cmds.autoKeyframe(query=True, state=True)
                cmds.autoKeyframe(edit=True, state=False)

                # indicate that the first loop has happened, reset in non-realtime function
                self.isFirstLoop = False

                # collect data once
                self.collectData_layers()

            # run apply in scene
            self.slider_exec_layers(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish_layers(self, *args, **kwargs):
        """
        This will close the realtime slider functionality
        """

        # indicate slider is finished
        self.isFirstLoop = True

        # set autokeyframe state
        if self.autoKeyState:
            # key all objects
            self.keyAll()

            # turn autokey back on
            cmds.autoKeyframe(edit=True, state=True)

        # close the undo chunk
        cmds.undoInfo(closeChunk=True)

        # reset slider
        self.resetSlider()

    def collectData_layers(self):
        '''
        structure, list of actual anim curve nodes
        object_attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''

        # set wait cursor
        cmds.waitCursor(state=True)
        # start fresh
        data = {}
        
        try:
            # get selection and some info
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)

            # iterate through objects
            for s in selection:
                # keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)
                keyableAttributes = Functions.listAttributes(s)
                
                # go through attributes
                for a in keyableAttributes:
                    # check against highlighted channels
                    if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                        # get info about attributes
                        attribute = '{0}.{1}'.format(s, a)
                        curveNode = cmds.keyframe(attribute, query=True, name=True)[0]
                        curveNode_output = '{0}.{1}'.format(curveNode, 'output')

                        # start data entry
                        data[curveNode] = {}
                        isBoring = False

                        # in the event there arent any keys
                        if curveNode:

                            # keyframe count
                            keyFrameCount = cmds.keyframe(curveNode, query=True, keyframeCount=True)
                            if not keyFrameCount >= 2:
                                isBoring = True

                            if not isBoring:
                                # current value
                                currentValue = cmds.getAttr(curveNode_output, time=currentTime)

                                # get neighboring key times
                                prevKeyFrame = cmds.findKeyframe(curveNode, which='previous')
                                nextKeyFrame = cmds.findKeyframe(curveNode, which='next')

                                # get neighboring key values
                                '''
                                *note, did a quick compare of using keyframe vs getAttr
                                for querying 5000 nodes, getAttr was marginally faster
                                '''
                                prevValue = cmds.getAttr(curveNode_output, t=prevKeyFrame)
                                nextValue = cmds.getAttr(curveNode_output, t=nextKeyFrame)

                                # additional boring check
                                if prevValue == nextValue == currentValue:
                                    isBoring = True

                                if not isBoring:
                                    # calculate easy tween value
                                    minTime = prevKeyFrame
                                    maxTime = nextKeyFrame
                                    midTime = Functions.clamp(currentTime, minTime, maxTime)
                                    ratio = (midTime - minTime) / (maxTime - minTime)
                                    ratioInverted = 1 - ratio

                                    # assign to setValue
                                    setValue = (prevValue * ratioInverted) + (nextValue * ratio)

                                    # is ignored to False
                                    isIgnored = False

                                    # set key on the current frame if there isnt one already
                                    keyTimeList = cmds.keyframe(curveNode, query=True)
                                    if currentTime not in keyTimeList:
                                        cmds.setKeyframe(curveNode)

                                    # store the current keyframe index
                                    keyTimeList = cmds.keyframe(curveNode, query=True)
                                    index = keyTimeList.index(currentTime)

                                    # store to data
                                    data[curveNode]['index'] = index
                                    data[curveNode]['prevValue'] = prevValue
                                    data[curveNode]['nextValue'] = nextValue
                                    data[curveNode]['currentValue'] = currentValue
                                    data[curveNode]['type'] = Functions.getAttributeType(s, a)
                                    data[curveNode]['setValue'] = setValue
                                    data[curveNode]['isBoring'] = isBoring
                                    data[curveNode]['isIgnored'] = isIgnored

            
        except Exception, e:
            print 565, Exception, e
        finally:
            # store data to class instance
            self.data = data
            
            # turn off wait cursor
            cmds.waitCursor(state=False)

    def slider_exec_layers(self, *args, **kwargs):
        """
        This will perform the actual execution of the data and slider
        """
        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')              

        # setup slider value
        sliderValue = self.getSliderValue()
        if overrideRatio:
            sliderValue = overrideRatio

        # setup slider related varaibles
        sliderValue = Functions.clamp(sliderValue, -1, 1)
        sliderPos = Functions.clamp(sliderValue, 0, 1)
        sliderNeg = abs(Functions.clamp(sliderValue, -1, 0))
        ratio = (sliderValue + 1) / 2
        ratioInverted = 1 - ratio
        sliderMult = 1.0

        # get data
        data = self.data
        currentTime = cmds.currentTime(query=True)

        # iterate over data
        '''
        structure, list of actual anim curve nodes
        object_attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        if data:
            for curveNode in data.keys():
                # gather up data
                isBoring = True
                try:
                    '''
                    to optimize performance, isBoring attributes may not have all the the data needed to continue
                    if thats the case the rest of this is simply skipped
                    '''
                    isBoring = data[curveNode]['isBoring']
                except:
                    pass

                # set attributes
                if not isBoring:
                    isIgnored = data[curveNode]['isIgnored']

                    if not isIgnored:
                        # unpack the remaining data
                        prevValue = data[curveNode]['prevValue']
                        nextValue = data[curveNode]['nextValue']
                        currentValue = data[curveNode]['currentValue']
                        setValue = data[curveNode]['setValue']
                        index = data[curveNode]['index']
                        attributeType = data[curveNode]['type']

                        # add in setvalue overwrite
                        newValue = 0
                        if useSetValue:
                            newValue = setValue
                        else:
                            if attributeType != 'enum':
                                # calculate new value
                                if fromCurrentValue:
                                    # blend from current value
                                    newValue = currentValue + ((prevValue - currentValue) * sliderNeg) + ((nextValue - currentValue) * sliderPos)
                                else:
                                    # blend ignoring the current value
                                    newValue = (prevValue * ratioInverted) + (nextValue * ratio)
                            else:
                                # for enums
                                if fromCurrentValue:
                                    # for enums
                                    if sliderValue > 0.5:
                                        newValue = nextValue
                                    elif sliderValue < -0.5:
                                        newValue = prevValue
                                    else:
                                        newValue = currentValue
                                else:
                                    if sliderValue >= 0:
                                        newValue = nextValue
                                    elif sliderValue < 0:
                                        newValue = prevValue
                                    else:
                                        newValue = currentValue

                        # set value
                        if newValue != currentValue:
                            cmds.setAttr('{0}.keyTimeValue[{1}].keyValue'.format(curveNode, index), newValue)

class slider_snapshot(slider_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'snapshotSlider'

        # inherit class
        slider_base.__init__(self, parent=parent, sliderType=sliderType)
        
        # modify slider range
        cmds.floatSlider(self.slider, edit=True, min=0, max=1)

    def collectData(self):
        '''
        rebuild new data from snapshot data
        '''
        # collectData
        data = {}
        
        # get snapshot data
        snapshotData = self.getSnapshotData()
        # print 4702, 'snapshotData', snapshotData
        if snapshotData:
            
            # setup namespace behavior
            selection = cmds.ls(sl=True)
            selectedNamespaces = set(Functions.getNamespaces(nodes=selection))
            snapshotDataNodes = snapshotData.keys()
            snapShotDataNamespaceList = set(Functions.getNamespaces(nodes=snapshotDataNodes))

            # create a remap lookup table
            remapLookup = {}
            for snapshotNode in snapshotDataNodes:
                # create node key
                remapLookup[snapshotNode] = []
                
                # if nothing selection apply to original OR something with same namespace selection
                if not selection or selectedNamespaces == snapShotDataNamespaceList:
                    # no change
                    remapLookup[snapshotNode] = [snapshotNode]  # this needs to be a list
                elif selectedNamespaces != snapShotDataNamespaceList:
                    remapLookup[snapshotNode] = Functions.findMatchingObjectsInNamespace(node=snapshotNode, namespaces=selectedNamespaces)
            
            # merge data
            '''
            structure
            object.attribute
                         >prevValue
                         >nextValue
                         >currentValue
                         >type                         
                         >setValue
                         >isBoring
                         >isIgnored
            
            '''
            # set wait cursor
            cmds.waitCursor(state=True)
            
            # start fresh
            data = {}
            
            try:
                # get selection and some info
                
                # snapshotNodes = remapLookup.keys()
                selection = cmds.ls(sl=True)
                selectedChannels = self.getSelectedChannels(selection=selection)
                currentTime = cmds.currentTime(query=True)
    
                # iterate through objects
                # print 4751, 'remapLookup', remapLookup
                for snapshotNode in remapLookup.keys():
                    for s in remapLookup[snapshotNode]:
                        # keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)
                        keyableAttributes = Functions.listAttributes(s, filterEnums=False)
                        snapshotDataAttributes = snapshotData[snapshotNode].keys()
                        commonAttributes = list(set(keyableAttributes) & set(snapshotDataAttributes))
        
                        # go through attributes
                        if commonAttributes:
                            for a in commonAttributes:
                                # check against highlighted channels
                                if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                                    # get info about attributes
                                    attribute = '{0}.{1}'.format(s, a)
            
                                    # start data entry with initial isBoring attribute
                                    data[attribute] = {}
            
                                    # setup is boring
                                    isBoring = False
                                    '''
                                    # keyframe count
                                    keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                                    
                                    if not keyFrameCount >= 2:
                                        isBoring = True
                                    '''
                                    if not isBoring:
                                        # current value
                                        currentValue = cmds.getAttr(attribute, time=currentTime)
            
                                        # get neighboring keys
                                        # prevKeyFrame = cmds.findKeyframe(s, which='previous', at=a)
                                        # nextKeyFrame = cmds.findKeyframe(s, which='next', at=a)
     
            
                                        # get neighboring key values
                                        # prevValue = cmds.getAttr(attribute, t=prevKeyFrame)\
                                        prevValue = False
                                        # nextValue = cmds.getAttr(attribute, t=nextKeyFrame)
                                        nextValue = snapshotData[snapshotNode][a]['nextValue']
            
                                        # additional boring check
                                        if currentValue == nextValue:
                                            isBoring = True
            
                                        if not isBoring:
                                            '''
                                            # calculate easy tween value
                                            minTime = prevKeyFrame
                                            maxTime = nextKeyFrame
                                            midTime = Functions.clamp(currentTime, minTime, maxTime)
                                            ratio = (midTime - minTime) / (maxTime - minTime)
                                            ratioInverted = 1 - ratio
                                            '''
                                            
                                            # assign to setValue
                                            # setValue = (prevValue * ratioInverted) + (nextValue * ratio)
                                            setValue = False
            
                                            # is ignored to False
                                            isIgnored = False
            
                                            # store to data
                                            data[attribute]['prevValue'] = prevValue
                                            data[attribute]['nextValue'] = nextValue
                                            data[attribute]['currentValue'] = currentValue
                                            data[attribute]['type'] = Functions.getAttributeType(s, a)
                                            data[attribute]['setValue'] = setValue
                                            data[attribute]['isBoring'] = isBoring
                                            data[attribute]['isIgnored'] = isIgnored
        
            except Exception, e:
                print 4255, Exception, e
            finally:
                # store data to class instance
                self.data = data
                # turn off wait cursor
                cmds.waitCursor(state=False)
                
    def collectSnapshotData(self):
        # set only next attributes
        '''
        object
                >attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        # set wait cursor
        cmds.waitCursor(state=True)
        
        # start fresh
        data = {}
        
        try:
            # get selection and some info
            selection = self.getSelected()
            if selection:
                selectedChannels = self.getSelectedChannels(selection=selection)
                currentTime = cmds.currentTime(query=True)
    
                # iterate through objects
                for s in selection:
                    # setup data
                    data[s] = {}
                    
                    # get keyable attributes
                    # keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)
                    keyableAttributes = Functions.listAttributes(s, filterEnums=False)
    
                    # go through attributes
                    if keyableAttributes:
                        for a in keyableAttributes:
                            # check against highlighted channels
                            if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                                # get info about attributes
                                attribute = '{0}.{1}'.format(s, a)
                                # attribute = a
        
                                # start data entry with initial isBoring attribute
                                data[s][a] = {}
        
                                # set is boring
                                isBoring = False
                                """
                                # keyframe count
                                keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                                
                                if not keyFrameCount >= 2:
                                    isBoring = True
                                """
                                if not isBoring:
                                    # current value
                                    # currentValue = cmds.getAttr(attribute, time=currentTime)
                                    currentValue = False
        
                                    # get neighboring keys
                                    # prevKeyFrame = cmds.findKeyframe(s, which='previous', at=a)
                                    prevKeyFrame = False
                                    nextKeyFrame = cmds.findKeyframe(s, which='next', at=a)
        
                                    # get neighboring key values
                                    # prevValue = cmds.getAttr(attribute, t=prevKeyFrame)
                                    prevValue = False
                                    nextValue = cmds.getAttr(attribute, t=currentTime)
        
                                    # additional boring check
                                    """
                                    if prevValue == nextValue == currentValue:
                                        isBoring = True
                                    """
                                    
                                    if not isBoring:
                                        """
                                        # calculate easy tween value
                                        minTime = prevKeyFrame
                                        maxTime = nextKeyFrame
                                        midTime = Functions.clamp(currentTime, minTime, maxTime)
                                        ratio = (midTime - minTime) / (maxTime - minTime)
                                        ratioInverted = 1 - ratio
                                        """
        
                                        # assign to setValue
                                        # setValue = (prevValue * ratioInverted) + (nextValue * ratio)
                                        setValue = False
        
                                        # is ignored to False
                                        isIgnored = False
        
                                        # store to data
                                        data[s][a]['prevValue'] = prevValue
                                        data[s][a]['nextValue'] = nextValue
                                        data[s][a]['currentValue'] = currentValue
                                        data[s][a]['setValue'] = setValue
                                        data[s][a]['isBoring'] = isBoring
                                        data[s][a]['isIgnored'] = isIgnored
        except Exception, e:
            print 4937, e
        finally:
            # store data to class instance
            self.setSnapshotData(data)
            # print 4938, 'data', data
            # turn off wait cursor
            cmds.waitCursor(state=False)
            
    def setSnapshotData(self, data):
        self.snapShotData = data

    def getSnapshotData(self):
        try:
            self.snapShotData
        except:
            self.snapShotData = {}
        return self.snapShotData

class slider_worldSpace(slider_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'tweenSlider'

        # inherit class
        slider_base.__init__(self, parent=parent, sliderType=sliderType)

    def collectData(self):
        '''
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        # set wait cursor
        cmds.waitCursor(state=True)
        # start fresh
        data = {}
        
        try:

            # get selection and some info
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)
            translateAttributes = ['tx', 'ty', 'tz']
            rotateAttributes = ['rx', 'ry', 'rz']
            transformAttributes = translateAttributes + rotateAttributes
    
            # iterate through objects
            if selection:
                for s in selection:
                    # keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)
                    keyableAttributes = Functions.listAttributes(s)
                    
                    # keyframe count, make sure one of the transforms has at least 2 + keys
                    isBoring = False
                    for a in transformAttributes:
                        attribute = '{0}.{1}'.format(s, a)
                        keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                        isBoring = True
                        if keyFrameCount and keyFrameCount >= 1: # allow for just one key
                            isBoring = False
                            break
                    
                    if not isBoring:
                        # current values
                        """
                        currentTransform = [False, False, False, False, False, False]
                        attribute = '{0}.{1}'.format(s, 'tx')
                        currentTransform[0] = cmds.getAttr(attribute, time=currentTime)
                        attribute = '{0}.{1}'.format(s, 'ty')
                        currentTransform[1] = cmds.getAttr(attribute, time=currentTime)    
                        attribute = '{0}.{1}'.format(s, 'tz')
                        currentTransform[2] = cmds.getAttr(attribute, time=currentTime)   
                        attribute = '{0}.{1}'.format(s, 'rx')
                        currentTransform[3] = cmds.getAttr(attribute, time=currentTime)
                        attribute = '{0}.{1}'.format(s, 'ry')
                        currentTransform[4] = cmds.getAttr(attribute, time=currentTime)    
                        attribute = '{0}.{1}'.format(s, 'rz')
                        currentTransform[5] = cmds.getAttr(attribute, time=currentTime) 
                        """
                                
                        # get neighboring keys
                        prevKeyFrame = cmds.findKeyframe(s, which='previous', at=transformAttributes)
                        nextKeyFrame = cmds.findKeyframe(s, which='next', at=transformAttributes)
                        
                        # for when there is only one keyframe, validate previous and next times
                        '''
                        If there isnt a prev/next key, it will return whatever key time is present
                        if this is the case, use the current time as a substitute
                        '''
                        prevKeyFrame = min(prevKeyFrame, currentTime )
                        nextKeyFrame = max(nextKeyFrame, currentTime )
    
                        # get values
                        prev_worldMatrix = OpenMaya.MMatrix(cmds.getAttr((s + '.worldMatrix'), time=prevKeyFrame))
                        curr_worldMatrix = OpenMaya.MMatrix(cmds.getAttr((s + '.worldMatrix'), time=currentTime))
                        next_worldMatrix = OpenMaya.MMatrix(cmds.getAttr((s + '.worldMatrix'), time=nextKeyFrame))
                        current_ParentMatrix = OpenMaya.MMatrix(cmds.getAttr((s + '.parentInverseMatrix'), time=currentTime))
                        
                        # get local matricies
                        prev_localMatrix = prev_worldMatrix * current_ParentMatrix
                        curr_localMatrix = curr_worldMatrix * current_ParentMatrix
                        next_localMatrix = next_worldMatrix * current_ParentMatrix
                        
                        # get local values
                        prev_localValues = Functions.decompMatrix(s, prev_localMatrix)
                        curr_localValues = Functions.decompMatrix(s, curr_localMatrix)
                        next_localValues = Functions.decompMatrix(s, next_localMatrix)
                        
                        # itterate 
                        for i, a in enumerate(transformAttributes): 
                            # check against keyable
                            if a in keyableAttributes:
                                # check against selection channels
                                if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                                    # check that values had changed
                                    if not prev_localValues[i] == curr_localValues[i] == next_localValues[i]:
                                        # get info about attributes
                                        attribute = '{0}.{1}'.format(s, a)
                
                                        # start data entry with initial isBoring attribute
                                        data[attribute] = {}
                                        
                                        # unpack
                                        prevValue = prev_localValues[i]
                                        currValue = curr_localValues[i]
                                        nextValue = next_localValues[i]
                                        
                                        # calculate easy tween value
                                        minTime = prevKeyFrame
                                        maxTime = nextKeyFrame
                                        midTime = Functions.clamp(currentTime, minTime, maxTime)
                                        ratio = (midTime - minTime) / (maxTime - minTime)
                                        ratioInverted = 1 - ratio
                    
                                        # assign to setValue
                                        setValue = (prevValue * ratioInverted) + (nextValue * ratio)
                    
                                        # is ignored to False
                                        isIgnored = False
                                        
                                        # store to data
                                        data[attribute]['prevValue'] = prevValue
                                        data[attribute]['nextValue'] = nextValue
                                        data[attribute]['currentValue'] = currValue
                                        data[attribute]['type'] = False  # not needed here
                                        data[attribute]['setValue'] = setValue
                                        data[attribute]['isBoring'] = isBoring
                                        data[attribute]['isIgnored'] = isIgnored

        except Exception, e:
            print traceback.format_exc()
            print 5495, Exception, e
            # might still have a shape selected, just clear selection
            cmds.select(clear=True)
        finally:
        # store data to class instance
            self.data = data
            
            # turn off wait cursor
            cmds.waitCursor(state=False)
            
class slider_inOut(slider_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'inOutSlider'
        
        # show multiplier popup
        showMultiplier = True

        # inherit class
        slider_base.__init__(self, parent=parent, sliderType=sliderType, showMultiplier=showMultiplier)
        
        # set multiplier default
        self.setMultiplier(1.0)           

    def collectData(self):
        '''
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        # set wait cursor
        cmds.waitCursor(state=True)
        # start fresh
        data = {}
        
        # get multiplier
        multiplier = self.getMultiplier() * 3
        
        try:
            # get selection and some info
            selection = self.getSelected()
            activeCamera = Functions.getActiveCamera()
            selectedChannels = self.getSelectedChannels(selection=selection)
            limitedAttributes = ['tx', 'ty', 'tz']
            averageBoundingBoxSize = Functions.getAverageBoundingBoxSize(selection) * multiplier
            print 5982, 'averageBoundingBoxSize', averageBoundingBoxSize
            
            # iterate through objects
            if selection and activeCamera:
                # get camera world matrix
                worldMatrixCamera = OpenMaya.MMatrix(cmds.getAttr((activeCamera + '.worldMatrix')))
                worldSpaceCamera = Functions.decompMatrix(activeCamera, worldMatrixCamera)
                
                # itterate 
                for s in selection:
                    # keyableAttributes_raw = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)
                    keyableAttributes_raw = Functions.listAttributes(s)
                    
                    # intersect keyable list with translate attributes
                    keyableAttributes = list(set(keyableAttributes_raw) & set(limitedAttributes))
                    if selectedChannels:
                        keyableAttributes = list(set(keyableAttributes) & set(selectedChannels))
                    #
                    if keyableAttributes:
    
                        # setup
                        isBoring = False
    
                        # current values
                        worldMatrix = OpenMaya.MMatrix(cmds.getAttr((s + '.worldMatrix')))
                        worldSpaceVectorCurrent = OpenMaya.MVector(Functions.decompMatrix(s, worldMatrix)[:3])  # just get the translates
                        
                        # vector to camera
                        cameraVector = OpenMaya.MVector((worldSpaceVectorCurrent[0] - worldSpaceCamera[0]), (worldSpaceVectorCurrent[1] - worldSpaceCamera[1]), (worldSpaceVectorCurrent[2] - worldSpaceCamera[2]))
                        # normalize and multiply by average bounding box size
                        cameraVector = cameraVector.normal() * averageBoundingBoxSize
                        
                        # setup in/out worldspace positions
                        worldSpaceVectorIn = worldSpaceVectorCurrent + cameraVector
                        worldSpaceVectorOut = worldSpaceVectorCurrent - cameraVector
                        
                        # setup local values
                        attribute = '{0}.{1}'.format(s, 'tx')
                        localSpaceCurrentX = cmds.getAttr(attribute)
                        attribute = '{0}.{1}'.format(s, 'ty')
                        localSpaceCurrentY = cmds.getAttr(attribute)
                        attribute = '{0}.{1}'.format(s, 'tz')
                        localSpaceCurrentZ = cmds.getAttr(attribute)                                                
                        localSpaceCurrent = [localSpaceCurrentX, localSpaceCurrentY, localSpaceCurrentZ]
                        
                        localSpaceCurrent = Functions.worldToLocalPoint(worldSpaceVectorCurrent, s)
                        localSpaceIn = Functions.worldToLocalPoint(worldSpaceVectorIn, s)
                        localSpaceOut = Functions.worldToLocalPoint(worldSpaceVectorOut, s)
    
                        # itterate 
                        for a in keyableAttributes: 
                            # lookup index 
                            indexLookup = limitedAttributes.index(a)
                            
                            # unpack
                            prevValue = localSpaceIn[indexLookup]
                            currValue = localSpaceCurrent[indexLookup]
                            nextValue = localSpaceOut[indexLookup]
                            
                            # check that values had changed
                            if not prevValue == currValue == nextValue:
                                # get info about attributes
                                attribute = '{0}.{1}'.format(s, a)
        
                                # start data entry with initial isBoring attribute
                                data[attribute] = {}
            
                                # assign to setValue
                                setValue = 0
            
                                # is ignored to False
                                isIgnored = False
                                
                                # store to data
                                data[attribute]['prevValue'] = prevValue
                                data[attribute]['nextValue'] = nextValue
                                data[attribute]['currentValue'] = currValue
                                data[attribute]['type'] = False  # not needed here
                                data[attribute]['setValue'] = setValue
                                data[attribute]['isBoring'] = isBoring
                                data[attribute]['isIgnored'] = isIgnored
                                     

        except Exception, e:
            print traceback.format_exc()
            print 5633, Exception, e
        finally:
            # store data to class instance
            self.data = data
            
            # turn off wait cursor
            cmds.waitCursor(state=False)            


class slider_PosePusher(slider_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'posePusherSlider'

        # show multiplier popup
        showMultiplier = True

        # inherit class
        slider_base.__init__(self, parent=parent, sliderType=sliderType, showMultiplier=showMultiplier)
        
        # set multiplier default
        self.setMultiplier(1.0)

    def collectData(self):
        '''
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type                                          
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        # set wait cursor
        cmds.waitCursor(state=True)
        
        # start fresh
        data = {}
        
        # get multiplier
        multiplier = self.getMultiplier() * 5   
        
        try:

            # get selection and some info
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)

            # iterate through objects
            for s in selection:
                keyableAttributes = Functions.listAttributes(s)
                # keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)

                # go through attributes
                if keyableAttributes:
                    for a in keyableAttributes:
                        # check against highlighted channels
                        if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                            # get info about attributes
                            attribute = '{0}.{1}'.format(s, a)
    
                            # start data entry with initial isBoring attribute
                            data[attribute] = {}
    
                            # keyframe count
                            keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                            isBoring = False
                            if not keyFrameCount >= 2:
                                isBoring = True
    
                            if not isBoring:
                                # current value
                                currentValue = cmds.getAttr(attribute, time=currentTime)
                                midValue = float(currentValue)  # make a copy here
                                midTime = currentTime
    
                                # set neighboring key lookups
                                '''
                                'Before', 'First','OnKey', 'InKeys', 'Last', 'After'
                                '''
                                previousLookup = -1
                                nextLookup = 1
                                midLookup = False 
                                relativePosition = Functions.getRelativePosition(s, a, currentTime)
                                if relativePosition == 'Before':
                                    midLookup = 1
                                    previousLookup = 1  
                                    nextLookup = 2
                                if relativePosition == 'After':
                                    midLookup = -1
                                    previousLookup = -2 
                                    nextLookup = -1                                
                                
                                # get neighboring keys
                                prevKeyTime, prevValueRaw = Functions.getKeyFrameAtOffsetInfo(s, a, previousLookup) 
                                nextKeyTime, nextValueRaw = Functions.getKeyFrameAtOffsetInfo(s, a, nextLookup) 
                                if midLookup:
                                    midTime, midValue = Functions.getKeyFrameAtOffsetInfo(s, a, midLookup) 
                                
                                # normalize times
                                PrevNormalizeKeyFrame = abs(midTime - prevKeyTime)  # abs(midTime - prevKeyTime)
                                if PrevNormalizeKeyFrame == 0:
                                    PrevNormalizeKeyFrame = 1
                                NextNormalizeKeyFrame = abs(nextKeyTime - midTime)  # abs(nextKeyTime - midTime)
                                if NextNormalizeKeyFrame == 0:
                                    NextNormalizeKeyFrame = 1                                
                                
                                # calculate new target values, these are projections so the inputs are swapped
                                prevValue = midValue + ((midValue - nextValueRaw) / NextNormalizeKeyFrame * multiplier)
                                nextValue = midValue + ((midValue - prevValueRaw) / PrevNormalizeKeyFrame * multiplier)
                                
                                # print 3888, 'prevKeyTime:', prevKeyTime, ' ,midTime:', midTime, ' ,nextKeyTime:', nextKeyTime
                                
                                # additional boring check
                                if prevValue == nextValue == currentValue:
                                    isBoring = True
    
                                if not isBoring:
                                    # assign to setValue
                                    setValue = 0
    
                                    # is ignored to False
                                    isIgnored = False
    
                                    # store to data
                                    data[attribute]['prevValue'] = prevValue
                                    data[attribute]['nextValue'] = nextValue
                                    data[attribute]['currentValue'] = currentValue
                                    data[attribute]['type'] = Functions.getAttributeType(s, a)
                                    data[attribute]['setValue'] = setValue
                                    data[attribute]['isBoring'] = isBoring
                                    data[attribute]['isIgnored'] = isIgnored

        except Exception, e:
            print 1146, Exception, e
        finally:
            # store data to class instance
            self.data = data
            # turn off wait cursor
            cmds.waitCursor(state=False)

class slider_multiply(slider_base):
    # inherit widget base
    def __init__(self, *args, **kwargs):
        # pull args
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'multiplySlider'

        # show multiplier popup
        showMultiplier = True

        # inherit class
        slider_base.__init__(self, parent=parent, sliderType=sliderType, showMultiplier=showMultiplier)
        
        # set multiplier default
        self.setMultiplier(1.0)

    def collectData(self):
        '''
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        '''
        # set wait cursor
        cmds.waitCursor(state=True)
        
        # start fresh
        data = {}
        
        # get multiplier
        multiplier = self.getMultiplier() * 2
        
        try:

            # get selection and some info
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            limitedAttributes = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            blackListAttributes = ['sx', 'sy', 'sz', 'v']
            currentTime = cmds.currentTime(query=True)

            # iterate through objects
            for s in selection:
                                
                # intersect keyable list with translate attributes
                keyableAttributes = []
                # override with selected
                if selectedChannels:
                    # keyableAttributes = list(set(keyableAttributes) & set(selectedChannels))
                    # allow for arbitrary channels when something selected
                    keyableAttributes = list(set(selectedChannels))
                else:
                    keyableAttributes_raw = Functions.listAttributes(s)
                    '''
                    more attributes
                    '''
                    #keyableAttributes = list(set(keyableAttributes_raw) - set(blackListAttributes))
                    '''
                    limited attrributes
                    '''
                    keyableAttributes = list(set(keyableAttributes_raw) & set(limitedAttributes))
                    
                # go through attributes
                if keyableAttributes:
                    for a in keyableAttributes:
                        # check against highlighted channels
                        # if (selectedChannels and a in selectedChannels) or (not selectedChannels):
                        # get info about attributes
                        attribute = '{0}.{1}'.format(s, a)

                        # start data entry with initial isBoring attribute
                        data[attribute] = {}
                        
                        # setup is boring check
                        isBoring = False
                        """
                        # keyframe count
                        keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                        
                        if not keyFrameCount >= 2:
                            isBoring = True
                        """
                        if not isBoring:
                            # current value
                            currentValue = cmds.getAttr(attribute, time=currentTime)
                        
                            
                            # calculate new target values, these are projections so the inputs are swapped
                            prevValue = 0
                            nextValue = currentValue * multiplier
                            
                            # additional boring check
                            if prevValue == nextValue == currentValue:
                                isBoring = True

                            if not isBoring:
                                # assign to setValue
                                setValue = 0

                                # is ignored to False
                                isIgnored = False

                                # store to data
                                data[attribute]['prevValue'] = prevValue
                                data[attribute]['nextValue'] = nextValue
                                data[attribute]['currentValue'] = currentValue
                                data[attribute]['type'] = False  # not needed here
                                data[attribute]['setValue'] = setValue
                                data[attribute]['isBoring'] = isBoring
                                data[attribute]['isIgnored'] = isIgnored

        except Exception, e:
            print 1146, Exception, e
        finally:
            # store data to class instance
            self.data = data
            # turn off wait cursor
            cmds.waitCursor(state=False)

    def slider_realtime(self, *args, **kwargs):
        # pull args
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')            
        
        # check modifiers
        mods = cmds.getModifiers()
        isCtrl = (mods & 4) > 0
        isShift = (mods & 1) > 0
        isAlt = (mods & 8) > 0
        
        # split functions for using/not using all Anim Layers
        if self.getUseAllLayersState():
            # run the standard realtime process
            self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)
        else:
            self.slider_realtime_layers(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish(self, *args, **kwargs):
        # split functions for using/not using all Anim Layers
        if self.getUseAllLayersState():
            # run the standard realtime post process
            self.slider_realtime_finish_standard()
        else:
            self.slider_realtime_finish_layers()

        
'''
import sys
sys.path.append('/home/ericb/GIT_DEV/ebLabs-workshop/whisKEY2')
import ebLabs_whisKEY
reload(ebLabs_whisKEY)
ebLabs_whisKEY.window.load()
'''
