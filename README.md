# EasyFitness

EasyFitness is a user-friendly web application built using Flask to help you manage your workout routines effectively. With EasyFitness, you can:  
- Browse and find workouts that suit your needs.  
- Add new workouts to your list.  
- Create and customize your own workout routines.  
- Share workouts with others.  
- Keep track of your progress and stay motivated.  

---

## Steps to Set Up the Project on Your Local Machine:

### Prerequisite:  
Ensure that you have Python installed on your system. You can check this by running `python --version` in your terminal.

### For Zip Downloads:  
If you downloaded the project as a zip file, unzip it and proceed directly to **Step 4**.

---

### 1. Create a New Folder:
Choose a directory on your computer and create a new folder to store the project files.

---

### 2. Initialize a Git Repository:
Open a terminal or command prompt, navigate to the folder you just created, and initialize an empty Git repository by running:  


**3)** Clone the repository using:
```
   git clone https://github.com/purgatoriumlautus/easyfitness.git  
```
**4)** Move into the folder, set up a new virtual enviroment and activate it.  
   i) For making a new virtual enviroment, paste:
   ```
   python -m venv venv  
   ```
   ii) For activating it:
   ```
   .\venv\Scripts\activate
   ```
**5)** Install all the dependencies using:
```
pip install -r requirements.txt
```
**6)** Set up the database by entering the below command  in the terminal:
```
python python .\create_db.py
```
**7)** Set up the enviroment variables and run the app.  
   Windows:  
   
   i)``` $env:FLASK_APP = "main"```  
   ii)``` flask run  ```


**To drop tables use :**
```python .\drop_tables.py``` 

**To apply changes in models use:**
```
flask db init
flask db migrate
flask db upgrade
```
