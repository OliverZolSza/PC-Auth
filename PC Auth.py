import pyotp # For codes generation
import ttkbootstrap as ttk # For meters
from PIL import Image, ImageTk # For icon
from customtkinter import * # For GUI
#cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
#other
import os
import pyperclip # Clipboard copying
import sys

#region set variables
MINWIDTH, MINHEIGHT = 550, 400
SETTINGS_LABEL_COLOUR = "gray70"

code_labels = []
account_name_labels = []
copy_buttons = []
lines_of_file = []

app_name = "PC Auth"
app = CTk()
app.geometry("1200x850")
app.title(app_name)
app.minsize(MINWIDTH, MINHEIGHT)
app.iconphoto(True, ImageTk.PhotoImage(Image.open(os.path.join("assets", "authenticator_icon.png"))))


FontManager().load_font(os.path.join("assets", "Roboto-Medium.ttf"))

code_font = CTkFont("Roboto", 50)
account_name_font = CTkFont("Roboto", 25)
#endregion

class RadioButtonFrame(CTkFrame):
    def __init__(self, master, title, values, default = 0):
        super().__init__(master)

        if len(values) == 0:
            raise ValueError("Must give more than 0 values")

        self.configure(fg_color = "transparent")

        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = StringVar(value="")

        self.title = CTkLabel(self, text=self.title, fg_color=SETTINGS_LABEL_COLOUR, corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)
        
        self.radiobuttons[default].select()

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

#region TOTP functions

#To generate from file use linesOTP(readLines())[0] -> [0]=codes [1]=account names

def read_lines(path = './codes.txt'):
    # Open the file in read mode
    with open(path, 'r') as file:
        lines = file.readlines()
    return lines

def generateOTP(otpauth_url):
    try:
        # Parse OTPauth URL to get the secret
        otp_data = pyotp.parse_uri(otpauth_url)
        secret = otp_data.secret
        account_name = otp_data.name or "Unknown Account"
        # Generate OTP
        otp = pyotp.TOTP(secret)
        otp_code = otp.now()
        return otp_code, account_name
    except ValueError as e:
        print(f"Error parsing OTPauth URL: {otpauth_url}. Error: {e}")
        sys.exit(4)

def linesOTP(lines):
    codes = []
    account_names = []
    for line in lines:
        code, account_name = generateOTP(line.strip())
        codes.append(code)
        account_names.append(account_name)
    return codes, account_names

#endregion

#region encryption functions

# Function to derive a base64-encoded key from a password and salt
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

# Encrypt function modified to generate and use a salt
def encrypt_file_with_password(file_path = "./codes.txt", password = ""):
    salt = os.urandom(16)  # Generate a new salt
    key = derive_key(password, salt)
    cipher = Fernet(key)

    with open(file_path, 'rb') as file:
        original_content = file.read()

    encrypted_content = cipher.encrypt(original_content)

    encrypted_file_path = file_path + '.encrypted'
    with open(encrypted_file_path, 'wb') as file:
        file.write(salt + encrypted_content)  # Prepend the salt to the encrypted content

    print("File encrypted successfully with password.")

# Decrypt function modified to read and use the salt
def decrypt_file_with_password(encrypted_file_path = "./codes.txt.encrypted", password = ""):
    with open(encrypted_file_path, 'rb') as file:
        salt = file.read(16)  # Read the salt from the beginning of the file
        encrypted_content = file.read()

    key = derive_key(password, salt)
    cipher = Fernet(key)

    decrypted_content = cipher.decrypt(encrypted_content)

    decrypted_file_path = encrypted_file_path[:-len('.encrypted')]
    with open(decrypted_file_path, 'wb') as file:
        file.write(decrypted_content)

    print("File decrypted successfully with password.")

def decrypt_to_lines(encrypted_file_path = "./codes.txt.encrypted", password = ""):
    with open(encrypted_file_path, 'rb') as file:
        salt = file.read(16)  # Read the salt from the beginning of the file
        encrypted_content = file.read()

    key = derive_key(password, salt)
    cipher = Fernet(key)

    decrypted_content = cipher.decrypt(encrypted_content)

    lines = decrypted_content.decode('utf-8').split("\n")

    lines = [x for x in lines if x]

    return lines

#endregion

#region main functions

