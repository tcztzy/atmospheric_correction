Quickstart
===========

The usage of zac for Sentinel 2 and Landsat 8 Top Of Atmosphere (TOA) reflectance is very straight forward: 

**Sentinel 2** ::

    from zac import zac_s2
    zac_s2('/directory/where/you/store/S2/data/') # this can be either from AWS or Senitinel offical package

**Landsat 8** ::

    from zac import zac_l8                                                                           
    zac_l8('/directory/where/you/store/L8/data/') 

An example usage of zac over other sensors and the way to access all the ancillary data is shown with a `jupyter notebook example <https://github.com/MarcYin/Global-analysis-ready-dataset/blob/master/15%20years%2010-30%20meters%20consistent%20uncertainty%20quantified%20global%20analysis%20ready%20dataset.ipynb>`_.
