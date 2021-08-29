from datetime import datetime
from datetime import date
from dateutil import relativedelta as rdelta
#INITIALIZING DATABASE VARIABLES
admins = []
registered_users = []
registered_donors = []
blood_banks = []
pending_requests = []
#PRE-DEFINED GLOBAL VARIABLES
rare_groups = ['O-', 'A-', 'B-', 'AB+', 'AB-']
start_time = datetime.utcnow()

#####################################################
##                    MODULES                      ##
#####################################################
#______________________ADMIN________________________#
class Admin:
    def __init__(self, name, ID):
        self.name = name
        self.ID = ID

    def AddBloodBank(self):
        name = input("Provide the blood bank's name: ")
        type = int(input("Is it a\n1. Hospital\n2. Blood donation camp\nEnter the appropriate choice number: "))
        blood_types = []
        j = 0
        while(j==0):
            k = input('Input available blood types, one at a time. (eg. O+ or AB-). Press 1 to escape if finished or not applicable. ')
            if k == '1':
                if len(blood_types) == 0 and type == 1:
                    print("At least enter one available blood type.")
                    continue
                break
            else:
                blood_types.append(k)
        address = input("Provide the blood bank's full address, including area and town: ")
        city = input("Provide the blood bank's city name: ")
        blood_bank = {'name' : name,
                        'type' : type,
                        'av_types' : blood_types,                 #Available blood types
                        'address' : address,
                        'city' : city,
                        'current_requests' : []
                    }
        blood_banks.append(blood_bank)
        print("Blood bank registered!\n")

    def searchByBranch(self):
        city = input("Provide the city's name to search blood donors in: ")
        area = input("Provide an area/town to look for blood donors in: ")
        eligibleDonors = []
        for i in registered_donors:
            if i.city.lower().strip() == city.lower().strip():
                if i.address.lower().count(area.lower().strip()) > 0:
                    eligibleDonors.append(i)
        j = 1
        if len(eligibleDonors) > 0:
            for i in eligibleDonors:
                print("{0}. Name = '{1.name}', Age = '{1.age}', Sex = '{1.sex}', Blood Group = '{1.blood_group}', Address = '{1.address}', City = '{1.city}'".format(j, i))
                j+=1
        else:
            print("No matching donors.")
        print('\n')

    def assignPendingRequest(self):
        if len(pending_requests) == 0:
            print('No pending requests!\n')
        else:
            j = 1
            for i in pending_requests:
                print("{0}. Name = '{1.name}', Age = '{1.age}', Sex = '{1.sex}', City = '{1.city}', Requested blood type = '{2}', Date = {3}".format(j, i['User'], i['Bg_req'], i['Date']))
                j+=1
            n = int(input('Enter the number to deal with a particular request. Enter 0 to return to previous menu.\n'))
            if n != 0:
                request = pending_requests[n-1]
                if request['Urgent'] != True and len(blood_banks) != 0:       #SEND REQUEST TO BLOOD BANK IF NOT URGENT
                    print("Assign request to which of the following blood banks:\n")
                    j=1
                    for i in blood_banks:
                        print("{0}. Name = '{1}', Address = '{2}', Available blood types = '{3}'".format(j, i['name'], i['address'], ", ".join(i['av_types'])))
                        j+=1
                    n = int(input("Pick the blood bank to assign the request to: "))
                    blood_banks[n-1]['current_requests'].append(request)
                    print("Request successfully sent to the blood bank!\n")
                    pending_requests.remove(request)
                else:                                                           #SEND DIRECTLY TO A DONOR IF REQUEST IS URGENT
                    j=1
                    if len(registered_donors) == 0:
                        print("There are no registered donors in the database. Wait for a donor to register to send the request to.\n")
                        return
                    elif len(registered_donors) == 1 and request['User'].donor == True:
                        print("There are no registered donors in the database. Wait for a donor to register to send the request to.\n")
                        return
                    for i in registered_donors:
                        if request['User'] != i:
                            print("{0}. Name = '{1.name}', Age = '{1.age}', Sex = '{1.sex}', Blood Group = '{1.blood_group}', Address = '{1.address}', City = '{1.city}'".format(j, i))
                        j+=1
                    n = int(input("Pick the donor to assign the request to (BE CAREFUL TO SEND THE REQUEST TO SOMEONE WITH COMPATIBLE BLOOD TYPE ELSE IT WILL BE REJECTED): "))
                    registered_donors[n-1].urgent_request.append(request)
                    print("Request successfully sent to the donor!\n")
                    pending_requests.remove(request)

    def CollectBloodSample(self):
        time_now = datetime.utcnow()
        global start_time
        time_passed = rdelta.relativedelta(time_now, start_time)
        if time_passed.minutes >= 1:                #1 Day in app = 1 minute in real life
            if len(blood_banks) > 0:
                for i in blood_banks:
                    if i['type'] == 2:
                        continue
                    print("Update available blood samples for '{0}'".format(i['name']))
                    blood_types = []
                    while(1):
                        k = input('Input available blood types, one at a time. (eg. O+ or AB-). Press 1 to escape if finished or not applicable. ')
                        if k == '1':
                            if len(blood_types) == 0:
                                print("At least enter one available blood type.")
                                continue
                            break
                        else:
                            blood_types.append(k)
                    i['av_types'] = blood_types
                    print("\nAvailable blood types for the hospital has been successfully updated!\n")
            else:
                print("Currently there are no blood banks in the database.\n")
            start_time = time_now
        else:
            print("A day has not passed yet. Come back tomorrow to input the blood samples for the different blood banks.\n")

