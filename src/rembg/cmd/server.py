import argparse
from io import BytesIO
import io
from urllib.parse import unquote_plus
from urllib.request import urlopen
from flask import Flask, request, send_file
import numpy as np
from waitress import serve
from ..u2net.detect import nn_forwardpass
from ..bg import get_model, remove_many
import datetime
import subprocess as sp
from multiprocessing import shared_memory, Process, Lock
from multiprocessing import cpu_count, current_process
import time
import json
from ilock import ILock

app = Flask(__name__)

net = get_model("u2net_human_seg")

lock = Lock()
a = np.ones(shape=(25,3,320,320), dtype=np.float32)  
shm = shared_memory.SharedMemory(create=True, size=a.nbytes)
np_array = np.ndarray((25,3,320,320), dtype=np.float32, buffer=shm.buf)

@app.route("/key/", methods=["GET"])
def get_key():
    return shm.name


@app.route("/", methods=["GET", "POST"])
def index():

    with ILock('gpu_processing_lock'):

        existing_shm = shared_memory.SharedMemory(name=shm.name)
        np_array = np.ndarray((25,3,320,320), dtype=np.float32, buffer=existing_shm.buf)
        masks = nn_forwardpass(np_array, net)
        print( F"{datetime.datetime.now()}: sent {masks.shape[0]} images" )
        # copy result back into shared memory
        np_array[:,0,:,:] = masks

        return 'Done'


def main():


    print("SHARED MEMORY CREATED: ", shm.name)

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "-a",
        "--addr",
        default="0.0.0.0",
        type=str,
        help="The IP address to bind to.",
    )

    ap.add_argument(
        "-p",
        "--port",
        default=5000,
        type=int,
        help="The port to bind to.",
    )

    args = ap.parse_args()

    serve(app, host=args.addr, port=args.port, threads=4)


if __name__ == "__main__":
    
    main()
