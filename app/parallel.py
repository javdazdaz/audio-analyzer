#!/usr/bin/env python3

import concurrent.futures
import config

# Crear un pool global de procesos con la cantidad de workers del config
process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=config.NUM_WORKERS)
