Next things To Do:
[DONE] When a user submits a hospital/lab register form, it goes to potential providers table
Once the admin approves the provider :- 
    0> [DONE] set status of the provider to "ACCEPTED"/"REJECTED"/"REVIEW"/"WITHDRAWN"
    1> (ACCEPTED) 
        i> [DONE] it creates a provider entry in the main table with the details
    2> [DONE] Record the verified_by and verified_at records
Update the routes and serviec to handle the newly modified work flow.
[DONE] Change the users table (hospital_id -> provider_id) (provider = hospital/lab)
[DONE] Remove the is_rejected fields from the Hospitals & Labs table.
    -> Added a status field to track the rejected, withdrawn, accepted and pending entries.
Thats IT !

Next things To Do:
ADD Role based admin functionality
What should be roles available to an admin(Moderator)
- root
- applications mod
- IDK