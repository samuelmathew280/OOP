#Python Control Practice
#If statements
a = 2
b = 3
if a<b:
    print("a is less than b", '\n')

#Multi-conditions
a, b = 2, 3
if a<b:
    print("a is less than b")
elif b<a:
    print("b is less than a")
else:
    print("a is equal to b")

#Nested If
if a<=b:
    if a<b:
        print("a is less than b")
    else:
        print("a is equal to b")

#For loop
numbers = [60, 25, 33, 85, 40, 22, 55, 43, 51]
sum = 0
for val in numbers:
    sum = sum+val
print("The sum is ", sum)

#For with range
for i in range(1,11):
    print(i+21)
print(' ')

#For with else
student_name = 'Soyuj'
marks = {'James': 90, 'Jules': 55, 'Arthur': 77}
for student in marks:
    if student == student_name:
        print(marks[student])
        break
else:
    print('No entry with that name found.')
print(' ')

#While loop
numbers = [60, 25, 33, 85, 40, 22, 55, 43, 51]
sum = i = 0
while i<9:
    sum+=numbers[i]
    i=i+1
print("The sum is ", sum)