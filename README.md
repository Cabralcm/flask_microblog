# Flask Microblog

Blog using the Python Flask micro-framework.

Built following the  [`Flask Mega-Tutorial`](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

## Custom features added (not covered in tutorial):
1) User login by both Email or Username
2) [Only single user session at a time](https://stackoverflow.com/questions/23360019/disable-simultaneous-login-from-multiple-different-places-on-flask-login)

# Notes and Learnings

## Werkzeug (Security)

1) This package's method `werkzeug.security.generate_password_hash()` will automatically `salt` your generated password hash.

2) The output string from this method will contain: the `hash algorithm`, `salt` used to generate the hash, the resulting `hash`

3) The method `werkzeug.security.check_password_hash()` is used to verify the hash generated from a given password.

> Note, databases should NEVER store the password, they instead can store the `salt` and `hash` for each password.The salt should be randomly generated for each instance of a user's password. Passwords that are the same should have different salts.

`check_password_hash()` takes in the `output string` from `generate_password_hash()`, and the `password`. The reason why it works is because the `output string` contains the `salt` used to generate the `hash`. 
   