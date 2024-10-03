from setuptools import setup, find_packages

setup(
    name='knpy',        # Package name
    version='0.1',            # Version number
    packages=find_packages(), # Automatically find packages
    install_requires=[],      # External dependencies (if any)
    description='Package designed for machine learning in knot theory.',
    long_description=open('README.md').read(),  # Detailed description from README
    long_description_content_type='text/markdown',
    url='https://github.com/dcs321/knpy.git',  # Your GitHub repository
    author='Csaba Dékány',
    author_email='dekanycsaba23@gmail.com',
    license='MIT',            # License type
)