#______________________USER________________________#
class User:
    def __init__(self, name, age, sex, address, city, blood_group, donor, Aadhaar_num, contact_number):
        self.name = name
        self.age = age 
        self.sex = sex
        self.address = address
        self.city = city
        self.blood_group = blood_group
        self.donor = donor
        self.Aadhaar_num = Aadhaar_num
        self.contact_number = contact_number
        self.received_blood_by = []
        if self.donor == True:
            self.urgent_request = []
            self.blood_donated_to = []

    def placeRequest(self):
        blood_type = input("What blood type are you in need of? (Eg. O- or AB+)\n")
        blood_type = blood_type.strip()
        if blood_type.upper() in rare_groups:                   #If blood type is rare, request is made an emergency or urgent. In such cases, it will be sent directly to a donor, and not a blood bank
            urgent = True
        else:
            urgent = False
        date = input("What is the date as of placing this request? (DD-MM-YYYY)\n")
        request = {'User': self,
                   'Urgent' : urgent,
                   'Bg_req' : blood_type,
                   'Date' : date}
        global pending_requests
        pending_requests.append(request)
        print("The request has been recorded. You will be contacted soon.\n")

    def viewRequests(self):
        if len(self.urgent_request) > 0:
            j = 1
            for request in self.urgent_request:
                print("{0}. Name = '{1.name}', Age = '{1.age}', Sex = '{1.sex}', Blood group required = '{2}', Address = '{1.address}', Date = {3}".format(j, request['User'], request['Bg_req'], request['Date']))
                j+=1
            k = int(input("\nWhat action do you want to take?\n1. Accept request\n2. Reject request\n3. Go back to menu (enter any number)\n"))
            if k == 1:
                j = int(input("Which of the listed requests do you want to accept? Enter the corresponding number: "))
                request = self.urgent_request[j-1]
                request['User'].received_blood_by.append(self)
                self.blood_donated_to.append(request['User'])
                print("Thanks for accepting the request and donating!\n")
            elif k == 2:
                j = int(input("Which of the listed requests do you want to reject? Enter the corresponding number: "))
                request = self.urgent_request[j-1]
                self.urgent_request.remove(request)
                pending_requests.append(request)
                print("Request removed!\n")
        else:
            print("You have no requests for blood donation.\n")

    def donationHistory(self):
        k = 1
        if self.donor == True:
            if len(self.blood_donated_to)> 0:
                print("Donated blood to: ")
                for i in self.blood_donated_to:
                    print("{0}. Name = '{1.name}', Age = '{1.age}', Sex = '{1.sex}', Blood group = '{1.blood_group}', Address = '{1.address}', City = '{1.city}'".format(k, i))
                    k+=1
            else:
                print("Didn't donate blood yet.")
        print('\n')
        k = 1
        if len(self.received_blood_by)> 0:
            print("Received blood from: ")
            for i in self.received_blood_by:
                print("{0}. Name = '{1.name}', Age = '{1.age}', Sex = '{1.sex}', Blood group = '{1.blood_group}', Address = '{1.address}', City = '{1.city}'".format(k, i))
                k+=1
        else:
            print("Haven't received blood from anyone.")
        print('\n')

