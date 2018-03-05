from setuptools import setup

# run command for installing development packages: pip install -e .[dev]
requirements = ['gevent==1.2.2', 'Flask_Migrate==2.0.2', 'Flask_SocketIO==2.9.3',
                'Flask==0.12', 'Flask_Bcrypt==0.7.1', 'Flask_Cors==3.0.3',
                'Flask_SQLAlchemy==2.1', 'Flask_Script==2.0.5', 'requests==2.18.4',
                'PyJWT==1.6.0', 'paho_mqtt==1.3.1', 'socketIO_client==0.7.2', 'psycopg2==2.7.4']
dev_requirements = ['httpretty==0.8.14']

setup(
    name='LanGateway',
    version='0.1',
    packages=['', 'core', 'test'],
    package_dir={'': 'src'},
    url='',
    license='',
    author='CEIT IOT Lab',
    author_email='',
    description='',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    }
)
