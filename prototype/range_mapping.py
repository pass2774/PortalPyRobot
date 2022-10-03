import numpy as np

angle_range_param={
    0:{'zero':  0,'mag':  90},
    1:{'zero':  0,'mag':  90},
    2:{'zero':  0,'mag':  90},
    3:{'zero':  0,'mag':  90},
    4:{'zero':  0,'mag':  90},
    5:{'zero': 45,'mag':  45},
}

dxl_range_param={
    0:{'zero': 2700,'mag':2000},
    1:{'zero': 2500,'mag':1800},
    2:{'zero': 2900,'mag':2700},
    3:{'zero': 2750,'mag':2000},
    4:{'zero':    0,'mag':1000},
    5:{'zero': 2600,'mag': 600},
}

def setRangeMap(range_param):
  range_map={}
  for idx,param in range_param.items():
      range_map[idx]=[param['zero']-param['mag'],param['zero']+param['mag']]
  return range_map

def interp_maps(x,map_x,map_y,dtype):
  y={}
  for idx, value in x.items():
    y[idx]=np.interp(value,map_x[idx],map_y[idx]).astype(dtype)
  return y

angle_range_map = setRangeMap(angle_range_param)
dxl_range_map   = setRangeMap(dxl_range_param)
x={0:0,1:0,2:0,3:0,4:0,5:90}
y=interp_maps(x,angle_range_map,dxl_range_map,np.int32)
  
print(dxl_range_map)
  
# y2=np.array(y,dtype=np.int32)
print("y")
print(y)