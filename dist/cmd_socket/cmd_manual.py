
import cmd_manager

# arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d,6:%d}' % (20,-60,110,0,0,0,0)
# # arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,20,0,0,0,0)
# gimbal = '{0:%d,1:%d,2:%d}' % (30,0,0)
# # gv = '{21:%d,22:%d,23:%d,24:%d}' % (10,10,10,-10)
# gv = '{21:%d,22:%d,23:%d,24:%d}' % (0,0,0,0)

# input_data_dict ={
# "arm":arm, 
# "gimbal":gimbal,
# "gv":gv
# }

arm = {
    0:20,
    1:-60,
    2:110,
    3:0,
    4:0,
    5:0,
    6:0
}
gimbal = {
    0:30,
    1:0,
    2:0
}
gv = {
    21:0,
    22:0,
    23:0,
    24:0
}

input_data_dict ={
"arm":arm, 
"gimbal":gimbal,
"gv":gv
}


cmd_manager.update_commandFile(input_data_dict)
# cmd_manager.update_commandFile(str(input_data_dict))
# cmd_manager.toHome()