import os

import pkg_resources


def run():

    # Reset setup.
    os.system("systemctl stop saraswati")
    os.system("userdel saraswati")

    # Create user.
    os.system("groupadd --system saraswati >/dev/null 2>&1")
    os.system(
        "useradd --system --create-home --shell /bin/bash --gid saraswati saraswati >/dev/null 2>&1"
    )

    # Add user to "audio" group.
    os.system("usermod --append --groups audio saraswati")

    # Fix ACLs on /dev/snd/*
    # https://askubuntu.com/a/37609
    os.system("setfacl -m u:saraswati:rw /dev/snd/* >/dev/null 2>&1")

    # Create spool directory.
    os.system("mkdir -p /var/spool/saraswati")
    os.system("chown -R saraswati:saraswati /var/spool/saraswati")

    # Copy two files from package to system.

    # Conditionally copy configuration settings blueprint if file does not exist on the system.
    if os.path.exists("/etc/default/saraswati"):
        print("WARNING: /etc/default/saraswati already exists, skip copying")
    else:
        defaultfile = pkg_resources.resource_filename(
            "saraswati.setup.systemd", "saraswati.default"
        )
        os.system(f"cp {defaultfile} /etc/default/saraswati")

    # Copy systemd unit and path-activation files. Always.
    unitfile = pkg_resources.resource_filename(
        "saraswati.setup.systemd", "saraswati.service"
    )
    pathfile = pkg_resources.resource_filename(
        "saraswati.setup.systemd", "saraswati.path"
    )
    os.system(f"cp {unitfile} {pathfile} /usr/lib/systemd/system/")

    os.system(
        "systemctl daemon-reload && systemctl enable saraswati"
    )
    print()
    print("Saraswati unit enabled successfully. The service will start when /dev/bus/usb is not empty.")
    print()

    # print("Start watching logfile using 'journalctl --unit=saraswati --follow'")
    # print()
    # os.system("journalctl --unit=saraswati --follow")
