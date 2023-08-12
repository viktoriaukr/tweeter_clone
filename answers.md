# Part one

1. How is the logged in user being kept track of?
   As I can explain to myself, we can keep track of the logged in user because their information is being stored in the session and is being checked in each route if the user is logged in or not.
2. What is Flask’s g object?
   `g` or `global` is data shared between different parts of the code base within one request cycle.(Examples: database connection or the user that is currently logged in).
3. What is the purpose of add_user_to_g?
   To check if the user is logged in and to prevent the user that is currently not logged in from using the features of our application that require user to be logged in.
4. What does @app.before_request mean?
   It is a text decorator that allows us to execute any needed functions before the request is made. We use this decorator to do such things like: opening database connection,tracking user actions, it also can help the application to remember last page that user visited, etc.
