# Project Details

1. **Your Name and Stevens Login:**
   - Chuqing Ke 20012820
   - Wai Hou Cheang 20016381

2. **URL of Your Public GitHub Repo:**
   - [https://github.com/chloecck/Project3](https://github.com/chloecck/Project3)

3. **Estimated Hours Spent on the Project:**
   - 168 hours

4. **Description of How You Tested Your Code:**
   - Executed `./test.sh`.
   - Utilized `setup.sh` for dependency setup.
   - Conducted thorough testing with four test collections.
   - Sample result stored in `tmp.out` file.

5. **Bugs or Issues:**
   - None

6. **Example of a Difficult Issue or Bug and How You Resolved It:**
   - Addressed an issue during Gradescope upload by including Node.js version management in `setup.sh`: `npm cache clean -f`, `npm install -g n`, `n stable`.

7. **List of the Five Extensions You’ve Chosen to Implement:**

- **1. Users and User Keys:**
     - Brief: In this extension, we add a notion of user with a private user key, which moderately updates our posts schema. Each post can be associated with a user by providing the user_id and corresponding user key when creating the post. Whenever you give information about a post that has an associated user, you should return the associated user id along with other data (e.g., when reading and deleting posts). If a user created a post, it should be sufficient to provide the user’s key to delete the post. It should be clear whether the user is providing a post’s key or a user’s key.
     - Endpoints: `POST /user`, `GET /user`, `PUT /user/<int:user_id>/edit/<string:user_key>`.
     - Details: POST request to /user should have a body consisting of a JSON object with a string-valued field called username and a string-valued field called user_bio. If the input isn’t a JSON object or is missing any of the required field or any of the fields isn’t a string, should return status 400 (indicating ‘bad request’). It should return a JSON object with fields of: user_id, user_key, timestamp,username,user_bio.
     - This endpoint is stateful: it creates a new user that can be read or deleted (with the key). The id should be unique: no two users should share an id, The key is long enough and random enough to be secure,The timestamp should be the time the server processed this request, i.e., when the user was created.


- **2. User Profiles:**
    - Brief:Add metadata to users. At least one piece of metadata should be unique, which we used username. User creation must specify the unique part, which we used username; it may specify the non-unique parts, which we have the user_bio. There should be an API endpoint to retrieve a given user’s metadata given their id or their unqiue metadata: we include endpoints of read_user_metadata. There should be an API endpoint to edit a given user’s metadata; doing so requires the user’s key: We include endpoints of edit_user_metadata. When returning information about a post associated with a user, you must include the user’s unique metadata, which we implemented with the username.
    - Endpoints: `POST /users`, `GET /user`, `PUT /user/{{int:user_id}}/edit/{{string:user_key}}`.
    - Details: When we create a user, we implement the POST request to /users that have a body consisting of a JSON object with a string-valued field called username and a string-valued field called user_bio, and a response of a JSON object with fields of: user_id, user_key, timestamp,username,user_bio. This effectively include the necessary fields of user profiles required. 
    - The second end point is: A GET request to /user looks up the given integer id or given username in the body. If the user does not exist, it should return an error message with a 404 exit status (indicating ‘not found’). If the user does exist, it should return a JSON object with following fields: id should be an integer, timestamp should be an ISO 8601 timestamp in UTC, username should be a string, user_bio should be a string. The timestamp should be the same as was returned when the user was created. 
    - The third endpoint is a PUT request to  /user/{{int:user_id}}/edit/{{string:user_key}}. The request should have a body consisting of a JSON object with a string-valued field called username and a string-valued field called user_bio. If the user does not exist, it should return an error message with a 404 exit status (indicating ‘not found’). If the user does exist, it should return a JSON object with following fields: id should be an integer, timestamp should be an ISO 8601 timestamp in UTC, username should be a string, user_bio should be a string. The timestamp should be the same as was returned when the user was created. 

- **3. Threaded Replies:**
    - Details:  When creating a post, it should be possible to specify a post_id to which the new post is replying, we have the optional reply_to field inside the POST /post. When returning information about a post that is a reply, include the id of the post to which it is replying. If that post was created with a given reply_to, then inside the GET /post/{{int:post_id}}, it should have a int that specify which it is replying. When returning information about a post which has replies, include the int:post_id of every reply to that post. (it should not include replies to replies—for that, you should implement threads.). If there were posts created that were replying to the post I'm getting, then it would include a list of int:post_id specifying all the posts that were replying to the current post.


- **4. User-Based Range Queries:**
    - Endpoint: `GET /post`.
    - Details: Add an API endpoint that lets the user search for posts based by a given user. The endpoint should return a list of post information (i.e., id, the message, the timestamp, and any other post information, like the user). The endpoint implemented is the GET request to /post, which looks up the user's post given integer id or given username (or both but would do the id) in the body. If the user does not exist, it should return an error message with a 404 exit status (indicating ‘not found’). If the user does exist, it should return a list of JSON object each with following fields: id should be an integer,timestamp should be an ISO 8601 timestamp in UTC, msg should be a string, and user field.  If there's any replies_to, replies, then it would also contain them. The timestamp should be the same as was returned when the posts was created. 

- **5. Time-Based Range Queries:**
    - Endpoint: `GET /post`.
    - Details:  Add an API endpoint that lets the user search for posts based on a date/time. It should be possible to search with a starting date and time, and ending date and time, or both an ending date and time. The endpoint should return a list of post information (i.e., id, the message, the timestamp, and any other post information, like the user).
    - The endpoint implemented is the GET request to /post, which looks up the post given start time or given end time (or both) in the body.If the time periord specified is not valid, it should return an error message with a 400 exit status (indicating ‘bad request’).If the post does exist given the time range, it should return a list of JSON object each with following fields: id should be an integer,timestamp should be an ISO 8601 timestamp in UTC, msg should be a string.The timestamp should be the same as was returned when the posts was created.  If there's user, or any replies_to, replies, then it would also contain them.

8. detailed summaries of your tests for each of your extensions, i.e., how to interpret your testing framework and the tests you’ve written
## 1. Users and User Keys (Testing)



## 2. User Profiles (Testing)



## 3. Threaded Replies (Testing)



## 4. User-Based Range Queries (Testing)



## 5. Time-Based Range Queries (Testing)

