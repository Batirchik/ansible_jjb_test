""" Common way to manage jenkins job. """

import argparse
import anymarkup
import configparser
import jenkins
import logging
import os

import subprocess

logger = logging.getLogger(__file__)

class Jenkins(object):
    """ Jenkins job manager """
    def __init__(self, jenkins_info_file, action, job_name, config_path):
        self.jenkins_info_file = jenkins_info_file
        j_config = self.setup_config_settings(self.jenkins_info_file)

        self.server = jenkins.Jenkins(j_config['jenkins']['url'],
                                      j_config['jenkins']['user'],
                                      j_config['jenkins']['password'])
        self.action = action
        self.job_name = job_name
        self.config_path = config_path

    @staticmethod
    def setup_config_settings(conf_path):
        """ Gets jenkins configs"""
        config = configparser.ConfigParser()
        if os.path.isfile(conf_path):
            logger.debug("Reading config from %s", conf_path)
            config.read(conf_path)
        else:
            raise RuntimeError("Jenkins configuration file is not found.")
        return config

    def get_j_config(self):
        """ Retrieve a job config from Jenkins. """
        logger.info("Getting %s job config", self.job_name)
        job_config = self.server.get_job_config(self.job_name)
        # Convert to YAML
        job_config_yaml = anymarkup.serialize(anymarkup.parse(job_config), 'yaml')

        with open(self.config_path, 'w') as f:
            f.write(job_config_yaml)

        logger.info(" %s job config has been saved to %s", self.job_name, self.config_path)

    def update_job(self):
        """ Update jenkins job using jenkins-job-builder cmd tool """
        cmd = "jenkins-jobs --conf {0} -l DEBUG update {1} {2}".format(self.jenkins_info_file,
                                                                       self.config_path,
                                                                       self.job_name)
        logger.info("Running %s", cmd)
        subprocess.Popen(cmd, executable='/bin/bash', stdout=subprocess.PIPE, shell=True).stdout.read().rstrip()

    def run(self):
        """ Performs preparations and deployment. """
        logger.info("Performing %s action with %s job", self.action, self.job_name)

        if self.action == "get":
            self.get_j_config()
        elif self.action == "update":
            self.update_job()
        else:
            RuntimeError("Unsupported action `%s`", self.action)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--jenkins-info-path", required=True, help="Path to Jenkins creds file.")
    parser.add_argument("-n", "--job-name", required=True, help="Job name.")
    parser.add_argument("-c", "--config-path", required=True, help="Path to ssh key.")
    parser.add_argument("-a", "--action", choices=['get', 'update', 'start'], required=True, help="Action.")

    args = parser.parse_args()

    jenkins = Jenkins(args.jenkins_info_path, args.action, args.job_name, args.config_path)
    jenkins.run()
