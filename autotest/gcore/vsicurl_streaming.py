#!/usr/bin/env pytest
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test /vsicurl_streaming
# Author:   Even Rouault <even dot rouault at spatialys.com>
#
###############################################################################
# Copyright (c) 2012-2013, Even Rouault <even dot rouault at spatialys.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

import time

import gdaltest
import pytest

from osgeo import gdal

pytestmark = pytest.mark.require_curl()

###############################################################################
#


def test_vsicurl_streaming_1():

    gdal.SetConfigOption("GDAL_HTTP_CONNECTTIMEOUT", "5")
    fp = gdal.VSIFOpenL(
        "/vsicurl_streaming/http://download.osgeo.org/gdal/data/usgsdem/cded/114p01_0100_deme.dem",
        "rb",
    )
    gdal.SetConfigOption("GDAL_HTTP_CONNECTTIMEOUT", None)
    if fp is None:
        if (
            gdaltest.gdalurlopen(
                "http://download.osgeo.org/gdal/data/usgsdem/cded/114p01_0100_deme.dem",
                timeout=4,
            )
            is None
        ):
            pytest.skip("cannot open URL")
        pytest.fail()

    if gdal.VSIFTellL(fp) != 0:
        gdal.VSIFCloseL(fp)
        pytest.fail()
    data = gdal.VSIFReadL(1, 50, fp)
    if data.decode("ascii") != "                              114p01DEMe   Base Ma":
        gdal.VSIFCloseL(fp)
        pytest.fail()
    if gdal.VSIFTellL(fp) != 50:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    gdal.VSIFSeekL(fp, 0, 0)

    if gdal.VSIFTellL(fp) != 0:
        gdal.VSIFCloseL(fp)
        pytest.fail()
    data = gdal.VSIFReadL(1, 50, fp)
    if data.decode("ascii") != "                              114p01DEMe   Base Ma":
        gdal.VSIFCloseL(fp)
        pytest.fail()
    if gdal.VSIFTellL(fp) != 50:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    time.sleep(0.5)
    gdal.VSIFSeekL(fp, 2001, 0)
    data_2001 = gdal.VSIFReadL(1, 20, fp)
    if data_2001.decode("ascii") != "7-32767-32767-32767-":
        gdal.VSIFCloseL(fp)
        pytest.fail(data_2001)
    if gdal.VSIFTellL(fp) != 2001 + 20:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    gdal.VSIFSeekL(fp, 0, 2)
    if gdal.VSIFTellL(fp) != 9839616:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    nRet = len(gdal.VSIFReadL(1, 10, fp))
    if nRet != 0:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    gdal.VSIFSeekL(fp, 2001, 0)
    data_2001_2 = gdal.VSIFReadL(1, 20, fp)
    if gdal.VSIFTellL(fp) != 2001 + 20:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    if data_2001 != data_2001_2:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    gdal.VSIFSeekL(fp, 1024 * 1024 + 100, 0)
    data = gdal.VSIFReadL(1, 20, fp)
    if data.decode("ascii") != "67-32767-32767-32767":
        gdal.VSIFCloseL(fp)
        pytest.fail(data)
    if gdal.VSIFTellL(fp) != 1024 * 1024 + 100 + 20:
        gdal.VSIFCloseL(fp)
        pytest.fail()

    gdal.VSIFCloseL(fp)
