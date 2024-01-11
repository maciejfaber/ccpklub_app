# ccpklub_app
 New web app for CCPKLUB

Required python packages are in 'ccpklub_app/CPP_app/requirements.txt'
First, activate venv and then run the application via manage.py

Some screens from main functions in app

Registration
![alt text](https://raw.githubusercontent.com/maciejfaber/ccpklub_app/main/Screens/registration.png)

![alt text](https://raw.githubusercontent.com/maciejfaber/ccpklub_app/main/Screens/registration_message.png)

![alt text](https://raw.githubusercontent.com/maciejfaber/ccpklub_app/main/Screens/inactive_users.png)

The User can register as an Exhibitor or Breeder. These roles determine what functionalities will be available to him. After confirming the registration, a confirmation e-mail is sent to the user.

Add pigs
![alt text](https://raw.githubusercontent.com/maciejfaber/ccpklub_app/main/Screens/add_pig.png)

Users can add guinea pigs via a form with multiple validations. After sending, the registration is saved in a JSON file for later approval by an authorized person.

![alt text](https://raw.githubusercontent.com/maciejfaber/ccpklub_app/main/Screens/waiting_pig_list.png)

![alt text](https://raw.githubusercontent.com/maciejfaber/ccpklub_app/main/Screens/waiting_pig_list_details.png)

An authorized user can view the user form and perform the appropriate action. The adding function is implemented in such a way as not to create duplicate pigs and not to edit pigs that are not owned by the adding user.
