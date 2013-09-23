divvy2fitbit
============

Divvy2fitbit converts your divvy bike trips to fitbit activities.

It reads your trip information from Divvy (including date, source and destination stations,
and during), and employs Google Maps API to calculate the bicycling distance of the trip.
It then converts the trip into an "biking" activity and uploads to fitbit.

*Note:* right now Divvy does not offer exact times for trips, so we log everything
activity at 5:00pm. You can edit the starting time in fitbit, or change the time to 
something else. I am going to nag the Divvy developers to expose trip start time.

Prerequisites
-----------------

divvy2fitbit depends on the following python packages:

 * bs4 (for HTML parsing)
 * json (for JSON object parsing)
 * mechanize (for HTTP interacting)
 * fitbit (for fitbit interacting)
 
For the fitbit package, you will have to download the source code
from [my fork](https://github.com/xuy/python-fitbit), because right now
the [official](https://github.com/orcasgit/python-fitbit) does not
support activity logging.

Once you have python-fitbit installed, run

	fitbit/gather_keys_cli.py 65d8b86c275e4236a93a265dce3d86b2 752b2671061c4ba3b2f7c7dd8fc26eba
	
under the python-fitbit directory. This will authorize divvy2fitbit to update your 
activity data. Once the authorization is done, you will get a *user_key* and a 
*user_secert*. You will need them in the next step.

Now, you are ready to create a file called config.json under the divvy2fitbit
directory. The structure of the file should look like this:

    {
        "divvy": {
            "User Name":"Your Divvy User Name",
            "Password":"Your Divvy Password"
    },
        "fitbit": {
            "consumer_key" : "65d8b86c275e4236a93a265dce3d86b2",
            "consumer_secret" : "752b2671061c4ba3b2f7c7dd8fc26eba",
            "user_key" : "You need to authorize divvy2fitbit to modify your data on your behalf",
            "user_secret" : "You need to authorize divvy2fitbit "
        }
    }

Obviously, you will need to fill in the *User Name* and *Password* fields to get
trips informaton from Divvy. 
You will also need the *user_key* and *user_secret* pair generated from the last step.

Once you have the file ready, just run 

	python divvy2fitbit.py
	
After it is done processing, you will see those activities in fitbit. Hooray!