#####################################################
##                    FUNCTIONS                    ##
#####################################################
def compareLists(list1, list2):             #Compare to see if two lists have a single common element
    for i in list1:
        for j in list2:
            if i == j:
                return True
    return False

def listRareBloodGroupsByBranch():
    if len(blood_banks) == 0:
        print("No blood banks in the data yet. An admin needs to add them.\n")
        return
    j = 0
    cities_covered = []
    for i in blood_banks:
        temp = i['city']
        if temp in cities_covered or i['type'] == 2:
            j+=1
            continue
        else:
            cities_covered.append(temp)
        print("Blood banks with rare blood types in {0}:".format(temp))
        flag = 0
        for k in blood_banks[j:]:
            if k['type'] == 2:
                continue
            if k['city'] == temp:
                if compareLists(k['av_types'], rare_groups) == True:            #Check if any available blood type is rare
                    print("Name = '{0}', Available blood types = '{1}', Address = '{2}'".format(k['name'], k['av_types'], k['address']))
                    flag = 1
            if flag == 0:
                print("None in database.")
        print('\n')
        j+=1

def searchBloodBank():
    if len(blood_banks) == 0:
        print("No blood banks in the data yet. An admin needs to add them.\n")
        return
    blood_type = input("Enter the blood type to be searched: ")
    flag = 0
    for i in blood_banks:
        if blood_type in i['av_types']:
            print("Name = '{0}', Available blood types = {1}, Address = '{2}', City = '{3}'".format(i['name'], i['av_types'], i['address'], i['city']))
            flag = 1
    if flag == 0:
        print("None in database.")
    print('\n')

def searchDonorsByCity():
    if len(registered_donors) == 0:
        print("No registered donors in the data yet. Users need to register as one.\n")
        return
    city = input("Enter the city you want donors to be searched in: ")
    flag = 0
    for i in registered_donors:
        if i.city == city:
            print("Name = '{0.name}', Age = '{0.age}', Sex = '{0.sex}', Blood group = '{0.blood_group}'".format(i))
            flag = 1
    if flag == 0:
        print("None in database.")
    print('\n')

def searchDonorsByBloodType():
    if len(registered_donors) == 0:
        print("No registered donors in the data yet. Users need to register as one.\n")
        return
    blood_type = input("Enter the blood type of donors you want to be searched: ")
    flag = 0
    for i in registered_donors:
        if i.blood_group == blood_type:
            print("Name = '{0.name}', Age = '{0.age}', Sex = '{0.sex}', Blood group = '{0.blood_group}'".format(i))
            flag = 1
    if flag == 0:
        print("None in database.")
    print('\n')

def listRareBloodGroupsByDonors():
    flag = 0
    for i in registered_donors:
        if i.blood_group in rare_groups:
            print("Name = '{0.name}', Age = '{0.age}', Sex = '{0.sex}', Blood group = '{0.blood_group}'".format(i))
            flag = 1
    if flag == 0:
        print("None in database.")
    print('\n')

#####################################################
##                EXISTING DATABASE                ##
#####################################################
# Admin(name, ID)
admin1 = Admin('Samuel', 1)
admin2 = Admin('Shaunak', 2)
admins.append(admin1)
admins.append(admin2)

# User(name, age, sex, address, city, blood_group, donor, Aadhaar_num, contact_number)
user1 = User('Rakesh', 19, 'M', 'C-21, Cloud 9, Sector 11, Vashi', 'Navi Mumbai', 'O-', True, 5134234511991456, 9322382911)
user2 = User('Samir', 27, 'M', '1, Swaraj Towers, Sector 2, Nerul', 'Navi Mumbai', 'O+', True, 1734324501851456, 9706382943)
user3 = User('Abby', 23, 'F', 'B-102, Atlantis, Sector 14, Powai', 'Mumbai', 'A-', True, 6514324585351456, 9294852943)
user4 = User('Kavya', 21, 'F', "J-42, Queen's Crown, Sector 1, Nanded", 'Pune', 'AB+', False, 3859424585301856, 9213892943)     #Not a donor
user5 = User('Alex', 35, 'M', "Flat 2, Priyadarshani, Sector 4, Aundh", 'Pune', 'B+', False, 1038524585351456, 9810395943)      #Not a donor
registered_donors.append(user1)
registered_donors.append(user2)
registered_donors.append(user3)
registered_users.append(user1)
registered_users.append(user2)
registered_users.append(user3)
registered_users.append(user4)
registered_users.append(user5)

