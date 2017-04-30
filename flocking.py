import c4d
from c4d import utils
import random
#Welcome to the world of Python


orbs = op[c4d.ID_USERDATA, 1].GetChildren() # Where all the birds are, for now
targetObj = op[c4d.ID_USERDATA, 2] # Target, if object is used
count = op[c4d.ID_USERDATA, 14] # Count


#Functions
#_____________________________________________

def Target(tp, p, target, target_vel):
    ##Particle setup/info_______________________
    mg_vec = c4d.utils.MatrixToHPB(tp.Alignment(p))
    tp.SetPData(p, 1, mg_vec.GetNormalized()) ##Alignment vector for cohesion
    mg_vec.z = 0 ##We want to figure everything out and do the roll separately
    mg = c4d.utils.HPBToMatrix(mg_vec)
    mg.off = tp.Position(p) ##Now we have a global matrix of the particle
    speed = tp.GetPData(p, 2)
    
    ##Target stuff________
    target_ml = ~mg * target ##Target matrix relative to particle
    target_relVel = ~mg * target_vel
    target_Speed = target_vel.GetLength()
    d = target_ml.off.GetLength()
    
    falloff = 300
    accel = op[c4d.ID_USERDATA, 15] ##How is target distance affecting our birds' preferred speed?  Start as preferred acceleration
    
    ##Speed stuff_________
    if d > falloff * 2:
        accel = op[c4d.ID_USERDATA, 3] ##Max Acceleration
        
    if d < falloff:
        d_factor = 1 ##I honestly don't know what to call it xD
        try:
            d_factor = d/falloff 
        except ZeroDivisionError: ##I think, while negligible, this is technically faster than "if falloff != 0"
            pass
        
        accel *= d_factor
        
        ##If the target's behind our bird________
        #if c4d.utils.GetAngle(c4d.Vector(0, 0, -1), target_ml.off) < c4d.utils.Rad(30)
    if p == 0:
        #print target_relVel
        pass
    if d < falloff * 2:
        if abs(target_relVel.z) < op[c4d.ID_USERDATA, 3]:
            if p == 0:
                print target_relVel
            target_ml.off = target_relVel ##If the target's close-ish and not going too fast, pretend like its relative position is its relative velocity so the bird "mimics" it
    
    
        
    
    ##Aiming______
    output = target_ml.off.GetNormalized() ##Direction vector pointing at target relative to particle
    
    return [output, mg] ##Just returning the particle matrix while we're here

def Separation(mg, mg2, d, sep_d): ##Doubles as finding the direction vector
    dirVector = (~mg * mg2).off ##The second particle's position in the coordinate space of the first
    dirVector.Normalize()
    
    output = 0
    
    if d < sep_d:
        output = 1 - (d/sep_d)
    
    return [output, dirVector]

def AngularConstraints(output, ang_maxDelta):
    if abs(output.x) > ang_maxDelta:
        if output.x > 0:
            output.x = ang_maxDelta
        else: output.x = -ang_maxDelta
    if abs(output.y) > ang_maxDelta:
        if output.y > 0:
            output.y = ang_maxDelta
        else: output.y = -ang_maxDelta
    if abs(output.z) > ang_maxDelta:
        if output.z > 0:
            output.z = ang_maxDelta
        else: output.z = -ang_maxDelta
    

def RollWhenTurning(output, targetRoll, p, ang_maxDelta, ang_maxBank):
    roll = tp.GetPData(p, 0)
    deltaRoll = targetRoll - roll
    
    if abs(deltaRoll) > ang_maxDelta:
        if deltaRoll > 0:
            deltaRoll = ang_maxDelta
        else: deltaRoll = -ang_maxDelta
    
    roll += deltaRoll
    if abs(roll) > ang_maxBank:
        if roll < 0:
            roll = -ang_maxBank
        else: roll = ang_maxBank
        
    tp.SetPData(p, 0, roll)
    
    rollMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, 0, roll))
    output = output * rollMatrix
    return output
    
    

def RotationConstraints(output, ang_minPitch, ang_maxPitch, ang_maxDelta):
    output_vec = c4d.utils.MatrixToHPB(output)
    output_vec.z = 0
    if output_vec.y > ang_maxPitch:
        output_vec.y = ang_maxPitch
    if output_vec.y < ang_minPitch:
        output_vec.y = ang_minPitch
        
    off = output.off
    output = c4d.utils.HPBToMatrix(output_vec)
    output.off = off
    
    return output
    
#____________________
#End Functions


