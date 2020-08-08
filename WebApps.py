import RPi.GPIO as GPIO
import os
import time
import decimal
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from w1thermsensor import W1ThermSensor
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

#ledpin waar lampje op aangesloten staat
ledPin = 6
# Zet de pinmode op Broadcom SOC.
GPIO.setmode(GPIO.BCM)
# Zet waarschuwingen uit.
GPIO.setwarnings(False)
# Zet de GPIO pin als uitgang.
GPIO.setup(ledPin, GPIO.OUT)

sensor = W1ThermSensor()

try:
    connection = mysql.connector.connect(host='db4free.net',
                                         database='plantjesvanglenn',
                                         user='glennbeeckman',
                                         password='********', #changed password in githubRepo because public
                                         port='3306',
                                         connect_timeout=100000)
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        print("\n\n")
        while True:            
            #bar.txt verwijderen als het al bestaat
            os.system("sudo rm /media/pi/HddGlenn/Plantjes_WebApps/bar/bar.txt")
            #script uitvoeren met oudere python versie en opslaan als bar.txt    
            os.system("python /home/pi/mu_code/bartest.py >> /media/pi/HddGlenn/Plantjes_WebApps/bar/bar.txt")
            #bar2.txt verwijderen als dit al bestaat
            os.system("sudo rm /media/pi/HddGlenn/Plantjes_WebApps/bar/bar2.txt")
            #enkel de waarde van de luchtdruk opslaan
            os.system("sudo cut -d ' ' -f7 /media/pi/HddGlenn/Plantjes_WebApps/bar/bar.txt >> /media/pi/HddGlenn/Plantjes_WebApps/bar/bar2.txt")
            
            #os.system slaat ook de stopcode (0) op, we moeten het dus openen als bestand en zo de waarde opslaan
            with open("/media/pi/HddGlenn/Plantjes_WebApps/bar/bar2.txt") as bar2text:
                luchtdrukWaarde = bar2text.read()
                print("de luchtdruk is: " + luchtdrukWaarde)
            #de luchtdruk is een string -> omzetten naar decimal    
                luchtdrukWaarde = decimal.Decimal(luchtdrukWaarde)
            
            print("De luchtdruk is momenteel", luchtdrukWaarde, "hPa\n")
            
            temp = sensor.get_temperature()
            print("De te'mperatuur is momenteel %s graden C.\n" % temp)
            
            #huidige tijd opslaan
            huidigetijd = datetime.now()
            #huidige tijd omzetten nr acceptabel formaat
            tijdGoedFormaat = huidigetijd.strftime("%Y_%m_%d_%H_%M_%S")
            naamFoto = tijdGoedFormaat + ".jpg"
            print("de huidige tijd en de naam van de foto wordt:" , naamFoto)
            
            print("testfoto 1 wordt genomen...")
            #led lampja aanzetten
            GPIO.output(ledPin, 1)
            time.sleep(2)
            cmd = "fswebcam -r 1920x1080 /home/pi/test.jpg"
            os.system(cmd)
            time.sleep(2)
            #led lampje uitzetten
            GPIO.output(ledPin, 0)
            print("testfoto 1 klaar!\n")
            
            print("testfoto 2 wordt genomen...")
            #led lampja aanzetten
            GPIO.output(ledPin, 1)
            time.sleep(2)
            cmd = "fswebcam -r 1920x1080 /home/pi/test.jpg"
            os.system(cmd)
            time.sleep(2)
            #led lampje uitzetten
            GPIO.output(ledPin, 0)
            print("testfoto 2 klaar!\n")
            
            print("testfoto 3 wordt genomen...")
            #led lampja aanzetten
            GPIO.output(ledPin, 1)
            time.sleep(2)
            cmd = "fswebcam -r 1920x1080 /home/pi/test.jpg"
            os.system(cmd)
            time.sleep(2)
            #led lampje uitzetten
            GPIO.output(ledPin, 0)
            print("testfoto 3 klaar!\n")

            print("Foto wordt genomen...")
            #led lampja aanzetten
            GPIO.output(ledPin, 1)
            time.sleep(2)
            cmd = "fswebcam -r 1920x1080 /media/pi/HddGlenn/Plantjes_WebApps/images/" + naamFoto
            os.system(cmd)
            time.sleep(2)
            #led lampje uitzetten
            GPIO.output(ledPin, 0)
            print("Foto klaar!\n")            
            
            print("pushing luchtdruk data to db...")
            cmd ="INSERT INTO luchtdruk (datum, waarde) VALUES ('%s', %s);" % (huidigetijd, luchtdrukWaarde)
            print("query: " + cmd)
            cursor.execute(cmd)
            connection.commit()
            print("luchtdruk pushed to db\n")
            
            print("pushing temperatuur to db")
            cmd ="INSERT INTO temperatuur (datum, waarde) VALUES ('%s', '%s');" % (huidigetijd, temp)
            print("query: " + cmd)
            cursor.execute(cmd)
            connection.commit()
            print("fotonaam pushed to db\n")
            
            print("pushing photo to dropbox")
            
            # Access token = NO LONGER VALID BECAUSE OF PUBLIC GITHUB REPO
            TOKEN = 'QnCiOMDUNBAAAAAAAAAAC6IKm3WBapjdoOH4mFUo5snJg1i5jfdSFs-QnkdMTrHl'

            LOCALFILE = str('/media/pi/HddGlenn/Plantjes_WebApps/images/' + naamFoto)
            BACKUPPATH = str('/' + naamFoto) # Keep the forward slash before destination filename

            # Uploads contents of LOCALFILE to Dropbox
            def backup():
                with open(LOCALFILE, 'rb') as f:
                    # We use WriteMode=overwrite to make sure that the settings in the file
                    # are changed on upload
                    print("Uploading " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
                    try:
                        dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
                    except ApiError as err:
                        # This checks for the specific error where a user doesn't have enough Dropbox space quota to upload this file
                        if (err.error.is_path() and
                                err.error.get_path().error.is_insufficient_space()):
                            sys.exit("ERROR: Cannot back up; insufficient space.")
                        elif err.user_message_text:
                            print(err.user_message_text)
                            sys.exit()
                        else:
                            print(err)
                            sys.exit()


            # Adding few functions to check file details
            def checkFileDetails():
                print("Checking file details")

                for entry in dbx.files_list_folder('').entries:
                    print("File list is : ")
                    print(entry.name)

            # Run this script independently
            if __name__ == '__main__':
                # Check for an access token
                if (len(TOKEN) == 0):
                    sys.exit("ERROR: Looks like you didn't add your access token. Open up backup-and-restore-example.py in a text editor and paste in your token in line 14.")

            # Create an instance of a Dropbox class, which can make requests to the API.
            print("Creating a Dropbox object...")
            dbx = dropbox.Dropbox(TOKEN)

            # Check that the access token is valid
            try:
                dbx.users_get_current_account()
            except AuthError as err:
                sys.exit(
                    "ERROR: Invalid access token; try re-generating an access token from the app console on the web.")

            try:
                checkFileDetails()
            except Error as err:
                sys.exit("Error while checking file details")

            print("Creating backup...")
            # Create a backup of the current settings file
            backup()
    
            result = dbx.files_get_temporary_link(BACKUPPATH)

            fotoUrl = str(result.link)

            print("photo uploaded to dropbox!")
            
            print("pushing fotonaam (as url to db")
            cmd ="INSERT INTO fotoNaam (datum, naam) VALUES ('%s', '%s');" % (huidigetijd, fotoUrl)
            print("query: " + cmd)
            cursor.execute(cmd)
            connection.commit()
            print("fotonaam pushed to db\n")
            
            
            print("loop succesvol afgewerkt")
            print("2 uur wachten voor volgende loop...")
            print("laatste loop: " + tijdGoedFormaat )
            print("---------------------------------------------------------\n")
            time.sleep(7200)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")