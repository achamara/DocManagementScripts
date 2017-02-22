from setuptools import setup

setup(name='DocManagementScripts',
      version='0.2',
      description='Combination of scripts to manage documentary content.',
      url='https://github.com/compilable/',
      author='achamara',
      author_email='achamara@gmail.com',
      license='MIT',
      packages=['docDuplicateManager'],
      scripts=['bin/findDuplicates'],
      install_requires=[
          'TinyDB'   ],
      include_package_data=True,
      zip_safe=False)


'''

http://python-packaging.readthedocs.io/en/latest/non-code-files.html

To Install :

Run below command from DocManagementScripts folder

sudo pip install -e .   

To Execute : 

findDuplicates config.ini

'''