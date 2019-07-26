# Catalog

## Description
Catalog project for the nano degree, it's about implementing CRUD operations and API using Flask and SqlAlchemy.

## Prerequisites
- Python 2
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Installing
To create an environment to run the project, install Vagrant and Virtual Box.

Start the Virtual Machine(VM) by running `vagrant up` in the directory that contains the "Vagrantfile" and then SSH into the VM using `vagrant ssh`. The first time `vagrant up` is run the VM will be configured based on information in the "Vagrantfile". Navigate to `/vagrant/<project_directory>` to access the project's files.

Then install dependencies:

`pip install -r requirements.txt`

Note: When done with the VM, type exit and then `vagrant suspend` to pause the VM and maintain the state of the VM.

## Running the Program
To run the program, first we need to create the database and put some data on it:

run `python data_population.py`

then we can run our project:

run `python catalog_project.py` to run the project

```
