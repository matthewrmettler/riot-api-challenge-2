# riot-api-challenge-2

This is my submission for Riot's API Challenge #2 ( https://developer.riotgames.com/discussion/announcements/show/2lxEyIcE )

A link to the web app showing off the analysis can be seen here: http://rylais-resolve.herokuapp.com/

There are two parts to this repository:

# The analysis folder:
Everything in the analysis folder was used in order to generate the data needed for the web app. What's not included are the databases generated (due to Riot's rules about spreading out collected data), but they can be generated again with access to the AP_ITEM_DATASET (available here: https://s3-us-west-1.amazonaws.com/riot-api/api_challenge/AP_ITEM_DATASET.zip ). * You do not need to do additional analysis runs to run the web app. * Everything collected has been stored into the JSON folder, included in the repo. 
  
You might need to comment or un-comment certain lines, but every file has a main function that does something. The order is as follows:
* file_calls.py : This makes API calls (requires Riot API key), using the match data from the AP_ITEM_DATASET, in order to generate a folder full of thousands upon thousands of match .json results. I'm not convinced this was a great method, but it's the one I chose. Due to API limiting, I thought it was okay to have ~10 GB worth of pure .json match history on my harddrive, just in case.
* api_calls.py : Has no actual main method, but file_calls and profile_builder use this to receive information from the Riot API.
* profile_builder.py : This creates an actual class containing all the information I need for one participant in one match. This class is the basis for creating the database tables in...
* db_calls.py: This uses those profiles created by profile_builder and starts adding rows to the database table 'Profile.' I then use those rows to generate additional tables as needed for the data I need for the web app. Once I have those extra tables, there's also methods in there to generate JSON files based off those database tables.
  These JSON files are used by dynatable and CanvasJS in order to display charts and graphs on the web app.
* helper.py : Additional methods used to help db_calls

# Flask app 
* If you're simply interested in seeing the app, all you need to do is run app.py as a Flask app, and it should work!
* If the tables don't appear, you will need to go into tables.js and make sure that you're pointing to specific JSON sources. Each table has a corresponding json file in the static/json folder, but they need to be hosted somewhere. I used myjson.com to host the data, but you can use whatever.
*  After that, you should be able to simply run the app.py Flask app (I use either the default Flask run through PyCharm, or I host it on Heroku and use gunicorn), and the web app should generate all those pretty tables!
  
  Any questions, feel free to message me. :)
