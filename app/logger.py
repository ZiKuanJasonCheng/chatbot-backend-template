import logging 

def setForWritefile(name: str, file_path: str):
    # logging.basicConfig(filename=file_path,
    #                     filemode='a',
    #                     format='[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s',
    #                     datefmt="%Y-%m-%d %H:%M:%S %z",
    #                     level=logging.DEBUG)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filename=file_path)
    fh.setLevel(logging.DEBUG)

    fmt = '[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s'
    datefmt = "%Y-%m-%d %H:%M:%S %z"
    formatter = logging.Formatter(fmt, datefmt)

    sh.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger
