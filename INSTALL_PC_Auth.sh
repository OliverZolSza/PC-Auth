#!/bin/bash

if [[ $(id -u) -eq 0 ]]; then
    echo "Script is running as root. Run without sudo."
    exit 1  # Quit the script
fi

# Define variables
app_name="PC Auth"
version="1.0"
install_dir="/opt/$app_name"
executable="PC Auth"
desktop_file="$HOME/.local/share/applications/$app_name.desktop"

#Already installed?
if [ -d "$install_dir" ]; then
    echo "App already installed."
    echo "If this was an error, please uninstall the app and try again:"
    echo "To uninstall run UNINSTALL.sh at $install_dir/UNINSTALL.sh"
    exit 2
else
    echo "Directory does not exist."
fi

# Function to display usage instructions
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help       Display this help message"
    echo "  -p, --prefix     Specify installation directory (default: $install_dir)"
    echo "  -y, --yes        Automatic yes to prompts"
    echo "  -n, --no-prompt  Run without any user prompts"
    echo "  -v, --verbose    Display verbose output"
    exit 0
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -h|--help) usage ;;
        -p|--prefix) install_dir="$2"; shift ;;
        -y|--yes) YES=1 ;;
        -n|--no-prompt) NO_PROMPT=1 ;;
        -v|--verbose) VERBOSE=1 ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
    shift
done


# Proceed?
if [ -z "$NO_PROMPT" ]; then
    read -p "Proceed with installation? (Y/n) " choice
    case "$choice" in
        y|Y|'') echo "Proceeding with installation" ;;
        n|N) echo "Installation cancelled"; exit 3 ;;
        *) echo "Invalid choice, please try again later."; exit 4 ;;
    esac
fi


# Create installation directory
sudo mkdir -p "$install_dir"

# Copy everything to install directory
sudo cp -r * "$install_dir"

# Set permissions for the executable
sudo chmod +x "$install_dir/$executable"

# Create a desktop file for the application
cat > "$desktop_file" << EOF
[Desktop Entry]
Name=$app_name
Exec="$install_dir/$executable"
Path=$install_dir
Icon=$install_dir/assets/authenticator_icon.svg
Terminal=false
Type=Application
EOF

# Notify the user
echo "Installation completed."
echo "The application has been installed to: $install_dir"
echo "A desktop shortcut has been created."

# Run the application if user wants to
if [ -z "$NO_PROMPT" ]; then
    read -p "Do you want to run the application now? (Y/n) " choice
    case "$choice" in
        y|Y|'') "$install_dir/$executable" ;;
        n|N) echo "You can run the application later by executing: $install_dir/$executable" ;;
        *) echo "Invalid choice, please run the application manually later." ;;
    esac
fi