def make_labels():
    global code_labels
    global account_name_labels
    global copy_buttons
    for line_index in range(len(lines_of_file)):
        # Account Labels
        account_name_labels.append(CTkLabel(master = scroll, text = "Error loading this account's name.", font = account_name_font))
        account_name_labels[line_index].pack(pady = 10, anchor = "w")

        # Code labels
        # This error message will be overwritten if no error
        code_labels.append(CTkLabel(master = scroll, text = "Error loading this code.", font = code_font))
        # Places the code to the right
        code_labels[line_index].pack(pady = 10, anchor = "e") # Note: laggy if pady is not specified

        copy_buttons.append(CTkButton(master = scroll, text = "COPY", font = account_name_font, command = lambda index=line_index: (app.clipboard_clear(), app.clipboard_append(code_labels[index].cget("text")), app.update() )  ))
        # Places the button to the right
        copy_buttons[line_index].pack(pady = 10, anchor = "e")

def update_code_labels():
    for label_index in range(len(code_labels)):
        code_labels[label_index].configure(text=linesOTP(lines_of_file)[0][label_index])
    app.after(100, update_code_labels)

def load_account_names():
    for label_index in range(len(account_name_labels)):
        account_name_labels[label_index].configure(text=linesOTP(lines_of_file)[1][label_index])

def copy_code(index):
    pyperclip.copy(code_labels[index].cget("text"))
    print(code_labels[index].cget("text"))

#endregion

#region command line operations

command_line_arguments = sys.argv

if len(command_line_arguments) > 1:
    command_line_arguments.pop(0)
    
    old_password = command_line_arguments[0]
    new_password = command_line_arguments[1]

    try:
        decrypt_to_lines(password = old_password)
    except:
        print("ERROR: INCORRECT PASSWORD")
        sys.exit(1)

    
    with open("./codes.txt.encrypted", 'rb') as file:
            salt = file.read(16)  # Read the salt from the beginning of the file
            encrypted_content = file.read()

    old_key = derive_key(old_password, salt)
    cipher = Fernet(old_key)

    decrypted_content = cipher.decrypt(encrypted_content)
    
    salt = os.urandom(16)  # Generate a new salt
    new_key = derive_key(new_password, salt)
    cipher = Fernet(new_key)


    encrypted_content = cipher.encrypt(decrypted_content)

    encrypted_file_path = 'codes.txt.encrypted'
    with open(encrypted_file_path, 'wb') as file:
        file.write(salt + encrypted_content)  # Prepend the salt to the encrypted content

    try:
        decrypt_to_lines(password = new_password)
    except:
        print("ERROR: FAILED")
        sys.exit(2)

    print(f"Successfully changed password: '{old_password}' to: '{new_password}'")

    sys.exit()

#endregion

#region MAIN

# app.iconbitmap(os.path.join(".", "assets", "authenticator_icon.svg"))

inputted_password = CTkInputDialog(text="Password:", title="PASSWORD").get_input()

try:
    lines_of_file = decrypt_to_lines(password = inputted_password)
except:
    print("ERROR: CHECK PASSWORD")
    sys.exit(3)

#region  Set up Tabview
tabview = CTkTabview(master = app)
tabview.pack(expand = True, fill = "both")
codes_tab = tabview.add("Codes")
settings_tab = tabview.add("Settings")

for button in tabview._segmented_button._buttons_dict.values():
    button.configure(width=100, height=60, font=("Roboto", 40)) #Change font using font object

# Set up the first tab
scroll = CTkScrollableFrame(master = codes_tab)
scroll.pack(expand = True, fill = "both")

#endregion

#region SETTINGS
# theme_radio_group = RadioButtonFrame(settings_tab, "Set colour theme", values=["System", "Light", "Dark"])
# theme_radio_group.pack(anchor = "w")

title = CTkLabel(settings_tab, text="Operations", fg_color=SETTINGS_LABEL_COLOUR, corner_radius=6)
title.pack(anchor = "w")

title = CTkLabel(settings_tab, text="Importing reads a codes file(unencrypted) from the installation location", fg_color="transparent", corner_radius=6)
title.pack(anchor = "w")

title = CTkLabel(settings_tab, text="REQUIRES APP RESTART AFTER IMPORT", fg_color="red", corner_radius=6)
title.pack(anchor = "w")

import_button = CTkButton(settings_tab, text="Import", corner_radius=6, command = lambda: encrypt_file_with_password(password = "password"))
import_button.pack(anchor = "w")

title = CTkLabel(settings_tab, text="Exporting saves a codes file(unencrypted!!!) to the installation location", fg_color="transparent", corner_radius=6)
title.pack(anchor = "w")

export_button = CTkButton(settings_tab, text="Export", corner_radius=6, command = lambda: decrypt_file_with_password(password = "password"))
export_button.pack(anchor = "w", )

#endregion

# Load
make_labels() # Makes all labels
load_account_names() # Runs once
update_code_labels() # Continuously update labels every 100 milliseconds

app.mainloop()

#endregion