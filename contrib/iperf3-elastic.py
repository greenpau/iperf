#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Author: Paul Greenberg @greenpau
#

from __future__ import (absolute_import, division, print_function);
__metaclass__ = type

import os;
import sys;
import argparse;
from collections import OrderedDict;
import traceback;
import json;
import pprint;

toolname = str(os.path.basename(__file__)).replace('.pyc', '').replace('.py', '');

import logging;
logging.basicConfig(stream=sys.stdout, format='%(asctime)s ' + toolname + ' [%(levelname)s] %(message)s');
logger = logging.getLogger(__file__);
logger.setLevel(logging.DEBUG);


class iPerfReport(object):

    def __init__(self, **kwargs):
        self.errors = [];
        self.summary = {};
        self.input_file = None;
        for key, value in kwargs.iteritems():
            if key == 'input_file':
                self.input_path = os.path.expanduser(value);
                self.input_file = os.path.basename(self.input_path);
                self.input_dir = self.input_path.replace(self.input_file, '');
                if not os.path.exists(self.input_path):
                    self.errors.append('file \'' + self.input_path + '\' does not exist');
                    return;
                if not os.path.isfile(self.input_path):
                    self.errors.append('file \'' + self.input_path + '\' is not a file');
                    return;
                try:
                    with open(self.input_path) as json_data:
                        self.data = json.load(json_data);
                    if not isinstance(self.data, dict):
                        self.errors.append('file \'' + self.input_path + '\' does not contain JSON dictionary');
                        return;
                    for i in ['start', 'intervals', 'end']:
                        if i not in self.data:
                            self.errors.append('file \'' + self.input_path + '\' does not contain \'' + i + '\' field');
                            return;
                    if 'cookie' not in self.data['start']:
                        self.errors.append('file \'' + self.input_path + '\' does not contain \'cookie\' field');
                        return;
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info();
                    self.errors.extend(traceback.format_exception(exc_type, exc_value, exc_traceback));
                logger.debug('Input File: ' + self.input_file);
                #pprint.pprint(self.data);
                self._parse();


    def _parse(self):
        self.cookie = self.data['start']['cookie'];
        self.summary['cookie'] = self._to_dict(self.cookie);
        logger.debug('Report ID: ' + self.cookie);
        if 'connected' in self.data['start']:
            c = self.data['start']['connected'][0];
            for i in ['local_host', 'local_port', 'remote_host', 'remote_port', 'socket']:
                if i in c:
                    ic = i;
                    if i == 'socket':
                        ic = 'ip_version';
                    if i in ['local_port', 'remote_port', 'socket']:
                        self.summary[ic] = self._to_dict(c[i], 'integer', 'analyzed', True);
                    if i in ['local_host', 'remote_host']:
                        self.summary[ic] = self._to_dict(c[i], 'ip', 'analyzed', True);
        if 'connecting_to' in self.data['start']:
            if 'host' in self.data['start']['connecting_to']:
                self.summary['host'] = self._to_dict(self.data['start']['connecting_to']['host']);
            if 'port' in self.data['start']['connecting_to']:
                self.summary['port'] = self._to_dict(self.data['start']['connecting_to']['port'], 'integer', 'analyzed', True);
            pass;
        for i in ['version', 'system_info']:
            if i in self.data['start']:
                self.summary['version'] = self._to_dict(self.data['start'][i]);
        pprint.pprint(self.summary);
        return;

    @staticmethod
    def _to_dict(value, value_type='string', index='analyzed', doc_values=None):
        r = {};
        r['value'] = str(value).strip();
        r['index'] = index;
        r['type'] = value_type;
        if doc_values:
            r['doc_values'] = doc_values;
        return r;

    def print_errors(self):
        for i in self.errors:
            for j in i.split('\n'):
                logger.error(j);
        return;


def main():
    global logger;
    """ Main function """
    descr = toolname + ' - iperf JSON client report parser for Elasticsearch\n\n';
    epil = '\ncontacts: Paul Greenberg @greenpau\n\n';
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, \
                                     description=descr, epilog=epil);
    main_group = parser.add_argument_group('arguments');
    main_group.add_argument('--input', dest='input_file', metavar='FILE', required=True, \
                            type=str, help='iPerf JSON client report file');
    logging_group = parser.add_argument_group('Logging and Debugging')
    logging_group.add_argument('-l', '--log-level', dest='ilog', metavar='LEVEL', type=int, default=0, \
                            choices=range(1, 3), help='Log level (default: 0, max: 2)');

    args = parser.parse_args();
    if args.ilog == 1:
        logger.setLevel(logging.INFO);
    elif args.ilog == 2:
        logger.setLevel(logging.DEBUG);
    else:
        logger.setLevel(logging.WARNING);
    kwargs = OrderedDict({
        'input_file': args.input_file,
    });
    r = iPerfReport(**kwargs);
    if r.errors:
        r.print_errors();
        sys.exit(1);


if __name__ == '__main__':
    main();
