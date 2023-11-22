import scara
import logging 
from xbox360controller import Xbox360Controller
import scara.can_pizza as pizza
import time

increasing = False
decreasing = False

init_point = [0.,500.,170.]
current_x = init_point[0]
current_y = init_point[1]
current_z = init_point[2]

current_orientation = 'right'
x_lims = [-200.0,200.0]
y_lims = [400.0,600.0]
z_lims = [30.0,170.0]

axis_speed = 60.0 #mm/s
refresh_rate = 100.0
period = 1.0/refresh_rate

gain = axis_speed/refresh_rate
steps_per_iter = int(50.0/refresh_rate)
if steps_per_iter == 0:
    steps_per_iter = 1

def axis_callback(x,y,z):
    global current_x
    global current_y
    global current_z
    global gain
    global nelen
    global current_orientation
    new_x = current_x + gain*x
    new_y = current_y + gain*y
    new_z = current_z + gain*z
    if x_lims[0] <= new_x <= x_lims[1]:
        current_x = new_x
    else:
        if abs(x_lims[0]-new_x) < abs(x_lims[1]-new_x):
            current_x = x_lims[0]
        else:
            current_x = x_lims[1]
    if y_lims[0] <= new_y <=y_lims[1]:
        current_y = new_y
    else:
        if abs(y_lims[0]-new_y) < abs(y_lims[1]-new_y):
            current_y = y_lims[0]
        else:
            current_y = y_lims[1]
    if z_lims[0] <= new_z <=z_lims[1]:
        current_z = new_z
    else:
        if abs(z_lims[0]-new_z) < abs(z_lims[1]-new_z):
            current_z = z_lims[0]
        else:
            current_z = z_lims[1]
    nelen.move(current_x,current_y,current_z,current_orientation)

def vueltita(arg):
    global t
    global current_x
    global current_y
    global gain
    global nelen
    global current_orientation
    global wait_for_vueltita
    if current_orientation == "right":
        current_orientation = "left"
    else:
        current_orientation = "right"
    config_trap_traj()
    wait_for_vueltita = True
    nelen.move(current_x,current_y,current_z,current_orientation)
    t = t+3

def a_increase():
    global nelen
    nelen.a_move(steps_per_iter)

def a_decrease():
    global nelen
    nelen.a_move(-1*steps_per_iter)

def on_increase_pressed(arg):
    global increasing
    global decreasing
    increasing = True
    decreasing = False

def on_increase_released(arg):
    global increasing
    increasing = False

def on_decrease_pressed(arg):
    global decreasing
    global increasing
    increasing = False
    decreasing = True

def on_decrease_released(arg):
    global decreasing
    decreasing = False

def a_init(arg):
    pizza.motor_enable(1)

def clamp(value,limit=0.33):
    if -1*limit <= value <= limit:
        return 0
    elif value> limit:
        return 1
    else:
        return -1

INPUT_MODE_POS_FILTER = 3
INPUT_MODE_TRAP_TRAJ = 5

wait_for_vueltita = False

def config_trap_traj():
    nelen.hombro.axis.controller.config.input_mode  = INPUT_MODE_TRAP_TRAJ
    nelen.codo.axis.controller.config.input_mode  = INPUT_MODE_TRAP_TRAJ


def config_filter():
    nelen.hombro.axis.controller.config.input_mode  = INPUT_MODE_POS_FILTER
    nelen.codo.axis.controller.config.input_mode  = INPUT_MODE_POS_FILTER
    nelen.hombro.axis.controller.config.input_filter_bandwidth  = refresh_rate/2
    nelen.codo.axis.controller.config.input_filter_bandwidth  = refresh_rate/2


def main():
        
     # Start an IPython terminal
    banner = "Welcome to the scara IPython terminal"

if __name__ == "__main__":
    # scara.logger.setLevel(logging.INFO)  # set info level for logger
    nelen = scara.Robot()  # creates an instance of the scara robot
    config_trap_traj()
    nelen.move(init_point[0],init_point[1],init_point[2])
    wait_for_vueltita = True
    try:
        with Xbox360Controller(0, axis_threshold=0.2) as controller:
            controller.button_start.when_pressed = vueltita
            controller.button_select.when_pressed = a_init
            controller.button_x.when_pressed = on_increase_pressed
            controller.button_x.when_released = on_increase_released
            controller.button_y.when_pressed = on_decrease_pressed
            controller.button_y.when_released = on_decrease_released
            t = time.clock_gettime(0)
            while True:
                if time.clock_gettime(0)-t >= period:
                    t = time.clock_gettime(0)
                    if wait_for_vueltita:
                        if nelen.hombro.axis.controller.trajectory_done \
                        and nelen.codo.axis.controller.trajectory_done:
                            wait_for_vueltita = False
                            config_filter()
                    else:
                        x = clamp(controller.axis_l.x)
                        y = clamp(-1*controller.axis_l.y)
                        z = controller.button_a.is_pressed-controller.button_b.is_pressed
                        axis_callback(x,y,z)
                        try:
                            if increasing:
                                a_increase()
                            elif decreasing:
                                a_decrease()
                        except:
                            pass
    except KeyboardInterrupt:
        config_trap_traj()
        pass
