
import cmd_manager

arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,-63,120,0,0,0)
# arm = '{0:%d,1:%d,2:%d,3:%d,4:%d,5:%d}' % (0,20,0,0,0,0)
gimbal = '{0:%d,1:%d,2:%d}' % (30,0,0)

input_data_dict ={
"arm":arm, 
"gimbal":gimbal,
}

cmd_manager.update_commandFile(str(input_data_dict))
# cmd_manager.toHome()