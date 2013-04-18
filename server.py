from bottle import static_file,route, run, template, request
import MySQLdb
import re
import os
import sys
import commands
import time
import ConfigParser, os
import urllib2
import base64
import requests
from requests.auth import HTTPBasicAuth

config = ConfigParser.ConfigParser()
config.read('global.cfg')
host=config.get('global','host')
user=config.get('global','user')
password=config.get('global','password')
pidfile_path=config.get('global','pidfile_path')
static_root=config.get('global','static_root')
webistrano_fqdn=config.get('global','webistrano_fqdn')
capfile_http_login=config.get('global','capfile_http_login')
capfile_http_password=config.get('global','capfile_http_password')
capify_api_url=config.get('global','capify_api_url')

pid = os.getpid()
print "PID: "+str(pid)
pidfile = open(pidfile_path,'w')
pidfile.write(str(pid))
pidfile.close()

conn = MySQLdb.connect(host=host, user=user, passwd=password, db="webistrano")

c = conn.cursor()
c.execute("show tables")
tables= c.fetchall()
print "Hi - I'm your webistrano"
print tables


@route('/')
def server_static():
				#return template('static/capify.tpl',capify_api_url=capify_api_url)
				return static_file('capify.py', root=static_root)


@route('/api/',method='POST') 
def serve_content():
				file_type=request.forms.get('req_type')
				stage_name=request.forms.get('stage_name')
				project_name=request.forms.get('project_name')
				print "----------Whoa - requested %s/%s/%s" % (project_name, stage_name, file_type)
				if file_type=='capfile':
								project_id_sql="select project_id  from configuration_parameters where value like '%s' and project_id is not NULL;" % ('%'+project_name)
							 	project = c.execute(project_id_sql)
								project_id = int(c.fetchone()[0])

								stage_id_sql ="select stage_id from configuration_parameters where stage_id IN ( SELECT id from stages where project_id='%s' ) and name='branch' and value='%s'" % (project_id, stage_name)
								stage = c.execute(stage_id_sql)
								stage_id = int(c.fetchone()[0])
								
								capfile_resource = "http://%s/projects/%s/stages/%s/capfile" % (webistrano_fqdn, project_id, stage_id)
								capfile_request = requests.get(capfile_resource, auth=HTTPBasicAuth(capfile_http_login, capfile_http_password))
								capfile_content = capfile_request.text
								capfile_appendix = '\r\n\
desc "tail log files" \r\n\
task :tail, :roles => :app do\r\n\
run "tail -f #{shared_path}/log/#{rails_env}.log" do |channel, stream, data| \r\n\
puts "#{channel[:host]}: #{data}" \r\n\
break if stream == :err \r\n\
end \r\n\
end'

				return (capfile_content + capfile_appendix)
run(host='localhost', port=8462)
