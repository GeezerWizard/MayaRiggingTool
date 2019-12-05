import maya.cmds as cmds
#THINGS TO DO
#Exclude helper joints from having nulls created
winID="Rigging_Assistant"
tipsText="   This is a nulls based rigging tool. It relies on '_JNT', '_CTRL' and '_NULL' to be used correctly."
shade=0.285
boxColour=( shade, shade, shade )
# - Making the Window
def ui():
    if( cmds.window( winID, exists=True ) ):
        cmds.deleteUI( winID )
    cmds.window( winID, t="Dave's Simple RigAssist" )
    middleColumn = CreateHeader()
#FRAME 1 Layout - Suffixes, prefixes----------------------------------------------------------------
    frameNaming = CreateFrame( 'Naming Tool', 'Add suffixes and prefixes to your objects.', middleColumn )
# - Suffix
    suffixField = cmds.textFieldGrp( l='Suffix:', p=frameNaming)
    cmds.textFieldGrp( suffixField, e=True, tx='_JNT' )
    cmds.rowLayout( nc=2 )
    cmds.button( l='Apply to All Joints', c=lambda *x: ApplyNameAddition(suffixField, True, True) )
    cmds.button( l='Apply to Selection', c=lambda *x: ApplyNameAddition(suffixField, True, False) )
# - Prefix
    prefixField=cmds.textFieldGrp( l='Prefix:', p=frameNaming )
    cmds.textFieldGrp( prefixField, e=True, tx='L_' )
    cmds.rowLayout( nc=2, p=frameNaming )
    cmds.button( l='Apply to Hierarchy', c=lambda *x: ApplyNameAddition(prefixField, False, False) )
    cmds.separator( style='none', h=20, p=frameNaming )
#FRAME 2 Layout - Controllers-----------------------------------------------------------------------
    frameControllers = CreateFrame( 'Controller Creator', 'Creates controllers for all or select joints.', middleColumn )
    ctrlNurbRadio = cmds.radioButtonGrp( l='Controller Type:', la3=['Circle', 'Square', 'Box'], nrb=3 )
    ctrlSelectRadio = cmds.radioButtonGrp( l='For:', la2=['All Joints', 'Selection'], nrb=2 )
    ctrlSizeFloat = cmds.floatSliderGrp( l='Size', field=True, minValue=0, maxValue=15 )
    cmds.button( l='Create Controls', c=lambda *x: CreateControllers(cmds.radioButtonGrp(ctrlNurbRadio,q=True,sl=True), cmds.radioButtonGrp(ctrlSelectRadio,q=True,sl=True), cmds.floatSliderGrp(ctrlSizeFloat, q=True, v=True) ) )
    cmds.separator( style='none', h=20 )
#FRAME 3 Layout - Nulls-----------------------------------------------------------------------------
    frameNulls = CreateFrame( 'Create Nulls', 'Generates Nulls and Constraints based on existing Controls.', middleColumn )
    cmds.rowLayout( nc=2, p=frameNulls )
    topJointBox = cmds.checkBox( l='Do not create for top joints (i.e. root joints)')
    parentAndFreezeBox = cmds.checkBox( l='Parent and Freeze Controls to Created Nulls')
    cmds.button( l='Create Nulls', c=lambda *x: CreateNullForEachCtrl(cmds.checkBox(topJointBox, q=True, v=True), cmds.checkBox(parentAndFreezeBox, q=True, v=True)), p=frameNulls )
#Frame 4 Layout - Constraints-----------------------------------------------------------------------
    frameConstraints = CreateFrame( 'Create Constraints', 'Automagically does all the constraining.', middleColumn )
    cmds.button( l='Constrain Joints to Controls', c=lambda *x: ConstrainJointsToControls())
    cmds.button( l='Constrain Upward Joints to Downward Nulls', c=lambda *x: ConstrainUpJntsToDownNulls())
    cmds.separator( style='none', h=20, p=frameNulls )

#Brings the window into existence.
    cmds.showWindow( winID )
    cmds.window( winID, e=True, wh=(550, 550) )

# - Naming Tools -
def ApplyNameAddition( txtFieldID, isSuffix, forJoints ):
    nameAddition = cmds.textFieldGrp(txtFieldID, query=True, text=True )#gets text to add as suffix
    if( forJoints==True ):
        toRename=cmds.ls( typ='joint' )
    if( forJoints==False ):
        toRename=cmds.ls( sl=True )
        if( isSuffix==False ):
            cmds.select( cmds.ls(sl=True), hi=True )
            toRename=cmds.ls( sl=True )
    for x in toRename:
        if( x.endswith(nameAddition)==False )and( isSuffix==True ):
            newName=x+nameAddition
        if( x.startswith(nameAddition)==False )and( isSuffix==False ):
            newName=nameAddition+x
        else:
            print( 'ERROR: '+x+' already contains '+nameAddition )
        cmds.rename( x, newName )
        print( x )

