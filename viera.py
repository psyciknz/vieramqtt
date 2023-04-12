import panasonic_viera

from dotenv import load_dotenv

load_dotenv()


def connect(self, host=None,app_id=None,encryption=None):
    if app_id is None:
        # Get pinn
        #rc.request_pin_code()
        # Interactively ask the user for the pin code
        #print("Asking for code")
        #pin = input("Enter code")
        # Authorize the pin code with the TV
        #print("Authorising")
        #rc.authorize_pin_code(pincode=pin)
        # Display credentials (application ID and encryption key)
        #print("sending result")
        #print(rc.app_id)
        #print( rc.enc_key)
    else:
        params = {}
        params["app_id"]= os.environ.get("APP_ID")
        params["encryption_key"]= os.environ.get("ENCRYPTION_KEY")

        rc = panasonic_viera.RemoteControl(host,**params)

    return rc
#def connect(self, host=None,app_id=None,encryption=None):



# Make the TV display a pairing pin code
# We can now start communicating with our TV
# Send EPG key
rc.send_key(panasonic_viera.Keys.home)