#!/usr/bin/python3

# git-in
# fast, user-friendly and security-focused
# git initialization script written in
# python

import os
import subprocess

# silent exec
def sexec(command): 
    try:
        subprocess.run(command, check=True, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # run a command in sh and redirect all output to devnull
    except subprocess.CalledProcessError as e:
        # if we get a non-zero exit code, catch it and return it
        return e.returncode
    else:
        # if successful, return 0
        return 0

def exec(command): 
    try:
        subprocess.run(command, check=True, shell=True)
        # run a command in sh
    except subprocess.CalledProcessError as e:
        # if we get a non-zero exit code, catch it and return it
        return e.returncode
    else:
        # if successful, return 0
        return 0
    
def checkcode(var, name):
    if var == 127:
        # exit with code 1 if we get code 127 from exec()
        print(f"=(x)> ERR: {name} is not installed or accessible from PATH.")
        exit(1)
    elif var == 0:
        # do nothing if we get code 0
        pass
    else:
        # exit with code 1 for everything else
        print(f"=(x)> ERR: Got unknown non-zero exit status {var} while checking for {name}.")
        exit(1)


HOME = os.environ["HOME"]

print("=> Conducting pre-flight checks...") 
# check the presence of programs required for git-in
checkcode(sexec("git --version"), "Git")
checkcode(sexec("gpg --version"), "GPG")
checkcode(sexec("ssh -V"), "SSH")

# check for SSH keys
print("\n\n=> Checking for existing SSH keys...")
if os.path.exists(f"{HOME}/.ssh"):
    RSA = False
    ED = False
    if os.path.exists(f"{HOME}/.ssh/id_rsa.pub"):
        print("=> Found RSA public key")
        RSA = True
    if os.path.exists(f"{HOME}/.ssh/id_ed25519.pub"):
        print("=> Found ED25519 public key")
        ED = True
else:
    print(f"=(!)> {HOME}/.ssh does not exist. Assuming no keys are available.")
    

# check for GPG keys
print("\n\n=> Checking for existing GPG keys...")
gpgkeyid = sexec("gpg --list-keys --with-colons --keyid-format=long | awk -F: '/^pub:/ { print $5 }'")
if gpgkeyid == "":
    print("=(!)> No GPG keys available. Would you like to generate some?")
    print("    (1) Generate")
    print("    (2) Abort")
    choice = input("=<( ")
    if choice == "2":
        print("=(x)> Abort.")
        exit(1)
    else:
        print("=> Generating GPG keys...")
        exec("gpg --full-generate-key")
        gpgkeyid = sexec("gpg --list-keys --with-colons --keyid-format=long | awk -F: '/^pub:/ { print $5 }'")

# choose which SSH keys to use
if not RSA and not ED:
    # give user the option of generating keys if they are not available
    print("=(!)> No SSH keys are available. Would you like to generate some?")
    print("    (1) Generate RSA")
    print("    (2) Generate ED25519")
    print("    (3) Generate both")
    print("    (4) Abort")
    choice = input("=<( ")
    if choice == "1":
        exec("ssh-keygen -t rsa")
        RSA = True
    elif choice == "2":
        exec("ssh-keygen -t ed25519")
        ED == True
    elif choice == "3":
        exec("ssh-keygen -t rsa")
        exec("ssh-keygen -t ed25519")
        RSA = True
        ED = True
    elif choice == "4":
        print("=(x)> Abort.")
        exit(1)
    else:
        print("=(x)> Invalid input. Abort.")
        exit(1)
elif RSA and ED:
    # if both are available, let the user choose one
    print("=(?)> Would you like to use your RSA key or ED25519 key?")
    print("    (1) RSA")
    print("    (2) ED25519")
    choice = input("=<( ")
    if choice == "1":
        print("=> Using RSA key")
        useRSA = True
        useED = False
    elif choice == "2":
        print("=> Using ED25519 key")
        useED = True
        useRSA = False
    else:
        print("=(!)> Invalid input. Assuming ED25519.")
        useED = True
        useRSA = False
elif RSA and not ED:
    print("=> Using RSA key")
    useRSA = True
    useED = False
elif not RSA and ED:
    print("=> Using ED25519 key")
    useED = True
    useRSA = False



# set up SSH
print("\n\n=> SSH key setup")
print("    Go to your GitHub account, click on your profile, drop")
print("    down to Settings, scroll to Access, and then click SSH")
print("    and GPG keys, and add the following key:\n\n")
if useED:
    exec(f"cat {HOME}/.ssh/id_ed25519.pub")
elif useRSA:
    exec(f"cat {HOME}/.ssh/id_rsa.pub")
input("\n\nOnce you have added your SSH key, press ENTER to add your GPG signing key.")

# set up GPG
print("\n\n=> GPG configuration")
print("    On the same page you added your SSH key, add your GPG key:")
input("=(!)> Press ENTER to continue. Your key is very long.\n\n")
exec(f"gpg --armor --export {gpgkeyid}")
input("\n\n=> Add this key to your GitHub account, and then press ENTER.")



# set up Git
print("\n\n=> Git configuration")
print("    Enter your name and email address for your Git configuration")
sexec(f'git config --global user.name "{input("Name =<( ")}"')
sexec(f'git config --global user.email "{input("Email =<( ")}"')

# configure Git for GPG
print("=> Configuring Git for GPG")
sexec("git config --global --unset gpg.format")
sexec(f"git config --global user.signingkey {gpgkeyid}")
print("=(?)> Would you like to configure Git to sign all commits automatically?")
print("    (1) Yes")
print("    (2) No")
choice = input("=<( ")
if choice == "1":
    sexec("git config --global commit.gpgsign true")


print("=(O)> Complete.")
