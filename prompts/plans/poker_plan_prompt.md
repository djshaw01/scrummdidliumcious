SCRUMM poker feature.

We are first building a SCRUM poker system which will allow our developers to vote on story points, which build consensus on how complex each task is.
- This feature should incorpate a responsive UI and support both Light and Dark modes selectable by the user.
- This feature will require four pages
    
    - An Admin configuration page
      - Should allow the admin(s) to manage the list of team names
      - Should allow the admin(s) to manage and delete existing completed sessions.
      - Should allow the admin(s) to set the base URL for navigating to issue details in the agile system the team is using (Azure DevOps, Attlasian JIRA, etc)

    - The Entry page will display a list of existing sessions that have been performed.
       - Should be presented in a table
       - Should should order the list by most recent to least
       - Should support filtering by session name, sprint number, and/or team
       - Should have a button which allows a user to begin a new session
       - Should allow the user to click on a session and navigate to the Session detail page       
    
    - New session dialog.  This can be a modal, with a drawer style presentation from the right side of the screen.
       - Should present a drop down to select the team which will participate in the session.
       - Should allow the user to specify the session name. This should pre populate with the name of the last session for the selected team.
       - Should allow the user to specify the sprint number   
       - Should allow the user to select the voting card set.
          - Begin with a single card set. Fibonacci numbers 1 - 13 and include the '?', the '☕️', and the '♾️' emoji
       - Should include a UX element to allow the user to upload a list of stories/bugs to evaluate for voting. 
          - This file will be in CSV format and needs to contain:
                - Issue Type, ["Story", "Bug"]
                - Issue Key, this is the value we can append to the end of the base URL from the admin page to link back to the story by opening in a new browser tab
                - Summary, this is like the title for the issue
                - Description, this is the original description in the story, we may want to display the first 200 characters when showing in the Session detail; Optional
                - Story points, any story points already estimated, Optional
                - Element should show a tool tip describing what is needed.
                - File parsing of the CSV should not care about the order of the elements, and should be able to ignore any additional fields we do not care about.        
       - Should contain "Begin" and "Cancel" buttons.
       - When the user initiates the session (Begin)
          - Will create a new session and store it in the repository.
          - Will navigate the user to the Session detail page
          - Will update Entry Page adding the new session to the top of the list, which other users will see and join even if they are currently reviewing the page.
          - The user will become the "Leader" for the session.

       - Session detail page.
          - Will display a page with a status row and then two columns, navigation, and detail
             - The status row 
               - Should show the title of the session, icons with the initials of each participant in the session, and a "Leave Session" button. All users can see this. This should be presented horizontally. The leader's icon should be different enough that. all participants can identify the leader.
               - The Leader of the session should see an additional "Complete Session" button and a "Designate Leader".
                  - Designate Leader should display a modal to allow the current leader to relinquish the role and grant to another participant. If a new participant becomes leader, the status icons at the top of the page should be updated to reflect the new leader. The previous leader becomes a standard participant.
                  - Complete Session should mark the session as complete. All voting will cease, and no longer be recorded.
             - Navigation column will display cards vertically and allow the user running the session to be able to select a card and show detail on the second column. 
                - The width of this column should be about 25% of the page
                - The card will show the emoji for the issue type (Story, 📖), (Bug, 🐞), The Issue Key as a link back to the story in the agile system of record (if clicked should open in a new browser tab), The summary, and any estimated points, either from the upload, or through the voting completion process.
                - When the card is selected, all other users participating in the session will automatically have the page updated to show which navigation card is selected, and the detail column in the second column will be updated to show the selection.
                - The other participants can select different cards, and the detail column will update for only that participant, but the system should maintain the status that the participant who clicked on an inactive card is no long participating in the current complexity evaluation, and they should see a button on the status bar which allows them to "Rejoin" the current evaluation.
            - Detail column will display the detail of the story/bug in a vertical orientation unless otherwise stated. Each set of elements is outlined below
                1. The first elements of the page will display the type emoji, the type name, and the link to the issue. Display this horizontally
                2. The next element should display the summary, No heading for this is necessary
                3. The third element should display the description, Include the word "Description" as a heading above the description
                4. The forth element should display the current estimate, or '-' of not yet estimated. i.e. "Estimate: -" or "Estimate: 3", etc.
                5. The fifth element should display the voting cards. The heading above should be "Your Vote". The cards should be displayed horizontally
                  - When the participant votes, the page should display that card as selected, but only for that user.
                  - The user vote is not locked, they can click the same card again to remove thier vote and/or click another card to change thier vote.
                6. The sixth element be a heading with the words "All votes N/M" where N is the number of votes cast, and M is the number of participants in the session.
                   - When a participant votes, the should update with the number of participants who voted.
                7. The seventh element should be a place holder to display the card selections for each participant. This will also be rendered horizontally
                   - When a participant selects a card, this row will be updated with an anonymized card. Use a triple elipsis `...` to represent each selection. 
                   - Verticallu below the card, should show the icon of the participant that selected the card.
                   - Later, the Leader will have the oportunity to reveal all the cards.
                8. The eighth element will represent the actions. These actions should only be enabled for the leader. This should include the header "Actions"
                   - The first action item should be a "Reveal" button.
                   - After Clicking "Reveal"
                      - Will reveal all the selected anonymized cards on 7.
                      - Will remove/hide the "Reveal" button, and be replaced with/show only unique selected cards from 7. display this hoirizontally.  Only the Leader may click these, they should display but be disabled for other participants.
                      - Below the cards, display the Average of all the numeric values of the cards. '?', the '☕️', and the '♾️' all get a numeric value of 0 for the average calculation
                        - Below the Average, allow the Leader to type in a custom estimate value, and a "Save" button which will apply the custom estimated story points to the story.
