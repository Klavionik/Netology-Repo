from setuptools import setup, find_packages

setup(
    name='vkinder',
    version='0.8',
    author='Roman Vlasenko',
    author_email='klavionik@gmail.com',
    url='https://github.com/Klavionik/Netology-Repo/tree/master/projects/vkinder',
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        vkinder=vkinder.scripts.cli:cli
    '''
)
