Webistrano-capify project
==============

If you use webistrano, this app will generate Capfile from your existing
webistrano project. Purpose of this project is to help transition from
webistrano app to Capfile being 100% backward compatible.

Overview
========

Webistrano-capify consists of :

- command that has to be run in order to "capify" your git project -
curl -L http://yourserver.com
- webserver application - server.py, which is just a Python-bottle app
that has access to webistrano's database

How to use it?
=============

1. Install server.py as a backend on webistrano host (it has to have
   access to webistrano mysql db) under let's say http://myhost.com
2. run : curl -L http://myhost.com | python
3. ????
4. PROFIT

Details
=======

- allow access to http://yourhost.com/projects/X/stages/Y/capfile to your host that runs server(.py) with http auth only (skip_before_filter auth in stages_controller#capfile)
- grant access for mysql user to webistrano db for server(.py)-side

Installation
============

On the server:
- install Python Bottle framework with 
<code> 
easy_install bottle
</code>
- checkout your project somewhere in /my/secret/directory/ via 
<code> 
git clone git@github.com:wzin/webistrano-capify.git 
</code>
- configure your global.cfg file on the basis of .example file - you
  will need to expose your webistrano "capfile" route to access without
  login, and enable nginx http auth for it. To disable login just apply
  the patch:
  <code>
  diff --git a/app/controllers/stages_controller.rb b/app/controllers/stages_controller.rb
  old mode 100644
  new mode 100755
  index 7990935..43602e3
  --- a/app/controllers/stages_controller.rb
  +++ b/app/controllers/stages_controller.rb
  @@ -1,7 +1,8 @@
   class StagesController < ApplicationController
   
     before_filter :load_project
  -  
  +       skip_before_filter :login_from_cookie, :only => :capfile 
  +       skip_before_filter :login_required, :only => :capfile 
     # GET /projects/1/stages.xml
     def index
       @stages = current_project.stages
  </code>
- configure your http server to proxy requests for server.py - nginx example is attached
- launch server.py with 
<code> 
python server.py 
</code>
it will listen on port that is defined on the end of this file
- you should now have http://yourcapify-host.com/ configured in such way it will return python script that will execute on the client side and gather the data, and then back request for capifile on the serverside
- http://yourcapify-host.com/api/ is used for requests to specific capfiles of the projecs
