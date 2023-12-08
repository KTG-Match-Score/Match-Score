# MatchScore - organise, manage and explore tournaments and leagues

# Welcome!
### This application provides a friendly interface for creating, managing or just observing sports events and their statistics.
#### * Backend - developed in Python using Fast API
#### * Frontend - Jinja2 library, combined with some JavaScript are used to create a nice and intuitive UI
#### * Email verification - implemented with MailJet, verification code is required for email validation
#### * Encryption - passwords are enrypted with JWT and the hashed values are stored in the database for security
#### * Database - MariaDB is used as a database management system. You can see the schema of the tables in the picture:

<p align="center">
<img src="./data/MatchScoreSchema.png" alt="Database schema" width="70%"/>
</p>

---

#### The app is not deployed on a remote container so it requres to be cloned locally and configured in order to work. The required packages can be found in the requirements.txt file. Verification of the mailjet account relies on secret keys, which are stored as environment variables on the user's PC. You should contact us if you want to be provided access to the secret keys :)
---
### Brief functionality of the app:
```
Without registration you can:

 - explore all the tournaments by the interactive calendar in the landing page
 - view all the matches associated with every tournament
 - view detailed statistics for the tournaments, matches and for every player who took part 
 in a tournament
 - available sports at this point are football, tennis and athletics

With registration, depending on your user role you can:

 - manage your profile - upload a profile picture, link your profile to a player in the system
 - request to be promoted to "director" so you can manage events and profiles of existing players
 - create or remove players in the system
 - add players to sports clubs
 - create tournaments in three formats - knockout, league or single
 - add players/sports clubs to the tournaments, depending on the chosen format and the selected 
 sport
 - option to add prizes for the winners
 - edit the matches locations and played-on dates
 - edit the participants list of a single event
 - add results for every match
```


---
---

### Detailed description of the app and its functionality:

<p align="center">
<img src="./data/MS_landing_page.png" alt="Landing page" width="70%"/>
</p>

