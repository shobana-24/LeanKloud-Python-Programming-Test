# LeanKloud Python Programming Test

## Part 1: REST API for Todo app using Flask-RESTPlus
  An REST API app to maintain a list of todos in a database with read access authorization for GET methods and write access authorization for PUT and POST methods.
  
### Tools Used:
1. Python 3.8.6
2. Flask 1.1.2
3. Flask-RESTPlus 0.13.0
4. Werkzeug 0.16.1
5. MySQL 8.0

## Part 2: Finding the subject-wise toppers and overall top 3 students
  Python program to read the data from a CSV file and find the subject-wise toppers and overall best students in the class, given their marks in 6 subjects.
  
### Time Complexity Analysis:
**To find the subject toppers:** O(N*M) where, 'N' is the number of students and 'M' is the number of subjects.  
Generally, the number of subjects is a constant (6 in this case) therefore the complexity is to **O(N)**.  
    
**To find the best students:** O(N)  
Since we only want the best 3 students we can traverse through the total marks once, while maintaining and updating the top 3 students. This logic can be easily extended to find the top k students using lists, which makes the complexity O(N*k) where, 'N' is the total number of students and 'k' is the number of best students to find.  
In this case k is a constant (k=3) therefore the complexity is **O(N)**.  

#### Overall Time Complexity: O(N), N - Number of student records.