#####################################################
##                  MAIN PROGRAM                   ##
#####################################################
while(1):
    n = int(input("Welcome to the Blood donation app\n1. Admin log-in\n2. Register admin\n3. User log-in\n4. Register user\n5. Other available data\n6. Exit\n"))
    if n == 1:
        name = input('Kindly enter your name: ')
        id = int(input('Kindly enter your ID as well: '))
        print('\n')
        verification = False
        for i in admins:
            if i.name == name and i.ID == id:
                verification = True
                break
        if verification == True:
            admin = i
            while(1):
                n = int(input("Welcome! If this is your first time logging-in, kindly input all the hospitals into the database and then proceed with the other options.\nWhat do you want to do now?\n1. Add a new hospital/blood donation camp.\n2. View list of donors of a particular area (branch).\n3. Check blood requests. ({0})\n4. Update blood banks' available samples (to be done daily)\n5. Exit to main screen\n".format(len(pending_requests))))
                if n == 1:
                    admin.AddBloodBank()
                elif n == 2:
                    admin.searchByBranch()
                elif n == 3:
                    admin.assignPendingRequest()
                elif n == 4:
                    admin.CollectBloodSample()
                elif n == 5:
                    break
                else:
                    print("Invalid entry\n")
        else:
            print("You are not a registered admin.\nKindly register yourself first.\n")
    elif n == 2:
        name = input("Enter your name: ")
        id = int(input("Enter your employee ID: "))
        admin = Admin(name, id)
        admins.append(admin)
        print("You have been registerd as an admin. Use these credentials to log-in.\n")

    elif n == 3:
        name = input('Kindly enter your name: ')
        print('\n')
        verification = False
        for i in registered_users:
            if i.name == name:
                verification = True
                break
        if verification == True:
            user = i
            while(1):
                if user.donor == True:
                    n = int(input("Welcome! What do you want to do now?\n1. Place a blood group request\n2. View requests to donate blood ({0})\n3. View donation history\n4. Exit to main screen\n".format(len(user.urgent_request))))
                else:
                    n = int(input("Welcome! What do you want to do now?\n1. Place a blood group request\n2. View requests to donate blood (for donors)\n3. View donation history\n4. Exit to main screen\n"))
                if n == 1:
                    user.placeRequest()
                elif n == 2:
                    user.viewRequests()
                elif n == 3:
                    user.donationHistory()
                elif n == 4:
                    break
                else:
                    print("Invalid entry.\n")
        else:
            print("You are not a registered user. Kindly register yourself first.\n")
    elif n == 4:
        name = input("Enter your name: ")
        age = int(input("Enter your age: "))
        sex = input("Enter your sex (M/F): ")
        address = input("Enter your full address: ")
        city = input("Enter your city: ")
        blood_group = input("Enter your blood group: ")
        donor = input("Will you be willing to donate blood if needed? Enter Yes or No: ")
        if donor.lower().startswith('y'):
            donorBool = True
        else:
            donorBool = False
        aadhaar_num = int(input("Enter your Aadhaar number: "))
        contact_num = int(input("Enter your contact number: "))
        user = User(name, age, sex, address, city, blood_group, donorBool, aadhaar_num, contact_num)
        registered_users.append(user)
        if donorBool == True:
            registered_donors.append(user)
        print("You have been registerd as a user. Use your name to log-in.\n")

    elif n == 5:
        while 1:
            n = int(input("1. Get blood banks with rare blood groups (city-wise)\n2. Search blood banks by blood group\n3. Search donors in your city\n4. Search donors by blood type\n5. List donors with rare blood types\n6. Go back to main menu\n"))       
            if n == 1:                          #Differentiated by cities, hence branches are classified
                listRareBloodGroupsByBranch()
            elif n == 2:
                searchBloodBank()
            elif n == 3:
                searchDonorsByCity()
            elif n == 4:
                searchDonorsByBloodType()
            elif n == 5:
                listRareBloodGroupsByDonors()
            elif n == 6:
                break
            else:
                print("Invalid entry. Try again.\n")

    elif n == 6:
        exit(1)

    else:
        print("Invalid entry.\n")