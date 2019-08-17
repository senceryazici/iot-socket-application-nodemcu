from distutils.core import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(name='IoTSocketServer',
      version='1.0',
      description='A simple package for basic IoT Applications, with both microcontroller and host side.',
      author='Sencer Yazici',
      license="MIT",
      long_description=long_description,
      author_email='senceryazici@gmail.com',
      packages=['IoTSocketServer'],
      install_requires=['pyyaml']
      )
