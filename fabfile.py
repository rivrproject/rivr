from fabric.api import *
from rivr import VERSION

def tag():
    local('git tag -sm "rivr {0}" {0}'.format(VERSION))
    local('git push origin {}'.format(VERSION))

def upload():
    local('python setup.py sdist register upload')

def release():
    tag()
    upload()

