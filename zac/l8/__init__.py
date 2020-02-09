import os
import sys
from datetime import datetime
from glob import glob
from os.path import expanduser

import gdal
import numpy as np
import requests

from zac import HOME, DEFAULT_MCD43_DIR, DEFAULT_MCD43_VRT_DIR
from zac.create_logger import create_logger
from zac.downloaders import downloader
from zac.get_MCD43 import get_mcd43
from zac.l8.preprocessing import l8_pre_processing
from zac.multi_process import parmap
from zac.the_aerosol import solve_aerosol
from zac.the_correction import atmospheric_correction

file_path = os.path.dirname(os.path.realpath(__file__))


def zac_l8(
    l8_dir,
    send_back=False,
    mcd43=DEFAULT_MCD43_DIR,
    vrt_dir=DEFAULT_MCD43_VRT_DIR,
    aoi=None,
    global_dem="/vsicurl/http://www2.geog.ucl.ac.uk/~ucfafyi/eles/global_dem.vrt",
    cams_dir="/vsicurl/http://www2.geog.ucl.ac.uk/~ucfafyi/cams/",
):
    rets = l8_pre_processing(l8_dir)
    aero_atmos = []
    for ret in rets:
        ret += (mcd43, vrt_dir, aoi, global_dem, cams_dir)
        # sun_ang_name, view_ang_names, toa_refs, cloud_name, cloud_mask, metafile = ret
        aero_atmo = do_correction(*ret)
        if send_back:
            aero_atmos.append(aero_atmo)
    if send_back:
        return aero_atmos


def do_correction(
    sun_ang_name,
    view_ang_names,
    toa_refs,
    qa_name,
    cloud_mask,
    metafile,
    mcd43=DEFAULT_MCD43_DIR,
    vrt_dir=DEFAULT_MCD43_VRT_DIR,
    aoi=None,
    global_dem="/vsicurl/http://www2.geog.ucl.ac.uk/~ucfafyi/eles/global_dem.vrt",
    cams_dir="/vsicurl/http://www2.geog.ucl.ac.uk/~ucfafyi/cams/",
):

    if os.path.realpath(mcd43) in os.path.realpath(DEFAULT_MCD43_DIR)\
        and not os.path.exists(DEFAULT_MCD43_DIR):
        os.mkdir(DEFAULT_MCD43_DIR)

    if os.path.realpath(vrt_dir) in os.path.realpath(DEFAULT_MCD43_VRT_DIR)\
        and not os.path.exists(DEFAULT_MCD43_VRT_DIR):
        os.mkdir(DEFAULT_MCD43_VRT_DIR)

    base = os.path.dirname(toa_refs[0])
    with open(metafile) as f:
        for line in f:
            if "REFLECTANCE_MULT_BAND" in line:
                scale = float(line.split()[-1])
            elif "REFLECTANCE_ADD_BAND" in line:
                off = float(line.split()[-1])
            elif "DATE_ACQUIRED" in line:
                date = line.split()[-1]
            elif "SCENE_CENTER_TIME" in line:
                time = line.split()[-1]
    log_file = os.path.join(os.path.dirname(metafile), "zac_l8.log")
    logger = create_logger(log_file)
    logger.info("Starting atmospheric corretion for %s" % base)
    datetime_str = date + time
    obs_time = datetime.strptime(datetime_str.split(".")[0], '%Y-%m-%d"%H:%M:%S')
    if not np.all(cloud_mask):
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)
        vrt_dir = get_mcd43(
            toa_refs[0],
            obs_time,
            mcd43_dir=mcd43,
            vrt_dir=vrt_dir,
            log_file=log_file,
        )

    else:
        logger.info("No clean pixel in this scene and no MCD43 is downloaded.")
    sensor_sat = "OLI", "L8"
    band_index = [1, 2, 3, 4, 5, 6]
    band_wv = [469, 555, 645, 859, 1640, 2130]
    toa_bands = (np.array(toa_refs)[band_index,]).tolist()
    view_angles = (np.array(view_ang_names)[band_index,]).tolist()
    sun_angles = sun_ang_name
    sza = gdal.Open(sun_angles).ReadAsArray()[1] * 0.01
    scale = scale / np.cos(np.deg2rad(sza))
    off = off / np.cos(np.deg2rad(sza))
    aero = solve_aerosol(
        sensor_sat,
        toa_bands,
        band_wv,
        band_index,
        view_angles,
        sun_angles,
        obs_time,
        cloud_mask,
        gamma=10.0,
        ref_scale=scale,
        ref_off=off,
        global_dem=global_dem,
        cams_dir=cams_dir,
        spec_m_dir=os.path.join(os.path.dirname(file_path), "spectral_mapping", ""),
        emus_dir=os.path.join(os.path.dirname(file_path), "emus", ""),
        mcd43_dir=vrt_dir,
    )
    aero._solving()
    toa_bands = toa_refs
    view_angles = view_ang_names
    base = os.path.join(base, "B".join(toa_bands[0].split("/")[-1].split("B")[:-1]))
    aot = base + "aot.tif"
    tcwv = base + "tcwv.tif"
    tco3 = base + "tco3.tif"
    aot_unc = base + "aot_unc.tif"
    tcwv_unc = base + "tcwv_unc.tif"
    tco3_unc = base + "tco3_unc.tif"
    rgb = [toa_bands[3], toa_bands[2], toa_bands[1]]
    band_index = [0, 1, 2, 3, 4, 5, 6]
    atmo = atmospheric_correction(
        sensor_sat,
        toa_bands,
        band_index,
        view_angles,
        sun_angles,
        aot=aot,
        cloud_mask=cloud_mask,
        tcwv=tcwv,
        tco3=tco3,
        aot_unc=aot_unc,
        tcwv_unc=tcwv_unc,
        tco3_unc=tco3_unc,
        global_dem=global_dem,
        cams_dir=cams_dir,
        rgb=rgb,
        ref_scale=scale,
        ref_off=off,
        emus_dir=os.path.join(file_path, "emus", ""),
        aoi=aoi,
    )
    atmo._doing_correction()
    return aero, atmo
