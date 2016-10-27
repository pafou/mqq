Stack Exchange Inbox Reputation and Badges sign up log in tour help  

Search Q&A

Stack Overflow
Questions
 
Jobs
 
Documentation 
 
Tags
 
Users
 
Badges
 
Ask Question
x Dismiss
Join the Stack Overflow Community
Stack Overflow is a community of 6.3 million programmers, just like you, helping each other. 
Join them; it only takes a minute: 
Sign up
Deploying a local django app using openshift

up vote
16
down vote
favorite
23
I've built a webapp using django. In order to host it I'm trying to use openshift but am having difficulty in getting anything working. There seems to be a lack of step by steps for this. So far I have git working fine, the app works on the local dev environment and I've successfully created an app on openshift.

Following the URL on openshift once created I just get the standard page of "Welcome to your Openshift App".

I've followed this https://developers.openshift.com/en/python-getting-started.html#step1 to try changing the wsgi.py file. Changed it to hello world, pushed it and yet I still get the openshift default page.

Is there a good comprehensive resource anywhere for getting local Django apps up and running on Openshift? Most of what I can find on google are just example apps which aren't that useful as I already have mine built.

python django git openshift
shareimprove this question
asked Nov 11 '14 at 18:01

Oliver Burdekin
482624
  	 	
Well I have also tried once and deployed once a django app on openshift. I have all commands that i used step by step if you want i can share the commands in answer ? – Tanveer Alam Nov 11 '14 at 18:14
  	 	
Deploying a Django instance is a pain in the ass, since the versions are different. I will put a sample code I use to do. – Luis Masuelli Nov 11 '14 at 20:39
1	 	
See answer and enjoy :D – Luis Masuelli Nov 11 '14 at 20:54
add a comment
4 Answers
active oldest votes
up vote
34
down vote
accepted
Edit: Remember this is a platform-dependent answer and since the OpenShift platform serving Django may change, this answer could become invalid. As of Apr 1 2016, this answer remains valid at its whole extent.

Many times this happened to me and, since I had to mount at least 5 applications, I had to create my own lifecycle:

Don't use the Django cartridge, but the python 2.7 cartridge. Using the Django cart. and trying to update the django version brings many headaches, not included if you do it from scratch.
Clone your repository via git. You will get yourproject and...
# git clone yourrepo@rhcloud.com:app.git yourproject <- replace it with your actual openshift repo address

yourproject/
+---wsgi.py
+---setup.py
*---.openshift/ (with its contents - I omit them now)
Make a virtualenv for your brand-new repository cloned into your local machine. Activate it and install Django via pip and all the dependencies you would need (e.g. a new Pillow package, MySQL database package, ...). Create a django project there. Say, yourdjproject. Edit Create, alongside, a wsgi/static directory with an empty, dummy, file (e.g. .gitkeep - the name is just convention: you can use any name you want).
 #assuming you have virtualenv-wrapper installed and set-up
 mkvirtualenv myenvironment
 workon myenvironment
 pip install Django[==x.y[.z]] #select your version; optional.
 #creating the project inside the git repository
 cd path/to/yourproject/
 django-admin.py startproject yourjdproject .
 #creating dummy wsgi/static directory for collectstatic
 mkdir -p wsgi/static
 touch wsgi/static/.gitkeep
Create a django app there. Say, yourapp. Include it in your project.
You will have something like this (django 1.7):
yourproject/
+---wsgi/
|   +---static/
|       +---.gitkeep
+---wsgi.py
+---setup.py
+---.openshift/ (with its contents - I omit them now)
+---yourdjproject/
|   +----__init__.py
|   +----urls.py
|   +----settings.py
|   +----wsgi.py
+---+yourapp/
    +----__init__.py
    +----models.py
    +----views.py
    +----tests.py
    +----migrations
         +---__init__.py
Set up your django application as you'd always do (I will not detail it here). Remember to include all the dependencies you installed, in the setup.py file accordingly (This answer is not the place to describe WHY, but the setup.py is the package installer and openshift uses it to reinstall your app on each deploy, so keep it up to date with the dependencies).
Create your migrations for your models.
Edit the openshift-given WSGI script as follows. You will be including the django WSGI application AFTER including the virtualenv (openshift creates one for python cartridges), so the pythonpath will be properly set up.
#!/usr/bin/python
import os
virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

from yourdjproject.wsgi import application
Edit the hooks in .openshift/action_hooks to automatically perform db sincronization and media management:

build hook

