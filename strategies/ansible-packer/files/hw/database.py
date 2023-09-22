import sqlite3

def logPingData(timestamp, status):
    """Saves Ethernet ping status on DB table (status = Fail or Success)
    Timestamp \ Status \
    1-23-93   \  OK     \
    """
    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE EthernetLogs (date text, Ping_status text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, status),
    ]
    cur.executemany("INSERT INTO EthernetLogs VALUES (?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logHardwareData(timestamp, PIC18, Screentype, CellModule, Audio, Camera, Keypad):
    """Saves Hardware status on DB table
     Timestamp \ Microchip (PIC18) \ ScreenType \ CellModule \ Audio \ Camera \ Keypad
     1-23-93   \      OK            \  TOUCH     \   OFF      \  OK   \  OK    \   OK
    """

    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE HardwareLogs (date text, PIC18 text, ScreenType text, CellModule text, Audio text, Camera text, Keypad text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, PIC18, Screentype, CellModule, Audio, Camera, Keypad),
    ]
    cur.executemany("INSERT INTO HardwareLogs VALUES (?,?,?,?,?,?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logPIC18Data(timestamp, AACK, NACK):
    """Saves PIC18 status on DB table
     Timestamp \ AACK  \ NACK \
     1-23-93   \  OK    \ OK   \
    """

    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE Pic18Logs (date text, AACK text, NACK text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, AACK, NACK),
    ]
    cur.executemany("INSERT INTO Pic18Logs VALUES (?,?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logStatusData(timestamp, voltage, temp, memory):
    """Saves status on DB table
     Timestamp \ Voltage  \ Temperature \ Memory \
     1-23-93   \  1.33    \     60.2     \   994  \
    """

    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE StatusLogs (date text, Voltage text, Temperature text, Memory text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, voltage, temp, memory),
    ]
    cur.executemany("INSERT INTO StatusLogs VALUES (?,?,?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logResetData(timestamp, reason):
    """Saves Reset status on DB table
    Timestamp \     reason    \
    1-23-93   \  PIC18 AACK    \
    1-24-93   \  ETHERNET PING  \
    1-25-93   \  NO KEYPAD       \
    """
    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE ResetLogs (date text, Reason text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, reason),
    ]
    cur.executemany("INSERT INTO ResetLogs VALUES (?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logKeyEvent(timestamp, State):
    """Saves Key events when switch is engaged on DB table
    Timestamp \ KeyEvents \
    1-23-93   \ OPEN      \
    1-23-93   \ CLOSED    \
    """
    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE KeyEvents (date text, KeyEvents text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, State),
    ]
    cur.executemany("INSERT INTO KeyEvents VALUES (?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logAccelEvent(timestamp, event):
    """Saves accelerometer events on DB table
    Timestamp \ Status   \
    1-23-93   \Triggered \
    """
    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE AccelLogs (date text, Events text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, event),
    ]
    cur.executemany("INSERT INTO AccelLogs VALUES (?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logTamperData(timestamp, tamper):
    """Saves Tamper Switch status on DB table
    Timestamp \ Tamper         \
    1-23-93   \  Frontplate OPEN     \
    1-23-93   \  Frontplate CLOSED     \
    """
    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE TamperSwitchLogs (date text, Status text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, tamper),
    ]
    cur.executemany("INSERT INTO TamperSwitchLogs VALUES (?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

def logEEPROM(timestamp, EEPROM):
    """Saves EEPROM on DB table
    Timestamp \ EEPROM \
    1-23-93   \  AISBIDBAJISDBFJN  \
    """
    con = sqlite3.connect('/data/data.db')
    cur = con.cursor()
    try:
        # Create table
        cur.execute('''CREATE TABLE EEPROMLogs (date text, EEPROM text)''')
    except:
        print("Logged in database")
    # The qmark style used with executemany():
    lang_list = [
        (timestamp, EEPROM),
    ]
    cur.executemany("INSERT INTO EEPROMLogs VALUES (?,?)", lang_list)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()
