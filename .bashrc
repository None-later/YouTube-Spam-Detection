# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions
source env/bin/activate
export http_proxy="http://10.3.100.207:8080"
export https_proxy="https://10.3.100.207:8080"
