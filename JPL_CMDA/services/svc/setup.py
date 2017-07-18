from setuptools import setup, find_packages

setup(
    name='svc',
    version='1.0',
    long_description='CMAC web services',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'gunicorn', 'tornado',
                      'httplib2', 'lxml']
)
