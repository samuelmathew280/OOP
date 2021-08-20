#Python Operators Practice
#Arithmetic Operators
a = 12
b = 32
print("a + b = ", a+b)
print("a - b = ", a-b)
print("a * b = ", a*b)
print("b / a = ", b/a)
print("b // a = ", b//a)
print("a ** b = ", a**b, '\n')

#Comparison Operators
a = 10
b = 12
print('a > b is',a>b) # Output: a > b is False
print('a < b is',a<b) # Output: a < b is True
print('a == b is',a==b) # Output: a == b is False
print('a != b is',a!=b) # Output: a != b is True
print('a >= b is',a>=b) # Output: a >= b is False
print('a <= b is',a<=b, '\n') # Output: a <= b is True

#Logical Operators
m = True
n = False
x = False
y = True
print('m and n is',m and n)
print('x or y is',x or y)
print('not x is',not x, '\n')

#Bitwise Operators
x=10
y= 4
print(x & y) # = 0 (0000 0000)      AND
print(x ^ y) # = 14 (0000 1110)     XOR 
print(x << 2) # = 40 (0010 1000)    left shift operator
print(x >> 2, '\n') # = 2 (0000 0010)     right shift operator

#Assignment Operators
a=2
a += 5; print(a)
a %= 5; print(a)
a **= 5; print(a)
a //= 5; print(a, '\n')

#Identity Operators
list1 = [1, 2, 3, 4, 5, 6, 7, 8]
list2 = [1, 2, 3, 4, 5, 6, 7, 8]
print(list2 is list1)
print(list1 is not list2, '\n')

#Membership Operators
list1 = [1, 2, 3, 4, 5, 6, 7, 8]
a= 3
b =32
print(a in list1)
print(b not in list1)