def main():
    #Setup
    #__________________________________________________________________________________________
    ####Velocity
    vel_maxDelta = op[c4d.ID_USERDATA, 3] ##Max acceleration
    vel_max = op[c4d.ID_USERDATA, 4] ##Max velocity
    pref_accel = op[c4d.ID_USERDATA, 15] ##Preferred acceleration (sometimes you like to just take it easy)
    ####Group
    sep_d = op[c4d.ID_USERDATA, 12] ##Separation distance
    sep = op[c4d.ID_USERDATA, 12] ##Separation strength
    coh = op[c4d.ID_USERDATA, 13] ##Cohesion strength
    ####Angular constraints/behaviors
    ang_maxDelta = op[c4d.ID_USERDATA, 7]
    ang_minPitch = op[c4d.ID_USERDATA, 8]
    ang_maxPitch = op[c4d.ID_USERDATA, 9]
    ang_maxBank = op[c4d.ID_USERDATA, 16]
    rollStrength = -2
    ####Target (if there is one)
    if "target_prePos" not in globals():
        global target_prePos ##Global so we can keep track of it between frames without putting information on the target itself
        target_prePos = c4d.Vector() ##though we may run into trouble if this gets changed by animation or we need more targets

    target_mg = c4d.Matrix()
    target_vel = c4d.Vector()
    if targetObj != None:
        target_mg = targetObj.GetMg()
        target_vel = target_prePos - target_mg.off
        target_prePos = target_mg.off
    
    tp = doc.GetParticleSystem()
    if doc.GetTime().GetFrame(doc.GetFps()) == 0:
        tp.FreeAllParticles()
        tp.AllocParticles(count)
        for i in range(count):
            spread = 300
            x = random.randrange(-spread, spread)
            y = random.randrange(-spread, spread)
            z = random.randrange(-spread, spread)
            start = c4d.Vector(x, y, z)
            tp.SetPosition(i, start)
            tp.SetLife(i, c4d.BaseTime(500))
            tp.SetPData(i, 0, 0) ##0 is Roll
            tp.SetPData(i, 1, c4d.utils.MatrixToHPB(tp.Alignment(i)).GetNormalized()) ##1 starts complicated, but it's a normalized direction vector (for cohesion)
            tp.SetPData(i, 2, 0) ##2 is Speed (for cohesion), but also used as Preferred Speed and acceleration calculation
    
        
    avePos = c4d.Vector()
    aveVel = c4d.Vector()
    for p in range(count):
    #Pre-Main start, collecting particle average info until octree's implemented
        avePos += tp.Position(p)
        
        
        
        
    for p in range(count):
    #Main start
    #___________________________________________
        output_t = Target(tp, p, target_mg, target_vel) ##______________Target (and more)
        mg = output_t[1] ##Had Target() return the particle's global matrix
        #for efficiency's sake
        pos = mg.off
        output_t = output_t[0] ##Normalized vector pointing to target relative to particle
        
        output_s = c4d.Vector(0)
        output_c = c4d.Vector(1) ##Just because
        k = 0 ##For averaging separation output
        
        #Begin double For loop
        #_______________________________________
        for p2 in range(count):          
            if p == p2: continue ##So we're not checking anything against itself
            
            ##Starting values
            pos2 = tp.Position(p2)
            d = (pos2 - pos).GetLength() ##Distance
            mg2 = c4d.Matrix()
            mg2.off = pos2 ##Just because we need it to be a matrix to do the maths
            ####
            output_s_dirVec = Separation(mg, mg2, d, sep_d)
            dirVector = output_s_dirVec[1] ##Again doubling up on the Functions use
            output_s += -dirVector * output_s_dirVec[0] ##I think that's right...
            #__________________________________
            #End double For loop
            
            
            
            
        vel = c4d.Matrix()
        vel.off = c4d.Vector(0, 0, vel_max) ##Just movin em by vel_Max for now
        
        ####Output
        #_______________________________________
        #output_s /= k ##Average of all Seperation vectors
        output_align = (output_t + output_s * sep).GetNormalized()
        output_align = c4d.utils.VectorToHPB(output_align) ##This is without constraints
        targetRoll = (output_align.x * rollStrength) #+ c4d.utils.Rad(180)??
        
        #Change in align constraints/behaviors
        AngularConstraints(output_align, ang_maxDelta)
        
        #Preparing final output matrix
        output = c4d.utils.HPBToMatrix(output_align)
        output = mg * output
        
        #Final output ("hard") constraints
        output = RotationConstraints(output, ang_minPitch, ang_maxPitch, ang_maxDelta)
        output = RollWhenTurning(output, targetRoll, p, ang_maxDelta, ang_maxBank)
        
        
        tp.SetAlignment(p, output)
        output = output * vel
        tp.SetPosition(p, output.off)
        
        tp.SetPData(p, 2, vel_max)
        
        if p == 7:
            cam = doc.SearchObject("Camera")
            tp.SetScale(p, c4d.Vector(0))            
            cam.SetMg(output)
        if p < 10:
            #print tp.GetPData(p, 2)
            pass
            ##Here for printing values
        
        
        
    ####Notes:
    ####"target" vel or pos refers to instances where the birds are following a target object, 
    ####whereas "pref" (preferred) vel or pos is the bird's *target* vel/pos
    
    ##Fix target_relVel
    return None