```
- When the server is started and you enter the url http://127.0.0.1:8000/ in the browser, 
the MatchScore landing page will be loaded.
- If you want to see the created tournaments, you can click on any tournament in the dedicated 
section. You can filter them by sport or you can select a date from the calendar to check if 
there are any events on this day.
- On the top right side the buttons for login and registration can be found.
    - If you already have an account in the system, just login with your username and password. 
    You will remain logged so you don't have to login every time you visit the site.
- The other option is to register in the system: 
    - You will be asked to provide a name, a strong password and a valid email address.
    - The email should be valid, because when you click "Register" we will send you a validation 
    code on this email. Be sure to check the Spam folder in your mailbox if you don't see the 
    message in the Inbox folder. 
    - For security reasons your profile will be created only after you provide the provided 
    validation code.
    - Users in system can happen to have the same names, but email addresses should be unique.
- By default your profile role will be "player" and will have a pictogram as default picture.
- If you want you can upload a new profile picture.
- If you want your profile to be linked to a participant profile in the system you can send a 
request from your dashboard.
- The benefit of that is that your picture will be shown when you or someone else views your 
statistics or when you appear as a participant in a match.
- If you want to be able to create events, manage the matches, adding scores or manage player 
profiles, from your dashboard you can send a request to be promoted to "director". When your 
request is approved by an admin, you will have the extended functionality which directors have.
- Admin users are created manually upon request to the developers team.
```    
```
- Creating tournaments:
    - The "Create tournament" button can be accessed from your dashboard and it will open a form
    where you should enter the specific details for the event you want to create.
    - Currently you can choose between three sports - football, tennis and athletics and three 
    formats - knockout, league or a single event.
    - You have to choose how many participants will take place in your tournament and how many
    participants every match will have. You have to specify if the players will be individuals or 
    teams.
    - You have the option to specify if there are any prizes for the players after the tournament 
    finishes. Be sure not to enter more prizes than the number of participants for the tournament :)
    - On the next screen you will enter the tournament participants. 
    - Enter a name or part of a name in the search field and the result will show you only players
    or sport clubs who play the sport you chose for the tournament (you can't put a tennis player 
    in a football tournament).
    - If you don't see the desired player in the results, then no such player exists in the 
    database, so you have the opportunity to create it manually or automatically.
    - Creating a player manually gives you options to enter more details for the player. 
    - If you are in a rush or you don't know details about the player, you may just click "Create 
    Automatically" and a player with the specified name will be created and will be associated with
    that sport.
    - The system will warn you if you try to put the same player twice in the tournament 
    or if you have reached the maximum number of players or if the players you entered are not 
    sufficient to create the tournament.
    - If you entered something in the prize field on the previous screen, the add prizes form will
    be shown on the next screen. Follow the instructions to add prizes for the players who 
    deserve them :)
    - You should now be able so see this tournament in the "Your Events" section on your dashboard.
    - After all the above steps are done the system will create the whole tournament structure
    along with all the necessary mathes for every stage of the tournament. 
        - For example: if you create a tournament with 16 players, the first stage will contain 
        8 matches between the players that you entered. The second stage will contain 4 matches with
        no players in. The last (Final) stage will also contain 4 matches with no players. The first
        match of the Final will be the final match for the tournament 1st and 2nd place and the 
        second match will be the playoff for 3rd and 4th place (this match will be created 
        automatically, but it's your choice to add result to it or not).
        - Another example: if you create a league with 4 players, the system will create a single
        stage and will generate 6 matches where everybody should play againts everybody. 
    - All the matches in the tournament you just created will have a played-on date which will be 
    the starting date of the tournament. The match's location will be "unknown location" and there
    will be no result.
    - Immediately after creating the tournament you can change the location and the played-on date
    of every match for a more informative view of the match.
    - When you go to the Match details, you will see the "Add Result" and "Edit Match" buttons. For
    convenience these buttons won't be shown if the user is not the owner of the tournament 
    (the person who created the tournament, so other directors won't mess with the results) or an
    admin.

- Editing matches and adding results:
    - If you are an admin or the "owner" of the tournament you can edit the details of matches. 
    For single events you can also change the participants of the event.
    - Pay attention when you change the date of the events, because it is connected with the 
    "Add result" functionality. Errors will be raised if you enter a date which is not within the
    tournament's start and end dates.
    - Although the "Add result" button will be visible while the match is marked as "not finished"
    you won't be able to actually add result (nothing will happen when you click the button).
    - For every player in the match there will be a field, where you will enter its result.
    - You will only be able to add result successfully when the time of the match is in the past,
    even if it's 1 second in the past :)
    - Pay attention on the way you enter the results:
        - For time-limited sports (football, basketball etc.) you should just enter a number which
        represents the player's score (2 for two goals, 87 for 87 points and so on).The result of 
        this example will be shown like that: 
                                        Player: 2
        - For score-limited sports like tennis you should enter the result of every set, separated
        by a comma (6,2,7 for player one; 1,6,5 for player two, for example). The result of this
        example will be shown like that: 
                                        Player one: 
                                        Place: 1, Score: 6 2 7
                                        Player two: 
                                        Place 2, Score: 1 6 5
        - For first-finisher sports (athletics) the numbers should also be comma separated in the 
        format "hours,minutes,seconds,milliseconds" (0,22,3,123 for example). The result of this
        example will be shown like that: 
                                        Player: 
                                        Place: 1, Score: 22:3,123
            - If no score if available you can just leave the field unchanged (0,0,0,0) and the 
            result will be shown like that:
                                        Player: 
                                        Place: №, Score: No result
    - If there is a mistake in the results that you enter, nothing will happen when you click
    "Add result". You can review your input and try to submit it again.
    - If everything was entered correctly, you will see a green pop up message "Result added" and 
    you can navigate back to the match, to the tournament or the main page using the provided 
    buttons in the top bar.
    - After adding result to a match, the buttons "Edit match" and "Add result" will be hidden 
    permanently and the match will be marked as "finished".
    - If you entered wrong results you will have to contact the dev team to mark the match as "not
    finished" so the results can be entered again.
    - If the match is part of a knockout tournament, the winner will be automatically assigned to 
    the corrensponding match in the next stage of the tournament (if there is next stage).
    - If the match is part of the Semi-final stage of a knockout tournament, the winner will be 
    assigned to the Final match (1st and 2nd place in the tournament) and the loser will be 
    assigned for the Final playoff match (3rd and 4th place).
```

## If you read all the other contents of the file - Thank You for the time spent in studiyng our app! If you have interest in using the app and further development suggestions, please contact anyone from the dev team!
# Bye :)