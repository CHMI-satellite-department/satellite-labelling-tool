import numpy as np
import time

from .config import DEBUG


def time_passed(start=0):
    return round(time.mktime(time.localtime())) - start


def frame_timestamp(image_dataloader, i: int) -> str:
    """Convert frame number to timestamp"""
    return str(image_dataloader.attrs[i]['datetime'])


def debug_print(*args):
    if DEBUG:
        print(*args)


def dl2np(dl):
    """Create numpy array from list of xr.DataArrays"""
    data = np.stack([np.moveaxis(da.values, 0, -1) for da in dl])

    data = data[:, ::-1, :]
    lat = dl[0].lat
    lon = dl[1].lon

    return data, lat, lon
