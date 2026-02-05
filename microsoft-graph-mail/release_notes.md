#### What's Improved
#### Following enhancements have been made to the Microsoft Graph Mail connector in version 1.4.0: 
- Added support for `Email Templates` in the action `Send Email` (only available in FortiSOAR™ v7.6.5 and later).
- Added a new parameter `Body Type` for the action `Send Email` with the following options:
    - `Rich Text`
    - `Email Template`
- Resolved an issue where email attachments were being ingested during the data ingestion wizard setup.
#### What's Fixed
- Fixed an issue where inline images were not being extracted as attachments.