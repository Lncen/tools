

#先安装wget
yum install -y wget


注意：
1、此脚本适用于centos7.6系统，别的系统没有测试过
2、创建云主机时记得把安全组完全放开

步骤：
1、使用xshell等工具登陆centos，使用云主机的主IP登陆
2、修改ip.txt
	a、查看本机所有内网ip
	c、一共10个内网ip依次填入ip.txt,本机内网主ip要在第一个，然后保存
3、修改vpn账号密码
	可以不修改，默认为vpn1-10,密码 hm123456 预共享密钥hm123456
2、将脚本文件夹上传至centos
3、进入文件夹执行脚本
	 cd centos7-l2tp-10ip-1user
	 bash l2tp.sh

