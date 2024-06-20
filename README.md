# EasyFitness is a Web-Application to find the workouts, add them, create your own ,share them keep track on your progress. 


Steps to set up the project on your local machine:  
For zip downloads, unzip the folder and go to step 4.

**1)** Make a new folder.  

**2)** Initialize an empty git repository inside the folder by running the command "git init" in your terminal.  

**3)** Clone the repository using:
   `git clone https://github.com/purgatoriumlautus/easyfitness.git`  

**4)** Move into the folder, set up a new virtual enviroment and activate it.  
   i) For making a new virtual enviroment, paste:
   `python -m venv venv`  
   
   ii) For activating it:
   `.\venv\Scripts\activate`

**5)** Install all the dependencies using:
`pip install -r requirements.txt`

**6)** Set up the database by entering the below command  in the terminal:
`python python .\create_db.py`

**7)** Set up the enviroment variables and run the app.  
   Windows:  
   i) $env:FLASK_APP = "main"  
   ii) flask run  


**To drop tables use :** `python .\drop_tables.py` 

**To apply changes in models use:**
   1) `flask db init`
   2) `flask db migrate `
   3) `flask db upgrade`