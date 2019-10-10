while [ true ]; do
	sleep 10
		sudo find /var/spool/saraswati/ -not -newermt '-25 seconds' -exec rm -rf {} \;
			sudo rsync -rv -e 'ssh -p <port> -i <path-to-key>' /var/spool/saraswati/ <server-address>
			  done