# - Controllers -
def CreateControllers( nurbGrp, selectGrp, size):
    print(selectGrp)
    print(nurbGrp)
    isJoint=selectGrp
    nurbType=nurbGrp
    if( isJoint==1 ):
        selection=cmds.ls( typ='joint' )
    if( isJoint==2 ):
        selection=cmds.ls( sl=True )
    axis=2
    offset=90
    isAppendSuffix=True
    ctrlSuffix='_CTRL'
    for eachObject in selection:
        if( eachObject.endswith('_JNT') ):
            print('Created Controller for joint: '+eachObject)
        ctrlName=eachObject.replace( '_JNT', ctrlSuffix)
        jointTranslate = cmds.xform(eachObject, translation = True, q = True, ws = True)
        jointRotate = cmds.xform(eachObject, rotation = True, q = True, ws = True)
        jointRotate[axis] = jointRotate[axis] + offset
        if( nurbType==1 ):
            newController = cmds.circle( n=ctrlName, nr=(0, 0, 0), c=(0, 0, 0), r=size )
        if( nurbType==2 ):
            newController = CreateCustomNurbsCurve( ctrlName, 'Square', size )
        if( nurbType==3 ):
            newController = CreateCustomNurbsCurve( ctrlName, 'Cube', size )
        cmds.xform(newController, translation = jointTranslate, rotation = jointRotate, ws = True)
        #cmds.xform(newController, rotation = jointRotate, ws = True)

# - Nulls - 
def CreateCustomNurbsCurve( jointName, nurbShape, nurbSize ):
    newName=jointName.replace( '_JNT', '_CTRL' )
    newNurb=cmds.group( em=True, n=newName )
    if( nurbShape=='Square' ):
        tempNurb=cmds.nurbsPlane( p=(0, 0, 0), ax=(0, 1, 0), w=nurbSize, ch=0)
    if( nurbShape=='Cube' ):
        tempNurb=cmds.nurbsCube( p=(0, 0, 0), ax=(0, 1, 0), w=nurbSize, ch=0)
    cmds.DuplicateCurve();
    shapes = cmds.listRelatives('duplicatedCurve*', c=True, s=True)
    cmds.select( shapes, r=True );
    cmds.select( newNurb, add=True );
    cmds.parent( r=True, s=True );
    cmds.select( 'duplicatedCurve*', r=True );
    cmds.select( 'duplicatedCurveShape*', d=True );
    cmds.select( tempNurb, add=True );
    cmds.delete();
    return newNurb

def CreateNullForEachCtrl(ignoreHeadJnts, parentAndFreeze): #only create nulls where there are curves.
    ctrls = SearchFor('_CTRL')
    jnts = SearchFor('_JNT')
    toRemove = []
    newCtrls = []
    if( ignoreHeadJnts==True ):
        relatives = cmds.listRelatives(jnts, c=True)
        jnts = [x for x in jnts if x not in relatives]
        for jnt in jnts:
            tempName = jnt.replace('_JNT', '_CTRL')
            toRemove.append(tempName)
        ctrls = [x for x in ctrls if x not in toRemove]
    for ctrl in ctrls:
        newName = ctrl.replace('_CTRL', '_NULL')
        toJoint = ctrl.replace('_CTRL', '_JNT')
        cmds.select(toJoint)
        newNull = cmds.group(em=True, n=newName, p=toJoint)
        cmds.parent(newNull, w=True)
    if(parentAndFreeze==True):
        ParentAndFreeze(ctrls)

def ParentAndFreeze(ctrls):
#    ctrls = SearchFor('_CTRL')
    for ctrl in ctrls:
        toNull = ctrl.replace('_CTRL', '_NULL')
        cmds.parent(ctrl, toNull)
        cmds.makeIdentity( ctrl, apply=True )

# - Constraints - 
def ConstrainJointsToControls():
    ctrls = SearchFor('_CTRL')
    for ctrl in ctrls:
        forJnt = ctrl.replace('_CTRL', '_JNT')
        cmds.parentConstraint(ctrl, forJnt)

def ConstrainUpJntsToDownNulls():
    nulls = SearchFor('_NULL')
    ctrls = SearchFor('_CTRL')
    ctrlJnts = []
    for ctrl in ctrls:
        ctrlJnts.append(ctrl.replace('_CTRL', '_JNT'))
    for null in nulls:
        jnt = null.replace('_NULL', '_JNT')
        toJoint = cmds.listRelatives(jnt, p=True)
        if(toJoint[0] not in ctrlJnts):
            toJoint = cmds.listRelatives(toJoint[0], p=True)
        if(toJoint[0] not in ctrlJnts):
            toJoint = cmds.listRelatives(toJoint[0], p=True)
        if(toJoint[0] in ctrlJnts):
            cmds.parentConstraint(toJoint[0], null, mo=True)

def SearchFor(searchTerm):
    objectList = cmds.ls()
    returnList = []
    for object in objectList:
        if( object.endswith(searchTerm)==True ):
            print(object)
            returnList.append(object)
    print(returnList)
    return returnList

# - User Interface -
def CreateHeader():
    headerLayout = cmds.rowLayout( adj=2, nc=3, rat=[(1,'both',0), (2,'both',0), (3,'both',0)] )
#    cmds.text( l=tipsText )
    cmds.separator( style='single', p=headerLayout)
#    middleColumn = cmds.rowLayout(bgc=(0,0,1), rat=[(1,'top',0),(2,'bottom',0)], p=headerLayout)
#    rootLayout = cmds.rowColumnLayout( nc=3, rat=[(1,'both',0), (3,'both',0)], adj=2, bgc=(1,1,1) )
    scrollLayout = cmds.scrollLayout( hst=16, vst=16, cr=True, p=headerLayout )
    contentColumn = cmds.columnLayout( adj=True, p=scrollLayout)
    cmds.separator( style='single', p=headerLayout)

    return contentColumn

def CreateFrame( frameLabel, frameDescription, frameParent ):
    cmds.frameLayout( l=frameLabel, p=frameParent, cl=True, mh=3 )
    frameContainer = cmds.columnLayout( bgc=boxColour, rs=3, co=('both', 10) )
    cmds.text( l=frameDescription )
    return frameContainer

ui()








