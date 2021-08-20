#Python Data Types
a = 20
b ="Hello World"  
c = 14.5  
print(type(a))  
print(type(b))  
print(type(c))

#Numbers
a = 10  
print("The type of a", type(a))  
  
b = 23.5  
print("The type of b", type(b))  
  
c = -5+2j  
print("The type of c", type(c))  
print(" c is a complex number", isinstance(1+3j,complex))

#Sequence
str1 = 'Hello World'
str2 = 'Merry Christmas'
print (str1[0:2])            #printing first two character using slice operator    
print (str1[4])             #printing 4th character of the string    
print (str1*2)               #printing the string twice    
print (str1 + str2, '\n')          #printing the concatenation of str1 and str2

#List
list1 = ['apples', 'bananas', 'cherries']
print(type(list1))
print(list1[:2])        #print first 2 elements in list
print(list1 + list1, '\n')    #list concatenation

#Tuple - Different from list because it is immutable
tup  = ('apples', 'bananas', 'cherries')
print (type(tup))
print (tup)  
print (tup[1:])  #Tuple slicing  
print (tup[0:1])    
print (tup + tup) #Tuple concatenation using + operator
print(tup*4, '\n') #Tuple repition

#Dictionary
dictionary = {'cars' : ['Honda', 'Hyundai', 'Ford'],
              'color' : ['Red', 'Blue', 'Green']}
print (dict)  
print("Available cars are: {0}\nAvailable in these colors: {1}\n".format(dictionary['cars'], dictionary['color']))

#Boolean
a = 1>2 #False
print(a)
print(type(a), '\n')

#Set
set1 = set()  #Empty set
set2 = {'India', 20.4, 100,'OOP'}   
print(set2)
set2.add(5)  
print(set2)
set2.remove(100)  
print(set2, '\n')

#Strings
str1 = 'Hello world!'
print("str1[4] = ", str1[4]) #str1[4] = 'o'
print("str1[6:11] = ", str1[6:11])  #str1[6:11] = 'world'
print(str1, '\n')

#Implicit Type Conversion
var_int = 123
var_float = 1.23
var_new = var_int + var_float
print("Datatype of var_int:",type(var_int))
print("Datatype of var_float:",type(var_float))
#Implicit type conversion of var_int into float
print("Value of var_new:",var_new)
print("Datatype of var_new:",type(var_new), '\n')

#Explicit Type Conversion
num_int = 500
num_str = "390"

print("Data type of num_int:",type(num_int))    #int
print("Data type of num_str before Type Casting:",type(num_str))    #string

num_str = int(num_str)
print("Data type of num_str after Type Casting:",type(num_str)) #sting forcibly converted to int

num_sum = num_int + num_str

print("Sum of num_int and num_str:",num_sum)
print("Data type of the sum:",type(num_sum))