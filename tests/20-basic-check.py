#!/usr/bin/env python3
# pylint: disable=c0111,c0103
import os
import re
import unittest

import yaml
import requests
from amulet import Deployment

SECONDS_TO_WAIT = 300


def find_bundle(name='bundle.yaml'):
    '''Locate the bundle to load for this test.'''
    # Check the environment variables for BUNDLE.
    bundle_path = os.getenv('BUNDLE_PATH')
    if not bundle_path:
        # Construct bundle path from the location of this file.
        bundle_path = os.path.join(os.path.dirname(__file__), '..', name)
    return bundle_path


class TestBundle(unittest.TestCase):
    bundle_file = find_bundle()

    @classmethod
    def setUpClass(cls):
        cls.deployment = Deployment(series='xenial')
        with open(cls.bundle_file) as stream:
            bundle_yaml = stream.read()
        bundle = yaml.safe_load(bundle_yaml)
        cls.deployment.load(bundle)
        # Allow some time for Juju to provision and deploy the bundle.
        cls.deployment.setup(timeout=SECONDS_TO_WAIT)
        # Wait for the system to settle down.
        application_messages = {
            'docker': re.compile(r'Ready'),
            'limeds': re.compile(r'Ready'),
        }
        cls.deployment.sentry.wait_for_messages(application_messages,
                                                timeout=600)
        cls.docker = cls.deployment.sentry['docker']
        cls.limeds = cls.deployment.sentry['limeds']

    def test_editor(self):
        self.deployment.expose('docker')
        url = self.get_url("/editor")
        teststring = "LimeDS Editor"
        response = requests.get(url)
        self.assertTrue(
            response.status_code == 200,
            "unable to access LimeDS editor")
        self.assertTrue(
            teststring in response.text,
            "LimeDS editor response not recognized: {}".format(response.text)
            )

    def test_API(self):
        self.deployment.expose('docker')
        url = self.get_url("/_limeds/config")
        teststring = "limeds"
        response = requests.get(url)
        self.assertTrue(
            response.status_code == 200,
            "unable to access LimeDS API")
        self.assertTrue(
            teststring in response.text,
            "LimeDS api response not recognized: {}".format(response.text))

    def get_url(self, path):
        """ Return complete url including port to path"""
        base_url = "http://{}:{}".format(
            self.docker[0].info['public-address'],
            self.docker[0].info['open-ports'][0].split('/')[0])
        return base_url + path


if __name__ == '__main__':
    unittest.main()
