sysctl -w net.ipv4.conf.eth0.route_localnet=1
git pull
python3 manage.py runserver