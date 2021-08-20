#Python Variable Practice
a = 3
b = 12
c = a+b

#Object Reference/Identity
a = "Hello"
print(type(a))
a = b = 5
print(id(a))
print(id(b))
c = 5
d = c
print(id(a))
print(id(b))

#Multi-assign
a,b,c = 5, 10, 15
print(a,b,c)
name1, name2, name3 = "Samuel", "Sam", "Samantha"
print(name1, name2, name3)

#Python Variable Types
def MUL():
    #Defining local variables
    m = 23
    n = 3
    return m*n
MUL()   #Calling function
z = 200 #Global variable

#Python String Practice
s = 'Beautiful palace'
print(s[:])
print(s[::])
print(s[:4]) #Printing only first 4 characters
print(s[2:5]) #Printing characters at indices 2-4
a = "Hello world"
slice_object1 = slice(-1, -6, -1)   #Slicing strings. (start, stop, step)
slice_object2 = slice(1, 6, -1)
slice_object3 = slice(1, 6, 1)
print(a[slice_object1], a[slice_object2], a[slice_object3])
rev_a = a[::-1]
print(rev_a)
s1 = s[2:8:2]
print(s1)

py_list = ['P', 'y', 't', 'h', 'o', 'n']    #List, mutable
py_tuple = ('P', 'y', 't', 'h', 'o', 'n')   #Tuple, immutable
slice_object = slice(3) #Indices 0, 1, 2
print(py_list[slice_object])
slice_object = slice(1, 5, 2)
print(py_tuple[slice_object]) #indices 1 and 3
slice_object = slice(-1, -4, -1)
print(py_list[slice_object]) # ['n', 'o', 'h']
slice_object = slice(-1, -5, -2)
print(py_tuple[slice_object]) # ('n', 'h')