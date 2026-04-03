import numpy as np

#Basic user input from the terminal with no error handling or validation, to be entered in degrees.
print("This script calculates the homogeneous transformation matrix for a 3 link robotic manipulator. (ZYY)")  
q1 = float(input("Enter the value of q1 in degrees: "))
q2 = float(input("Enter the value of q2 in degrees: "))
q3 = float(input("Enter the value of q3 in degrees: "))

# Converts each angle from dgrees to radians
q1 = np.deg2rad(q1)
q2 = np.deg2rad(q2)
q3 = np.deg2rad(q3)

#Hard coded link length and base height as, for this assignment they are unchanged throughout.
b1 = 0.1
l1 = 0.4
l2 = 0.2
l3 = 0.2

#Homogenous Transformation to find end effector position and orintation with respect to the base.
#Each matrix to be multiplied on the RHS of the equation
#B_T_EE = B_T_1 x 1_T_2 x 2_T_3 x 3_T_EE is added as an individual array 

#Base to joint 1 transformation matrix
B_T_1 = np.array([[np.cos(q1), -np.sin(q1), 0, 0],
                     [np.sin(q1), np.cos(q1), 0, 0],
                     [0, 0, 1, b1],
                     [0, 0, 0, 1]])

#Joint 1 to joint 2 transformation matrix
T_2 =   np.array([[np.cos(q2), 0, np.sin(q2), 0],
                     [0, 1, 0, 0],
                     [-np.sin(q2), 0, np.cos(q2), l1],
                     [0, 0, 0, 1]])

#Joint 2 to joint 3 transformation matrix
T_3 =   np.array([[np.cos(q3), 0, np.sin(q3), 0],
                     [0, 1, 0, 0],
                     [-np.sin(q3), 0, np.cos(q3), l2],
                     [0, 0, 0, 1]])

#Joint 3 to end effector transformation matrix
E_3 =   np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, l3],
                    [0, 0, 0, 1]])

#Matrix Multiplication of each matric to find the final transfrom matrix
ans = B_T_1 @ T_2 @ T_3 @ E_3

#Extracting the position from the last column of the transform matrix
x = ans[0, 3]
y = ans[1, 3]
z = ans[2, 3]

#Extracting the orintation from the rotation component of the transfrom matrix.
yaw = np.degrees(np.arctan2(ans[1, 0], ans[0, 0]))
pitch = np.degrees(np.arctan2(-ans[2, 0], np.sqrt(ans[2, 1]**2 + ans[2, 2]**2)))
roll = np.degrees(np.arctan2(ans[2, 1], ans[2, 2]))

#Print the position and orinetation to the terminal, rounded to 4 decimal places. 
print("The homogeneous transformation matrix is: ")
print("X ", round(x, 4))
print("Y ", round(y, 4))
print("Z ", round(z, 4))
print("Pitch (Y) ", round(pitch, 4), "degrees")
print("Yaw (Z) ", round(yaw, 4), "degrees")
print("Roll (X) ", round(roll, 4), "degrees")
