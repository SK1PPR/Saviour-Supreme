from setuptools import setup

setup(
   name='Saviour-Supreme',
   version='1.0',
   description='A file sharing server for the IITR Junta',
   author='Khushal Agrawal',
   author_email='agrawalkhushal04@gmail.com',
   packages=['SAVIOUR-SUPREME'], 
   install_requires=['PySimpleGUI', 'tqdm', 'pycryptodome', 'ratelimit'], #external packages as dependencies
   scripts=[
            'gui_application.py',
           ]
)