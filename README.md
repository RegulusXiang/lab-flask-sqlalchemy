# lab-flask-sqlalchemy

<!-- [![Build Status](https://travis-ci.org/rofrano/lab-flask-tdd.svg?branch=master)](https://travis-ci.org/rofrano/lab-flask-tdd)
[![Codecov](https://img.shields.io/codecov/c/github/rofrano/lab-flask-tdd.svg)]() -->

NYU DevOps lab on using SQLAlchemy with Flask

## Introduction

This lab shows how to use SQLAlchemy with Flask so that you don't need to worry about making raw database queries. SQLAlchemy is an Object Relational Mapper (ORM) that will allow you to work with classes instead of database records. This example extends our Pet Store to use a relational database for it's persistence.

This lab also demonstrates how to create a simple RESTful service using Python Flask and SQLite.
The resource model is persistences using SQLAlchemy to keep the application simple. It's purpose is to show the correct API and return codes that should be used for a REST API.

**Note:** All of the code is in one file `server.py` to make it easier to teach. In a "real" application you would separate out the code into several modules.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/nyu-devops/lab-flask-sqlalchemy.git
    cd lab-flask-sqlalchemy
    vagrant up
    vagrant ssh
    cd /vagrant

You can now run `nosetests` to run the tests.

## Manually running the Tests

Run the tests using `nose`

    $ nosetests

**Nose** is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

Run Code Coverage to see how well your test cases exercise your code:

    $ coverage run test_server.py
    $ coverage report -m --include=server.py

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases.

You can even run `nosetests` with `coverage`

    $ nosetests --with-coverage --cover-package=server

Try and get as close to 100% coverage as you can.

When you are done, you can exit and shut down the vm with:

    $ exit
    $ vagrant halt

If the VM is no longer needed you can remove it with:

    $ vagrant destroy


## What's featured in the project?

    * server.py -- the main Service using Python Flask
    * test_server.py -- test cases using unittest
    * test_pets.py -- test cases using just the Pet model

This repo is part of the DevOps course CSCI-GA.3033-013/014 at NYU.
