import time
import sys
import subprocess
import logging

from nlpipe import client
from nlpipe.module import get_module

from multiprocessing import Process
from configparser import SafeConfigParser
from pydoc import locate

class Worker(Process):
    """
    Base class for NLP workers.
    """

    sleep_timeout = 1

    def __init__(self, client, module):
        """
        :param client: a Client object to connect to the NLP Server
        """
        super().__init__()
        self.client = client
        self.module = module

    def run(self):
        while True:
            id, doc = self.client.get_task(self.module.name)
            if id is None:
                time.sleep(self.sleep_timeout)
                continue
            logging.info("Received task {self.module.name}/{id} ({n} bytes)".format(n=len(doc), **locals()))
            try:
                result = self.module.process(doc)
                self.client.store_result(self.module.name, id, result)
                logging.debug("Succesfully completed task {self.module.name}/{id} ({n} bytes)"
                              .format(n=len(result), **locals()))
            except Exception as e:
                logging.exception("Exception on parsing {self.module.name}/{id}"
                              .format(**locals()))
                try:
                    self.client.store_error(self.module.name, id, str(e))
                except:
                    logging.exception("Exception on storing error for {self.module.name}/{id}"
                                      .format(**locals()))


def _import(name):
    result = locate(name)
    if result is None:
        raise ValueError("Cannot import {name!r}".format(**locals()))
    return result
    
def run_workers(client, modules):
    """
    Run the given workers as separate processes
    :param modules: names of the modules (module name or fully qualified class name)
    """
    # import built-in workers
    import nlpipe.modules
    # create and start workers
    for module_class in modules:
        if "." in module_class:
            module = _import(module_class)()
        else:
            module = get_module(module_class)
        logging.debug("Starting worker {module}".format(**locals()))
        Worker(client=client, module=module).start()

    logging.info("Workers active and waiting for input")
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("server", help="Server hostname or directory location")
    parser.add_argument("modules", nargs="+", help="Class names of module(s) to run")
    parser.add_argument("--verbose", "-v", help="Verbose (debug) output", action="store_true", default=False)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
    
    client = client._get_client(args.server)
    run_workers(client, args.modules)
