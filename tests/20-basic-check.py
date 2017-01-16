#!/usr/bin/env python3
#pylint: disable=c0111,c0103
import re
import unittest

import requests
import amulet

SECONDS_TO_WAIT = 300

class TestBundle(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.deployment = amulet.Deployment()

        # Editors Note:  Instead of declaring the bundle in the amulet
        # setup stanza, rely on bundletester to deploy the bundle on
        # this tests behalf.  When coupled with reset:false in
        # tests.yaml this yields faster test runs per bundle.

        # Allow some time for Juju to provision and deploy the bundle.
        cls.deployment.setup(timeout=SECONDS_TO_WAIT)

        # Wait for the system to settle down.
        application_messages = {
            'docker': re.compile('Ready'),
            'limeds': re.compile('Ready'),
        }
        cls.deployment.sentry.wait_for_messages(application_messages,
                                                timeout=600)
        # Make every unit available through self reference
        # eg: for worker in self.workers:
        #         print(worker.info['public-address'])
        # cls.docker = cls.deployment.sentry['docker'][0]
        # cls.limeds = cls.deployment.sentry['limeds'][0]
        cls.docker = cls.deployment.sentry['docker']
        cls.limeds = cls.deployment.sentry['limeds']
        print("docker: {}".format(cls.docker))
        for unit in cls.docker:
            print(unit.info['public-address'])
        print("limeds: {}".format(cls.limeds))
        for unit in cls.limeds:
            print(unit.info['public-address'])
        exit()

    def test_editor(self):
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
        base_url = "{}:{}".format(
            self.docker[0].info['public-address'],
            self.docker[0].info['open-ports'][0].split('/')[0])
        return base_url + path





if __name__ == '__main__':
    unittest.main()
