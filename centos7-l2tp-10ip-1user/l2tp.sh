#!/bin/bash

# 设置网络

sed -i '/^IPADDR/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/^PREFIX/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/^GATEWAY/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i 's/dhcp/static/g' /etc/sysconfig/network-scripts/ifcfg-eth0

a=( `cat ipstr.txt` )
b=( `cat ip.txt` )
c=( `cat l2tpip.txt` )
for ((i=0; i<10; ++i))
do
	echo "${a[$i]}${b[$i]}" >> /etc/sysconfig/network-scripts/ifcfg-eth0
	echo "PREFIX$i=24" >> /etc/sysconfig/network-scripts/ifcfg-eth0
done

#此处修改网关，天翼云一般默认是192.168.0.1，不需要修改
echo "GATEWAY0=192.168.0.1" >> /etc/sysconfig/network-scripts/ifcfg-eth0

sleep 5
systemctl restart network
echo "sleep 5"
ip addr

# 设置DNS，重启网络之后好像/etc/resolv.conf中的配置就被自动清除了
echo "nameserver 223.5.5.5" >> /etc/resolv.conf


# 安装xl2tpd和ipsec,并配置
rm -rf /etc/yum.repos.d/epel-7.repo
rm -rf /etc/yum.repos.d/Centos-7.repo

wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
wget -O /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo


yum make clean
yum install -y epel-release
yum install -y xl2tpd libreswan lsof
yum install -y iptables iptables-services

cat >/etc/xl2tpd/xl2tpd.conf <<EOF
[global]
listen-addr = 0.0.0.0
ipsec saref = yes
[lns default]
ip range = 172.16.100.10-172.16.100.100
local ip = 172.16.100.1
require chap = yes
refuse pap = yes
require authentication = yes
name = LinuxVPNserver
ppp debug = yes
pppoptfile = /etc/ppp/options.xl2tpd
length bit = yes
EOF


cat >/etc/ppp/options.xl2tpd <<EOF
ipcp-accept-local
ipcp-accept-remote
ms-dns  223.5.5.5

noccp
auth
#obsolete: crtscts
idle 1800
mtu 1410
mru 1410
nodefaultroute
debug
#obsolete: lock
proxyarp
connect-delay 5000

require-mschap-v2
EOF


#此处可以修改你想要的用户名密码
cat >/etc/ppp/chap-secrets <<EOF
# Secrets for authentication using CHAP
# client	server	secret			IP addresses
a1        *       123456        172.16.100.11
a2        *       123456        172.16.100.12
a3        *       123456        172.16.100.13
a4        *       123456        172.16.100.14
a5        *       123456        172.16.100.15
a6        *       123456        172.16.100.16
a7        *       123456        172.16.100.17
a8        *       123456        172.16.100.18
a9        *       123456        172.16.100.19
a10       *       123456        172.16.100.20


EOF


cat >/etc/ipsec.d/l2tp-ipsec.conf <<EOF
conn L2TP-PSK-NAT
    rightsubnet=0.0.0.0/0
    #dpddelay=10
    #dpdtimeout=20
	dpddelay=40
    dpdtimeout=130
    dpdaction=clear
    forceencaps=yes
    also=L2TP-PSK-noNAT
conn L2TP-PSK-noNAT
    authby=secret
    pfs=no
    auto=add
    keyingtries=3
    rekey=no
    ikelifetime=8h
    keylife=1h
    type=transport
    #设置本机IP,${b[0]}为本机IP
    left=${b[0]}
    leftprotoport=17/1701
    right=%any
    rightprotoport=17/%any

EOF

#此处可以修改预共享密钥
cat >/etc/ipsec.d/default.secrets <<EOF
: PSK "123456"
EOF



# 配置系统sysctl
cat >/etc/sysctl.d/60-sysctl_ipsec.conf <<EOF
net.ipv4.ip_forward = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.default.rp_filter = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.eth0.accept_redirects = 0
net.ipv4.conf.eth0.rp_filter = 0
net.ipv4.conf.eth0.send_redirects = 0
net.ipv4.conf.eth1.accept_redirects = 0
net.ipv4.conf.eth1.rp_filter = 0
net.ipv4.conf.eth1.send_redirects = 0
net.ipv4.conf.eth2.accept_redirects = 0
net.ipv4.conf.eth2.rp_filter = 0
net.ipv4.conf.eth2.send_redirects = 0
net.ipv4.conf.ip_vti0.accept_redirects = 0
net.ipv4.conf.ip_vti0.rp_filter = 0
net.ipv4.conf.ip_vti0.send_redirects = 0
net.ipv4.conf.lo.accept_redirects = 0
net.ipv4.conf.lo.rp_filter = 0
net.ipv4.conf.lo.send_redirects = 0
net.ipv4.conf.ppp0.accept_redirects = 0
net.ipv4.conf.ppp0.rp_filter = 0
net.ipv4.conf.ppp0.send_redirects = 0

EOF

sysctl -p /etc/sysctl.d/60-sysctl_ipsec.conf



systemctl stop firewalld
systemctl mask firewalld

# 设置filter规则
iptables  -F

iptables -I FORWARD -s 172.16.100.0/24 -j ACCEPT
iptables -I FORWARD -d 172.16.100.0/24 -j ACCEPT
iptables -A INPUT -p udp -m policy --dir in --pol ipsec -m udp --dport 1701 -j ACCEPT
iptables -A INPUT -p udp -m udp --dport 1701 -j ACCEPT
iptables -A INPUT -p udp -m udp --dport 500 -j ACCEPT
iptables -A INPUT -p udp -m udp --dport 4500 -j ACCEPT
iptables -A INPUT -p esp -j ACCEPT
iptables -A INPUT -m policy --dir in --pol ipsec -j ACCEPT
iptables -A FORWARD -i ppp+ -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT


# 设置nat规则
iptables -t nat -F

for ((i=0; i<10; ++i))
do
	iptables -t nat  -A POSTROUTING -o eth0 -d 0.0.0.0/0 -s ${c[$i]} -j SNAT --to-source ${b[$i]}
done

service iptables save
systemctl restart iptables
systemctl enable iptables
systemctl status iptables

systemctl start xl2tpd
systemctl enable  xl2tpd
systemctl status xl2tpd

systemctl start ipsec
systemctl enable ipsec
ipsec verify



systemctl restart network
ip addr
iptables -L -n --line-number -t nat