#!/bin/bash
#this is .openshift/action/hooks/build
#remember to make it +x so openshift can run it.
if [ ! -d ${OPENSHIFT_DATA_DIR}media ]; then
    mkdir -p ${OPENSHIFT_DATA_DIR}media
fi
ln -snf ${OPENSHIFT_DATA_DIR}media $OPENSHIFT_REPO_DIR/wsgi/static/media

######################### end of file
deploy hook
#!/bin/bash
#this one is the deploy hook .openshift/action_hooks/deploy
source $OPENSHIFT_HOMEDIR/python/virtenv/bin/activate
cd $OPENSHIFT_REPO_DIR
echo "Executing 'python manage.py migrate'"
python manage.py migrate
echo "Executing 'python manage.py collectstatic --noinput'"
python manage.py collectstatic --noinput

########################### end of file
Now you have the wsgi ready, pointing to the django wsgi by import, and you have your scripts running. It is time to consider the locations for static and media files we used in such scripts. Edit your Django settings to tell where did you want such files:
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'wsgi', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'wsgi', 'static', 'media')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'yourjdproject', 'static'),)
TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'yourjdproject', 'templates'),)
Create a sample view, a sample model, a sample migration, and PUSH everything.
Edit Remember to put the right settings to consider both environments so you can test and run in a local environment AND in openshift (usually, this would involve having a local_settings.py, optionally imported if the file exists, but I will omit that part and put everything in the same file). Please read this file conciously since things like yourlocaldbname are values you MUST set accordingly:
"""
Django settings for yourdjproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ON_OPENSHIFT = False
if 'OPENSHIFT_REPO_DIR' in os.environ:
    ON_OPENSHIFT = True


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '60e32dn-za#y=x!551tditnset(o9b@2bkh1)b$hn&0$ec5-j7'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yourapp',
    #more apps here
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'yourdjproject.urls'

WSGI_APPLICATION = 'yourdjproject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

if ON_OPENSHIFT:
    DEBUG = True
    TEMPLATE_DEBUG = False
    ALLOWED_HOSTS = ['*']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'youropenshiftgenerateddatabasename',
            'USER': os.getenv('OPENSHIFT_MYSQL_DB_USERNAME'),
            'PASSWORD': os.getenv('OPENSHIFT_MYSQL_DB_PASSWORD'),
            'HOST': os.getenv('OPENSHIFT_MYSQL_DB_HOST'),
            'PORT': os.getenv('OPENSHIFT_MYSQL_DB_PORT'),
            }
    }
else:
    DEBUG = True
    TEMPLATE_DEBUG = True
    ALLOWED_HOSTS = []
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', #If you want to use MySQL
            'NAME': 'yourlocaldbname',
            'USER': 'yourlocalusername',
            'PASSWORD': 'yourlocaluserpassword',
            'HOST': 'yourlocaldbhost',
            'PORT': '3306', #this will be the case for MySQL
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'yr-LC'
TIME_ZONE = 'Your/Timezone/Here'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'wsgi', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'wsgi', 'static', 'media')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'yourdjproject', 'static'),)
TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'yourdjproject', 'templates'),)
Git add, commit, push, enjoy.
cd path/to/yourproject/
git add .
git commit -m "Your Message"
git push origin master # THIS COMMAND WILL TAKE LONG
# git enjoy
Your sample Django app is almost ready to go! But if your application has external dependencies it will blow with no apparent reason. This is the reason I told you to develop a simple application. Now it is time to make your dependencies work.

[untested!] You can edit the deploy hook and add a command after the command cd $OPENSHIFT_REPO_DIR, like this: pip install -r requirements.txt, assuming the requirements.txt file exists in your project. pip should exist in your virtualenv, but if it does not, you can see the next solution.

Alternatively, the setup.py is an already-provided approach on OpenShift. What I did many times is -assuming the requirements.txt file exists- is:

Open that file, read all its lines.
For each line, if it has a #, remove the # and everything after.
strip leading and trailing whitespaces.
Discard empty lines, and have the result (i.e. remaining lines) as an array.
That result must be assigned to the install_requires= keyword argument in the setup call in the setup.py file.
I'm sorry I did not include this in the tutorial before! But you need to actually install Django in the server. Perhaps an obvious suggestion, and every Python developer could know that beforehand. But seizing this opportunity I remark: Include the appropriate Django dependency in the requirements.txt (or setup.py depending on whetheryou use or not a requirements.txt file), as you include any other dependency.
This should help you to mount a Django application, and took me a lot of time to standarize the process. Enjoy it and don't hesitate on contacting me via comment if something goes wrong

Edit (for those with the same problem who don't expect to find the answer in this post's comments): Remember that if you edit the build or deploy hook files under Windows and you push the files, they will fly to the server with 0644 permissions, since Windows does not support this permission scheme Unix has, and has no way to assign permissions since these files do not have any extension. You will notice this because your scripts will not be executed when deploying. So try to deploy those files only from Unix-based systems.

Edit 2: You can use git hooks (e.g. pre_commit) to set permissions for certain files, like pipeline scripts (build, deploy, ...). See the comments by @StijndeWitt and @OliverBurdekin in this answer, and also this question for more details.

shareimprove this answer
edited Jul 25 at 17:50
answered Nov 11 '14 at 20:54

Luis Masuelli
5,93632047
1	 	
Yes. Windows does not have a permission system, so when you push, files go with 644 as permission. So they don't have an execute flag and arent thus executed. Besides, "build" and "deploy" have no extension so they could never be hinted about having such flag or not. You have to manually change the flags after you push. – Luis Masuelli Nov 24 '14 at 14:57
1	 	
point 2. is still unclear. Please explain how to do it and where. (from the answer below, I think you mean rhc git-clone mysite) – Mauro BBianc-Pynchia Sep 8 '15 at 12:05 
1	 	
the more I read points 2 and 3 the less I understand. You clone your project (existing and working django project) and then in step 3 you create another django project from scratch? – Mauro BBianc-Pynchia Sep 8 '15 at 12:09 
1	 	
On the point of windows and permissions, I've discovered that you can set the action_hooks to run everytime you push. After git add --all changed permissions for action_hooks will be returned to 644. However, if you add a git hook in .git/hooks/pre-commit you can automate changing them to executable. For example in the .git/hooks/pre-commit this will update build permissions before pushing: #!/bin/sh git update-index --chmod=+x .openshift/action_hooks/build A windows specific problem but took me a while to work out. – Oliver Burdekin Sep 8 '15 at 13:39
1	 	
point 9. python manage.py migrate will not work in build action hook for Postgres or MySQL databases, because DB is taken down during build and deploy. It should be rather placed in post_deploy hook – Ivan Jan 4 at 9:24
show 24 more comments
up vote
6
down vote
1)  Step 1 install  Rubygems
Ubuntu - https://rubygems.org/pages/download
Windows - https://forwardhq.com/support/installing-ruby-windows
$ gem
or
C:\Windows\System32>gem
RubyGems is a sophisticated package manager for Ruby.  This is a
basic help message containing pointers to more information……..

2)  Step 2:
$ gem install rhc
Or
C:\Windows\System32> gem install rhc

3)  $ rhc
Or
C:\Windows\System32> rhc

Usage: rhc [--help] [--version] [--debug] <command> [<args>]
Command line interface for OpenShift.

4)  $ rhc app create -a mysite -t python-2.7
Or 
C:\Windows\System32>  rhc app create -a mysite -t python-2.7
# Here mysite would be the sitename of your choice
#It will ask you to enter your openshift account id and password

Login to openshift.redhat.com: Enter your openshift id here
Password : **********


Application Options
---------------------
Domain:    mytutorials
Cartridges: python-2.7
Gear Size:  Default
Scaling:    no

......
......

Your application 'mysite' is now available.

 URL : http://mysite.....................
 SSH to :  39394949......................
 Git remote: ssh://......................

Run 'rhc show-app mysite' for more details about your app.

5)  Clone your site
$ rhc git-clone mysite
Or
D:\> rhc git-clone mysite
.......................
Your application Git repository has been cloned to "D:\mysite"

6)  #”D:\mysite>” is the location we cloned.
D:\mysite> git remote add upstream -m master git://github.com/rancavil/django-openshift-quickstart.git

D:\mysite> git pull -s recursive -X theirs upstream master

7)  D:\mysite> git push
remote : ................
remote: Django application credentials
               user: admin
               xertefkefkt

remote: Git Post-Receive Result: success
.............

8)  D:\mysite>virtualenv venv --no-site-packages
D:\mysite>venv\Scripts\activate.bat
<venv> D:\mysite> python setup.py install
creating .....
Searching for Django<=1.6
.............
Finished processing dependencies for mysite==1.0

9)  Change admin password
<venv> D:\mysite\wsgi\openshift> python manage.py changepassword admin
password:
...
Password changed successfully for user 'admin'
<venv> D:\mysite\wsgi\openshift> python manage.py runserver
Validating models….

10) Git add
<venv> D:\mysite> git add.
<venv> D:\mysite> git commit -am"activating the app on Django / Openshift"
   .......
<venv> D:\mysite> git push



#----------------------------------------------------------------------------------
#-----------Edit your setup.py in mysite with packages you want to install----------

from setuptools import setup

import os

# Put here required packages
packages = ['Django<=1.6',  'lxml', 'beautifulsoup4', 'openpyxl']

if 'REDISCLOUD_URL' in os.environ and 'REDISCLOUD_PORT' in os.environ and 'REDISCLOUD_PASSWORD' in os.environ:
     packages.append('django-redis-cache')
     packages.append('hiredis')

setup(name='mysite',
      version='1.0',
      description='OpenShift App',
      author='Tanveer Alam',
      author_email='xyz@gmail.com',
      url='https://pypi.python.org/pypi',
      install_requires=packages,
)
shareimprove this answer
answered Nov 11 '14 at 20:18

Tanveer Alam
3,4143824
  	 	
thanks tanveer. This looks good for starting an application from scratch. – Oliver Burdekin Nov 12 '14 at 17:28
1	 	
It doesn't answer the question though – Oliver Burdekin Nov 14 '14 at 13:31
add a comment
up vote
1
down vote
This is helpful for me take a look

http://what-i-learnt-today-blog.blogspot.in/2014/05/host-django-application-in-openshift-in.html

shareimprove this answer
answered Feb 21 '15 at 18:46

GrvTyagi
1,203820
add a comment
up vote
1
down vote
These are steps that works for me: I've done some steps manually, but you can automate them later to be done with each push command.

Create new django app with python-3.3 from website wizard
Add mysql cartridge to app (my option is mysql)
git clone created app to local
add requirements.txt to root folder
Add myapp to wsgi folder
Modify application to refer to myapp
execute git add, commit, push
Browse app and debug errors with "rhc tail myapp"
connect to ssh console

rhc ssh myapp
10.execute this

source $OPENSHIFT_HOMEDIR/python/virtenv/venv/bin/activate
install missing packages if any
go to app directory

cd ~/app-root/runtime/repo/wsgi/app_name
do migration with:

python manage.py migrate
create super user:

python manage.py createsuperuser
15.Restart the app

shareimprove this answer
edited Oct 24 '15 at 16:30
answered Oct 24 '15 at 10:52

Serjik
2,51142649
add a comment
Your Answer


 
Sign up or log in

Sign up using Google
Sign up using Facebook
Sign up using Email and Password
Post as a guest

Name

Email

required, but never shown
 Post Your Answer
By posting your answer, you agree to the privacy policy and terms of service.

Not the answer you're looking for?	Browse other questions tagged python django git openshift or ask your own question.

asked

1 year ago

viewed

8731 times

active

3 months ago

Want a python job?
Software Developer
PeopleDocParis, France
€40,000 - €48,000
pythondjango
Python Back-end Web Engineer - Startup en peine croissance
Meilleursagents.comParis, France
pythonpostgresql
Ingénieur DevOps (H/F)
AdaCoreParis, France
pythonunix
Python Backend Engineer
DoleadParis, France
pythonapi
Get the weekly newsletter! In it, you'll get:

The week's top questions and answers
Important community announcements
Questions that need answers
Sign up for the newsletter
see an example newsletter

Linked

81
How to create file execute mode permissions in Git on Windows?
1
Using Django on OpenShift
2
Django on Openshift - 500 Internal Server Error - error in wsgi.py
0
Export local Django website to Open Shift
-2
Deploying on Openshift
Related

3941
How to remove local (untracked) files from the current Git branch?
8726
How to delete a Git branch both locally and remotely?
4352
How to rename a local Git branch?
0
Django on Openshift, keeping config files different in different environments
1
Using Django on OpenShift
0
Installing / Creating a Django app on Openshift
1
Bootstrapping of Django 1.7 application to deploy on OpenShift
0
How do you add a third party reusable app to django and deploy in openshift?
1
deploying app on openshift - git and ssh key not working
1
Best way to deploy Django app to OpenShift without downtime?
Hot Network Questions

How bad is it if I write AJAX functions using wp-load.php?
How to explain the use of high-tech bows instead of guns
How to explain centuries of cultural/intellectual stagnation?
Should I define the relations between tables in database or just in code?
What is the rationale behind decltype behavior?
Approximation of the Gamma function for small value
Why is international first class much more expensive than international economy class?
DDoS: Why not block originating IP addresses?
Creating new renderings that are compatible with SXA
Why don't miners get boiled to death at 4km deep?
Why can't one eat prior to hearing havdala?
What is way to eat rice with hands in front of westerners such that it doesn't appear to be yucky?
Display an xkcd
Does the Iron Man movie ever establish a convincing motive for the main villain?
Why don't we see "the milky way" in both directions?
How to see the name of the command everytime I run it by a shortcut?
2N2222 experiment is indicating incorrect gains
Grandma likes coffee but not tea
知っているはずです is over complicated?
Is this aphorism involving "turco" racist?
The Rule of Thumb for Title Capitalization
Word/expression for a German "Ausflugscafé" - a cafe mainly catering to people taking a walk
In a World Where Gods Exist Why Wouldn't Every Nation Be Theocratic?
Abstract definition of convex set
question feed
about us tour help blog chat data legal privacy policy work here advertising info mobile contact us feedback
TECHNOLOGY	LIFE / ARTS	CULTURE / RECREATION	SCIENCE	OTHER
Stack Overflow
Server Fault
Super User
Web Applications
Ask Ubuntu
Webmasters
Game Development
TeX - LaTeX
Software Engineering
Unix & Linux
Ask Different (Apple)
WordPress Development
Geographic Information Systems
Electrical Engineering
Android Enthusiasts
Information Security
Database Administrators
Drupal Answers
SharePoint
User Experience
Mathematica
Salesforce
ExpressionEngine® Answers
Cryptography
Code Review
Magento
Signal Processing
Raspberry Pi
Programming Puzzles & Code Golf
more (7)
Photography
Science Fiction & Fantasy
Graphic Design
Movies & TV
Music: Practice & Theory
Seasoned Advice (cooking)
Home Improvement
Personal Finance & Money
Academia
more (8)
English Language & Usage
Skeptics
Mi Yodeya (Judaism)
Travel
Christianity
English Language Learners
Japanese Language
Arqade (gaming)
Bicycles
Role-playing Games
Anime & Manga
Motor Vehicle Maintenance & Repair
more (17)
MathOverflow
Mathematics
Cross Validated (stats)
Theoretical Computer Science
Physics
Chemistry
Biology
Computer Science
Philosophy
more (3)
Meta Stack Exchange
Stack Apps
Area 51
Stack Overflow Talent
site design / logo © 2016 Stack Exchange Inc; user contributions licensed under cc by-sa 3.0 with attribution required
rev 2016.10.27.4149




Django on OpenShift
===================

This git repository helps you get up and running quickly w/ a Django
installation on OpenShift.  The Django project name used in this repo
is 'myproject' but you can feel free to change it.  Right now the
backend is sqlite3 and the database runtime is found in
`$OPENSHIFT_DATA_DIR/db.sqlite3`.

Before you push this app for the first time, you will need to change
the [Django admin password](#admin-user-name-and-password).
Then, when you first push this
application to the cloud instance, the sqlite database is copied from
`wsgi/myproject/db.sqlite3` with your newly changed login
credentials. Other than the password change, this is the stock
database that is created when `python manage.py syncdb` is run with
only the admin app installed.

On subsequent pushes, a `python manage.py syncdb` is executed to make
sure that any models you added are created in the DB.  If you do
anything that requires an alter table, you could add the alter
statements in `GIT_ROOT/.openshift/action_hooks/alter.sql` and then use
`GIT_ROOT/.openshift/action_hooks/deploy` to execute that script (make
sure to back up your database w/ `rhc app snapshot save` first :) )

You can also turn on the DEBUG mode for Django application using the
`rhc env set DEBUG=True --app APP_NAME`. If you do this, you'll get
nicely formatted error pages in browser for HTTP 500 errors.

Do not forget to turn this environment variable off and fully restart
the application when you finish:

```
$ rhc env unset DEBUG
$ rhc app stop && rhc app start
```

Running on OpenShift
--------------------

Create an account at https://www.openshift.com

Install the RHC client tools if you have not already done so:
    
    sudo gem install rhc
    rhc setup

Select the version of python (2.7 or 3.3) and create a application

    rhc app create django python-$VERSION

Add this upstream repo

    cd django
    git remote add upstream -m master git://github.com/openshift/django-example.git
    git pull -s recursive -X theirs upstream master

Then push the repo upstream

    git push

Now, you have to create [admin account](#admin-user-name-and-password), so you 
can setup your Django instance.
	
That's it. You can now checkout your application at:

    http://django-$yournamespace.rhcloud.com

Admin user name and password
----------------------------
Use `rhc ssh` to log into python gear and run this command:

	python $OPENSHIFT_REPO_DIR/wsgi/myproject/manage.py createsuperuser

You should be now able to login at:

	http://django-$yournamespace.rhcloud.com/admin/
