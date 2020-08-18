import setuptools

with open('README.md', 'r') as f:
    readme_text = f.read()

setuptools.setup(
    name='gw2build',
    version='0.dev',
    author='Joseph Lansdowne',
    author_email='ikn@ikn.org.uk',
    description='Python library for working with Guild Wars 2 builds',
    long_description=readme_text,
    long_description_content_type='text/markdown',
    url='http://ikn.org.uk/gw2build',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ]
)
