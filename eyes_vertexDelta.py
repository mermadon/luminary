import c4d
import cPickle
from c4d import gui


def main():
    
    # The goal
    out_x = {}
    out_y = {}


    # Let's make sure we have both meshes before doing anything
    static_eyes = doc.SearchObject("Eyes_static")
    if not static_eyes:
        print "'Eyes_static' not found." # It's the same in every project this plugin is used, so 'Eyes_static' is plenty clear
        return                           # Note that I did *not* name 'Eyes_static'

    dyn_eyes = static_eyes[c4d.ID_USERDATA, 3]
    if not dyn_eyes:
        print "'Dynamic Eyes' not found on Eyes_static."
        return
    

    # Standard C4D time fare
    time = c4d.BaseTime()
    time.SetDenominator(doc.GetFps())
    
    start = doc.GetMinTime().GetFrame(doc.GetFps())
    end = doc.GetMaxTime().GetFrame(doc.GetFps())
    
    # Start at the beginning of the project
    doc.SetTime(doc.GetMinTime())
    
    pointCount = static_eyes.GetPointCount()
    
    for i in range(start, end + 1):
        
        time.SetNumerator(i)

        doc.SetTime(time)
        doc.ExecutePasses(None, True, True, True, True)
        
        vertexWeight_y = []
        vertexWeight_x = []        

        out_x[i] = []
        out_y[i] = []
    
        for p in range(pointCount):
            
            point_Ay = static_eyes.GetPoint(p).y
            point_Ax = static_eyes.GetPoint(p).x
            
            if dyn_eyes.GetDeformCache == None:
                point_By = dyn_eyes.GetPoint(p).y
                point_Bx = dyn_eyes.GetPoint(p).x
                
            else:
                point_By = dyn_eyes.GetDeformCache().GetPoint(p).y
                point_Bx = dyn_eyes.GetDeformCache().GetPoint(p).x
                

            delta_x = point_Ax - point_Bx
            delta_y = point_Ay - point_By            

            out_x[i].append(delta_x)
            out_y[i].append(delta_y)

        
    f = doc.GetDocumentPath() + "../../rainbow" # 'rainbow' is more than a silly name--in Nuke this data translated into an animated color map

    with open(f, "w") as outFile:
        cPickle.dump([out_x, out_y], outFile)
        
    print "Pickle's done!"

if __name__=='__main__':
    main()