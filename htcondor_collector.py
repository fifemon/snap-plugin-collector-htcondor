#!/usr/bin/env python
#
# Copyright 2016 Kevin Retzke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import string
import time
import copy

import snap_plugin.v1 as snap
import htcondor


logger = logging.getLogger(__name__)


class HTCondor(snap.Collector):
    def __init__(self, name, version, **kwargs):
        #logger.addHandler(logging.FileHandler(filename='/tmp/htcondor.log'))
        #logger.setLevel(logging.DEBUG)

        super(HTCondor, self).__init__(name, version, **kwargs)

    def get_config_policy(self):
        return snap.ConfigPolicy(
            [
                ('fifemon','htcondor'),
                [
                    ('pool', snap.StringRule(default='localhost')),
                    ('retry_delay', snap.IntegerRule(default=5)),
                    ('max_retries', snap.IntegerRule(default=1)),
                ]
            ]
        )

    def update_catalog(self, config):
        metrics = []
        for daemon_type in htcondor_daemons.keys():
            metrics.append(snap.Metric(
                namespace=['fifemon','htcondor',daemon_type,
                    snap.NamespaceElement(name='daemon',description='daemon name'),
                    snap.NamespaceElement(name='classad',description='daemon classad statistics'),
                    'value',
                ],
                version=1,
                tags={},
                description='classad statistics for HTCondor {0}'.format(daemon_type),
            ))
        return metrics

    def collect(self, metrics):
        config = metrics[0].config # TODO process config from all metrics?
        daemon_types_to_query = set([m.namespace[2].value for m in metrics])

        logger.info('collecting metrics from htcondor pool {}'.format(config['pool']))
        ads = get_classads(pool=str(config['pool']), 
            daemon_types = daemon_types_to_query, 
            retry_delay = config['retry_delay'],
            max_retries = config['max_retries'])

        timestamp = time.time()
        rmetrics=[]
        # TODO: cleanup loops
        for metric in metrics:
            dt = metric.namespace[2].value
            for d in ads[dt]:
                if metric.namespace[3].value not in ['*', d['Name']]:
                    continue
                for k in d:
                    if metric.namespace[4].value not in ['*', k]:
                        continue
                    m = snap.Metric(
                            namespace=['fifemon','htcondor',dt,d['Name'],k,'value'],
                            version=metric.version,
                            tags=dict(metric.tags),
                            config=metric.config,
                            timestamp=timestamp,
                            unit=metric.unit,
                            description=metric.description,
                            data = d[k])
                    # TODO: why doesn't this work instead?
                    #m = copy.deepcopy(metric)
                    #m.namespace[3].value = d['Name']
                    #m.namespace[4].value = k
                    #m.data = d[k]
                    #m.timestamp = timestamp
                    rmetrics.append(m)
        return rmetrics

htcondor_daemons = {
    'schedds': htcondor.DaemonTypes.Schedd,
    'collectors': htcondor.DaemonTypes.Collector,
    'negotiators': htcondor.DaemonTypes.Negotiator,
    'startds': htcondor.DaemonTypes.Startd,
    'masters': htcondor.DaemonTypes.Master,
    'hads': htcondor.DaemonTypes.HAD,
}


def get_classads(pool='localhost', daemon_types=htcondor_daemons.keys(), retry_delay=10, max_retries=10):
    c = htcondor.Collector(pool)
    ads = {}
    for daemon_type in daemon_types:
        logger.info('collecting stats for {} daemons'.format(daemon_type))
        retries = 0
        while retries < max_retries:
            try:
                ads[daemon_type] = c.locateAll(htcondor_daemons[daemon_type])
            except:
                logger.warning('trouble getting pool {0} {1} status, retrying in {2}s.'.format(pool,daemon_type,retry_delay))
                ads[daemon_type] = None
                retries += 1
                time.sleep(retry_delay)
            else:
                break
        if ads[daemon_type] is None:
            logger.error('trouble getting pool {0} {1} status, giving up.'.format(pool,daemon_type))
    logger.info('done collecting metrics from pool {}'.format(pool))
    return ads


if __name__ == '__main__':
    HTCondor("htcondor", 1).start_plugin()
