import setuptools

with open('README.md', 'r') as f:
    readme_text = f.read()

setuptools.setup(
    name='gw2buildutil',
    version='0.4',
    author='Joseph Lansdowne',
    author_email='ikn@ikn.org.uk',
    description='Python library for working with Guild Wars 2 builds',
    long_description=readme_text,
    long_description_content_type='text/markdown',
    url='http://ikn.org.uk/lib/gw2buildutil',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ]
)
