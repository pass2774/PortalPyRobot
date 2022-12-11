# Protocol version
PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel
# Control table address
ADDR_PRO_TORQUE_ENABLE      = 64               # Control table address is different in Dynamixel model
ADDR_PRO_GOAL_POSITION      = 116
ADDR_PRO_GOAL_VELOCITY      = 104
ADDR_PRO_PRESENT_POSITION   = 132
ADDR_PRO_PRESENT_VELOCITY   = 128
ADDR_PRO_PROFILE_ACC        = 108
ADDR_PRO_PROFILE_VEL        = 112
ADDR_PRO_OPERATING_MODE     = 11
# Data Byte Length
LEN_PRO_GOAL_POSITION       = 4
LEN_PRO_GOAL_VELOCITY       = 4
LEN_PRO_PRESENT_POSITION    = 4
LEN_PRO_PRESENT_VELOCITY    = 4
# Data definition
TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold

VELOCITY_MODE               = 1
POSITION_MODE               = 3
EXTENDED_POSITITON_MODE     = 4
PWM_MODE                    = 16