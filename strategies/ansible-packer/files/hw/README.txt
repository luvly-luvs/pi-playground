VOLUME SELECTION
1) Add a enviromental variable in Balena called "VolumeSelection"
2) VolumeSelection = low OR medium OR high
Note: amixer sset 'Headphone' 50%    << this controls volume outut

KEY SWITCH SETUP
1) Add an enviromental variable when needed in Balena with the name "KeySwitch"
2) Write either of these options to tell the keyswitch what relay to turn on/off:
    KeySwitch = 1 >>> Open relay one when activated
    KeySwitch = 2 >>> Open relay two when activated
    KeySwitch = 3 >>> Open none when activated
    KeySwitch = 4 >>> Open both relays when activated
3) Key events are logged into the /data/data.db

DATABASE MANAGEMENT
To view data about the status of the unit stored in the /data/data.db use the following:
1) While in the backend use:  sqlite3 /data/data.db
2) .schema   (this will show the tables in the database that contain the information)

sqlite> .schema
CREATE TABLE EthernetLogs (date text, Ping_status text);
CREATE TABLE StatusLogs (date text, Voltage text, Temperature text, Memory text);
CREATE TABLE HardwareLogs (date text, PIC18 text, ScreenType text, CellModule text, Audio text, Camera text, Keypad text);
CREATE TABLE Pic18Logs (date text, AACK text, NACK text);
CREATE TABLE ResetLogs (date text, Reason text);

3) SELECT * from HardwareLogs;    (using SQL commands you can ask for the infromation in the tables. Hardware logs is an example)

sqlite> SELECT * from HardwareLogs;
2022-01-04 18:56:32.841668|OK|GEN3|FAIL|OK|OK|OK
2022-01-04 19:31:17.421991|OK|GEN3|FAIL|OK|OK|OK
2022-01-04 19:31:42.047343|OK|GEN3|FAIL|OK|OK|OK
2022-01-04 19:32:06.682346|OK|GEN3|FAIL|OK|OK|OK
2022-01-04 19:32:31.314470|OK|GEN3|FAIL|OK|OK|OK
2022-01-04 19:32:55.936182|OK|GEN3|FAIL|OK|OK|OK