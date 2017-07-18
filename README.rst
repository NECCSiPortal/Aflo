================
Develop Note
================
CREATE 2015/06/23


================
INSTALL & UNINSTALL
================
1) install command
    $ sudo python setup.py install --record files.txt

2) uninstall command
    $ sudo cat files.txt | sudo xargs rm -rvf

3) Database setting.
   - Login Mysql
   - Make aflo database.
     $ CREATE DATABASE aflo CHARACTER SET utf8;
     $ GRANT ALL PRIVILEGES ON aflo.* TO 'aflo'@'localhost' IDENTIFIED BY 'aflo';

4) aflo-api.conf
   - SQLAlchemy connection setting.

5) Make aflo tables.
   $ sudo aflo-manage --config-file=/home/user/workspace/aflo/etc/aflo-api.conf db_sync

================
RUN TEMPEST API TEST
================
This manual is Tempest API test example for running on local .
If you contribute a component
then necessary create shell-script('post_test_hook.sh' and 'pre_test_hook.sh') for "Jenkins".

Tempest API Test on a component use "Tempest project".

Procondition:
  - Get original tempest project, and it install to local.
  - Add service & endpoint data to keystone.
  - Load rc file(use source command).
  - Install your new component.

1) Copy your tempest code to original tempest.
  -> devstack
  $ sudo cp -r -f /home/user/git/Aflo/contrib/tempest/tempest/ /opt/stack/tempest
  -> packstack
  $ sudo cp -r -f /home/user/workspace/Aflo/contrib/tempest/tempest/ /var/lib/tempest

2) Run tests.
  -> devstack
  $ cd /opt/stack/tempest/
  -> packstack
  $ cd /var/lib/tempest/

  -> devstack
  $ ./run_tempest.sh tempest.api.aflo
  -> packstack
  $ sudo ./run_tempest.sh tempest.api.aflo

Infomation:
  - If [TypeError: Invalid credentials] has occurred.
  - Please check "Tempest Project" config file.
    File name is "tempest.conf".
