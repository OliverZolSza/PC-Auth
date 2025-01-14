#!/bin/bash

if [[ $(id -u) -eq 0 ]]; then
    echo "Script is running as root. Run without sudo."
    exit 1  # Quit the script
fi

# Define variables
APP_NAME="PC Auth"
INSTALL_DIR="/opt/$APP_NAME"
DESKTOP_FILE="$HOME/.local/share/applications/$APP_NAME.desktop"

#App installed?
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory exists"
else
    echo "Directory does not exist."
    echo "If this was an error, please try again:"
    echo "To install run INSTALL_PC_Auth.sh"
    exit 2
fi

# Function to display usage instructions
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help    Display this help message"
    exit 3
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
    shift
done

# Function to remove a directory
remove_directory() {
    local directory="$1"
    if [ -d "$directory" ]; then
        echo "Removing directory: $directory"
        sudo rm -rf "$directory"
    fi
}

# Function to remove a file
remove_file() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "Removing file: $file"
        sudo rm -f "$file"
    fi
}

# Proceed?
if [ -z "$NO_PROMPT" ]; then
    read -p "Proceed with uninstallation? WARNING: REMOVES ALL OTPAUTH CODES YOU HAVE SAVED! (Y/n) " choice
    case "$choice" in
        y|Y|'') echo "Proceeding with uninstallation" ;;
        n|N) echo "Uninstallation cancelled"; exit 4 ;;
        *) echo "Invalid choice, please try again later."; exit 5 ;;
    esac
fi

# Remove the installation directory
remove_directory "$INSTALL_DIR"

# Remove the desktop file
remove_file "$DESKTOP_FILE"


# Notify the user
echo "Uninstallation completed."

# End of script
