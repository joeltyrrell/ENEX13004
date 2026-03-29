import numpy

print("This script calculates the homogeneous transformation matrix for a 3 link robotic manipulator. (ZYY)")  
q1 = float(input("Enter the value of q1 in degrees: "))
q2 = float(input("Enter the value of q2 in degrees: "))
q3 = float(input("Enter the value of q3 in degrees: "))

q1 = numpy.deg2rad(q1)
q2 = numpy.deg2rad(q2)
q3 = numpy.deg2rad(q3)

b1 = 0.1
l1 = 0.4
l2 = 0.2
l3 = 0.2

B_T_1 = numpy.array([[numpy.cos(q1), -numpy.sin(q1), 0, 0],
                     [numpy.sin(q1), numpy.cos(q1), 0, 0],
                     [0, 0, 1, b1],
                     [0, 0, 0, 1]])


T_2 =   numpy.array([[numpy.cos(q2), 0, numpy.sin(q2), 0],
                     [0, 1, 0, 0],
                     [-numpy.sin(q2), 0, numpy.cos(q2), l1],
                     [0, 0, 0, 1]])

T_3 =   numpy.array([[numpy.cos(q3), 0, numpy.sin(q3), 0],
                     [0, 1, 0, 0],
                     [-numpy.sin(q3), 0, numpy.cos(q3), l2],
                     [0, 0, 0, 1]])

E_3 =   numpy.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, l3],
                    [0, 0, 0, 1]])


ans = B_T_1 @ T_2 @ T_3 @ E_3
x = ans[0, 3]
y = ans[1, 3]
z = ans[2, 3]
yaw = numpy.degrees(numpy.arctan2(ans[1, 0], ans[0, 0]))
pitch = numpy.degrees(numpy.arctan2(-ans[2, 0], numpy.sqrt(ans[2, 1]**2 + ans[2, 2]**2)))
roll = numpy.degrees(numpy.arctan2(ans[2, 1], ans[2, 2]))



print("The homogeneous transformation matrix is: ")
print("X ", round(x, 4))
print("Y ", round(y, 4))
print("Z ", round(z, 4))
print("Pitch (Y) ", round(pitch, 4), "degrees")
print("Yaw (Z) ", round(yaw, 4), "degrees")
print("Roll (X) ", round(roll, 4), "degrees")