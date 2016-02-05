#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Stephane Chamberland <stephane.chamberland@canada.ca>
# Copyright: LGPL 2.1

"""
Module vgd.const defines constants for the vgd module
"""
import ctypes as _ct
## import numpy  as _np
## import numpy.ctypeslib as _npc

VGD_OK       = 0
VGD_ERROR    = -1
VGD_MISSING  = -9999.
VGD_MAXSTR_NOMVAR = 5
VGD_MAXSTR_TYPVAR = 3
VGD_MAXSTR_ETIKET = 13
VGD_MAXSTR_GRTYP  = 2

VGD_ALLOW_RESHAPE  = 0
VGD_ALLOW_SIGMA    = 1
VGD_DISALLOW_SIGMA = 0

VGD_SIGM_KIND = 1  #Sigma
VGD_SIGM_VER  = 1
VGD_ETA_KIND  = 1  #Eta
VGD_ETA_VER   = 2
VGD_HYBN_KIND = 1  #Hybrid Normalized
VGD_HYBN_VER  = 3
VGD_PRES_KIND = 2  #pressure
VGD_PRES_VER  = 1
VGD_HYB_KIND  = 5  #Hybrid Un-staggered
VGD_HYB_VER   = 1
VGD_HYBS_KIND = 5  #Hybrid staggered
VGD_HYBS_VER  = 2
VGD_HYBT_KIND = 5  #Hybrid staggered, first level is a thermo level, unstaggered last Thermo level
VGD_HYBT_VER  = 3
VGD_HYBM_KIND = 5  #Hybrid staggered, first level is a momentum level, same number of thermo and momentum levels
VGD_HYBM_VER  = 4

VGD_DIAG_LOGP = 1  #vgd_diag_withref: output log pressure
VGD_DIAG_PRES = 0  #vgd_diag_withref: output pressure
VGD_DIAG_DPI  = 1  #vgd_diag_withref: output pressure
VGD_DIAG_DPIS = 0  #vgd_diag_withref: output hydrostatic pressure partial derivative with respect to surface hydrostatic pressure, default used in vgd_levels

VGD_KIND_VER = {
    'sigm' : (VGD_SIGM_KIND, VGD_SIGM_VER),
    'eta'  : (VGD_ETA_KIND, VGD_ETA_VER),
    'hybn' : (VGD_HYBN_KIND, VGD_HYBN_VER),
    'pres' : (VGD_PRES_KIND, VGD_PRES_VER),
    'hyb'  : (VGD_HYB_KIND, VGD_HYB_VER),
    'hybs' : (VGD_HYBS_KIND, VGD_HYBS_VER),
    'hybt' : (VGD_HYBT_KIND, VGD_HYBT_VER),
    'hybm' : (VGD_HYBM_KIND, VGD_HYBM_VER)
    }

VGD_OPR_KEYS = {
    'get_char'      : ["ETIK", "NAME", "RFLD"],
    'put_char'      : ["ETIK", "NAME", "RFLD"],
    'get_int'       : ["NL_M", "NL_T", "KIND", "VERS", "DATE", "IG_1", "IG_2",
                       "IG_3", "IG_4", "IP_1", "IP_2", "DIPM", "DIPT", "MIPG",
                       "LOGP"],
    'put_int'       : ["DATE", "IG_1", "IG_2", "IG_3", "IG_4", "IP_1", "IP_2",
                       "IP_3", "DIPM", "DIPT"],
    'get_float'     : ["RC_1", "RC_2", "DHM", "DHT"],     
    'get_int_1d'    : ["VIP1", "VIPM", "VIPT"], 
    'get_float_1d'  : ["VCDM", "VIPM", "VCDT", "VIPT"], 
    'put_double'    : ["PTOP", "PREF", "RC_1", "RC_2"],
    'get_double'    : ["PTOP", "PREF", "RC_1", "RC_2"],
    'get_double_1d' : ["CA_M", "COFA", "CB_M", "COFB", "CA_T", "CB_T"],
    'get_double_3d' : ["VTBL"],
    'getopt_int'    : ["ALLOW_SIGMA"],
    'putopt_int'    : ["ALLOW_SIGMA"]
    }

VGD_KEYS = {
    'KIND' : ('Kind of the vertical coordinate ip1'),
    'VERS' : ('Vertical coordinate version. For a given kind there may be many versions, example kind=5 version=2 is hyb staggered GEM4.1'),
    'NL_M' : ('Number of momentum levels (verison 3.2.0 and up)'),
    'NL_T' : ('Number of thermodynamic levels (version 3.2.0 and up)'),
    'CA_M' : ('Values of coefficient A on momentum levels'),
    'CA_T' : ('Values of coefficient A on thermodynamic levels'),
    'CB_M' : ('Values of coefficient B on momentum levels'),
    'CB_T' : ('Values of coefficient B on thermodynamic levels'),
    'COFA' : ('Values of coefficient A in unstaggered levelling'),
    'COFB' : ('Values of coefficient B in unstaggered levelling'),
    'DIPM' : ('The IP1 value of the momentum diagnostic level'),
    'DIPT' : ('The IP1 value of the thermodynamic diagnostic level'),
    'DHM'  : ('Height of the momentum diagonstic level (m)'),
    'DHT'  : ('Height of the thermodynamic diagonstic level (m)'),
    'PREF' : ('Pressure of the reference level (Pa)'),
    'PTOP' : ('Pressure of the top level (Pa)'),
    'RC_1' : ('First coordinate recification R-coefficient'),
    'RC_2' : ('Second coordinate recification R-coefficient'),
    'RFLD' : ('Name of the reference field for the vertical coordinate in the FST file'),
    'VCDM' : ('List of momentum coordinate values'),
    'VCDT' : ('List of thermodynamic coordinate values'),
    'VIPM' : ('List of IP1 momentum values associated with this coordinate'),
    'VIPT' : ('List of IP1 thermodynamic values associated with this coordinate'),
    'VTBL' : ('real*8 Fortran 3d array containing all vgrid_descriptor information'),
    'LOGP' : ('furmula gives log(p) T/F (version 1.0.3 and greater). True -> Formula with A and B gives log(p), False -> Formula with A and B gives p'),
    'ALLOW_SIGMA' : ('Allow definition of sigma coor or not')
    }


# -*- Mode: C; tab-width: 4; indent-tabs-mode: nil -*-
# vim: set expandtab ts=4 sw=4:
# kate: space-indent on; indent-mode cstyle; indent-width 4; mixedindent off;
