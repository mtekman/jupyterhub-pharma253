#!/bin/bash

negative="\nAction: Quitting, without doing anything.\nReason:"

# Check if user has sudo privileges
if ! [ "$EUID" -eq 0 ]; then
    echo -e "${negative} Please run script as sudo."
    exit 255
fi

read -p "username (e.g. alother, sarnold, spreissl): " username
read -p "Real Name (e.g. Achim Lother, etc.): " realname

if [ "$username" == "" ]; then
    echo -e "${negative} Username is blank."
    exit 255
fi
if [ "$realname" == "" ]; then
    echo -e "${negative} Real Name is blank"
    exit 255
fi

homedir=/media/daten/$username;

echo -e "\nThis will create a new account for\n\n              \t'${realname}'\nwith username:\t'${username}'\nwith a home at:\t'${homedir}'\n"
read -p "Type 'YES' to proceed: " ans
if [ "$ans" != "YES" ]; then
    echo "$negative"
    exit 255
fi

## Sanity check
if id "${username}" >/dev/null 2>&1; then
    echo -e "${negative} User with that username ($username) already exists."
    echo "Either check your inputs, or remove that user first, via 'sudo userdel $username'."
    exit 255
fi

if [[ -d ${homedir} ]]; then
    echo -e "${negative} The directory '${homedir}' already exists."
    echo "Either check your inputs, or remove that directory first, via 'sudo rmdir $homedir'."
    echo "It should be empty first before you do this."
    exit 255
fi

## Proceed
sudo useradd -m -d "${homedir}" -s /bin/bash -c "${realname}" "${username}";
sudo passwd "${username}"

echo "Action: Complete"