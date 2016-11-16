# see also source/regtestutils.py

%pylab

from regtestutils import datamaker
import galextools as gt
import MCUtils as mc
import pandas as pd
import gphoton_utils as gu
import gFind
from FileUtils import flat_filename
import numpy as np
import matplotlib.pyplot as plt

skypos = {'LDS749B':[323.06766667,0.25400000],
          'PS_CDFS_MOS00':[53.1032558472, -27.7963826072],
          'CDFS_00':[53.1273118244, -27.8744513656]}
bands = ['NUV','FUV']

ra0,dec0=skypos['LDS749B']

from gPhoton.regtestutils import datamaker
datamaker('FUV',[323.06766667,0.25400000],'LDS749B_dm_FUV.csv',margin=0.001,searchradius=0.001)

from gPhoton.regtestutils import datamaker
datamaker('NUV',[323.06766667,0.25400000],'LDS749B_dm_NUV.csv',margin=0.001,searchradius=0.001)

"""The following gCalrun commands generate photometry for a large number of
random sources, which serves as a test of relative photometry.
"""
./gCalrun -f 'DPFCore_calrun_FUV.csv' -b 'FUV' --rarange [0,360] --decrange [-90,90] -n 100 --seed 323 -v 1

./gCalrun -f 'DPFCore_calrun_NUV.csv' -b 'NUV' --rarange [0,360] --decrange [-90,90] -n 100 --seed 323 -v 1

"""The following gAperture commands generate photometry for the full depth
of LDS749B observations, a test of absolute photometry.
"""
./gAperture --skypos [323.06766667,0.25400000] -a 0.005 --annulus [0.01,0.02] -b 'NUV' -v 2 -f 'LDS749B_NUV.csv' --maxgap 50 --minexp 90 --overwrite

./gAperture --skypos [323.06766667,0.25400000] -a 0.005 --annulus [0.01,0.02] -b 'NUV' -v 2 -f 'LDS749B_NUV_-9.csv' --maxgap 50 --minexp 90 --overwrite --t0 1 --t1 900000000.

./gAperture --skypos [323.06766667,0.25400000] -a 0.005 --annulus [0.01,0.02] -b 'NUV' -v 2 -f 'LDS749B_NUV_9-.csv' --maxgap 50 --minexp 90 --overwrite --t0 900000000. --t1 1100000000.


./gAperture --skypos [323.06766667,0.25400000] -a 0.005 --annulus [0.01,0.02] -b 'FUV' -v 2 -f 'LDS749B_FUV.csv' --maxgap 50 --minexp 90 --overwrite



###############################################################################
def error(data,band,radius,annulus):
    N_a = 1
    N_b0 = (mc.area(annulus[1])-mc.area(annulus[0]))/mc.area(radius)
    N_b = data[band]['bg_eff_area']/mc.area(radius)
    B0 = data[band]['bg']
    B = data[band]['bg_cheese']
    S = gt.mag2counts(data[band]['mag'],band)*data[band]['t_eff']
    s2 = {'bg_cheese_err':(S-B)+(N_a+(N_a**2.)/N_b),
          'bg_err':(S-B0)+(N_a+(N_a**2.)/N_b0)}
    return s2

###############################################################################
# Jake VanderPlas was nice enough to make a clean looking template for us...
from astroML.plotting import setup_text_plots
scl = 1.8
setup_text_plots(fontsize=8*scl, usetex=False)

bands = ['NUV','FUV']
base = 'DB10_calrun_'
data = {}
for band in bands:
    data[band] = pd.read_csv('{base}{band}.csv'.format(
                                                        base=base,band=band))
    print '{band} sources: {cnt}'.format(
                                band=band,cnt=data[band]['objid'].shape[0])

"""dMag vs. Mag"""
for band in bands:
    dmag = {'gphot_cheese':(lambda band:
                        data[band]['aper4']-data[band]['mag_bgsub_cheese']),
                 'gphot_nomask':(lambda band:
                        data[band]['aper4']-data[band]['mag_bgsub']),
                 'gphot_sigma':(lambda band:
                        data[band]['aper4']-data[band]['mag_bgsub_sigmaclip']),
                 'mcat':lambda band: data[band]['aper4']-
                        gt.counts2mag(gt.mag2counts(data[band]['mag'],band)-
                        data[band]['skybg']*3600**2*mc.area(gt.aper2deg(4)),
                        band)}
bgmodekeys={'gphot_cheese':'mag_bgsub_cheese',
            'gphot_nomask':'mag_bgsub',
            'gphot_sigma':'mag_bgsub_sigmaclip',
            'mcat':'skybg'}
for bgmode in dmag.keys():
    for band in bands:
        fig = plt.figure(figsize=(8*scl,4*scl))
        fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,
                                                        bottom=0.15,top=0.9)
        dmag_err=gu.dmag_errors(100.,band,sigma=1.41)
        # Make a cut on crazy outliers in the MCAT. Also on det radius and expt.
        ix = ((data[band]['aper4']>0) & (data[band]['aper4']<30) &
              (data[band]['distance']<300) & (data[band]['t_eff']<300) &
              (np.isfinite(np.array(data[band][bgmodekeys[bgmode]]))))
        plt.subplot(1,2,1)
        plt.title('{band} {d}Mag vs. AB Mag (n={n},{bg}_bg)'.format(
                            d=r'$\Delta$',band=band,n=ix.shape[0],bg=bgmode))
        plt.xlabel('AB Magnitude (MCAT)')
        plt.ylabel(r'{d}Magnitude (MCAT-gPhoton)'.format(d=r'$\Delta$'))
        plt.axis([13,23,-1.3,1.3])
        plt.plot(data[band]['aper4'][ix],dmag[bgmode](band)[ix],'.',
                        alpha=0.25,color='k',markersize=5,label='gPhoton Mags')
        plt.plot(dmag_err[0],dmag_err[1],color='k',
                        label='1.41{s}'.format(s=r'$\sigma$'))
        plt.plot(dmag_err[0],dmag_err[2],color='k')
        plt.legend()
        plt.subplot(1,2,2,xticks=[],yticks=[],ylim=[-1.3,1.3])
        plt.title('{d}Magnitude Histogram ({band})'.format(
                                                    d=r'$\Delta$',band=band))
        plt.hist(np.array(dmag[bgmode](band)[ix]),
                        bins=np.floor(ix.shape[0]/10.),range=[-1.3,1.3],
                        orientation='horizontal',color='k')
        fig.savefig(
            '../calpaper/src/dMag_v_Mag({band},{bg}_bg).png'.format(
                                                        band=band,bg=bgmode))

#"""Compare Errors"""
#fig = plt.figure(figsize=(4*scl,8*scl))
#fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,bottom=0.05,top=0.95)
#for i,band in enumerate(bands):
#    s2 = error(data,band,gt.aper2deg(4),[0.0083,0.025])
#    dflux = np.sqrt(s2['bg_cheese_err'])/data[band]['t_eff'] # \Delta cps
#    flux = gt.mag2counts(data[band]['mag'],band) # cps
#    dmag = 2.5*np.log10((flux+dflux)/flux)
#    plt.subplot(2,1,i+1,yticks=[],xlim=[0,1])
#    plt.title('{band} Magnitude Errors'.format(band=band))
#    plt.hist(dmag,bins=100,range=[0,1],color='r',label='gPhoton')
#    plt.hist(data[band]['aper4_err'],bins=100,range=[0,1],color='k',
#                                                                label='MCAT')
#    plt.legend()
#fig.savefig('../calpaper/src/mag_err.png')

"""Background Plots
The gPhoton background is scaled to counts in the aperture and the
MCAT skybg is in units of arcsec^2/s, so we'll scale the skybg to the
aperture and put the gPhoton bg in cps.
"""
bgmodes=['bg_cheese','bg','bg_sigmaclip']
for mode in bgmodes:
    fig = plt.figure(figsize=(8*scl,4*scl))
    fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,bottom=0.15,top=0.9)
    for i,band in enumerate(bands):
        gphot_bg = gt.counts2mag(
                        data[band][mode]/data[band]['t_eff'],band)
        #gphot_bg = gt.counts2mag(data[band]['bg_cheese']/data[band]['t_eff'],band)
        mcat_bg = gt.counts2mag(
                    data[band]['skybg']*3600**2*mc.area(gt.aper2deg(4)),band)
        delta = mcat_bg - gphot_bg
        ix = (np.isfinite(delta))
        plt.subplot(1,2,i+1,yticks=[],xlim=[-3,3])
        plt.title('{band} {mode} Background {d}Magnitude (MCAT-gPhoton)'.format(
                                            band=band,mode=mode,d=r'$\Delta$'))
        plt.hist(delta[ix],bins=500,range=[-3,3],color='k')
    fig.savefig('../calpaper/src/dMag_{mode}.png'.format(mode=mode))

#"""Background 'Magnitude' vs. Source Magnitude"""
#for i,band in enumerate(bands):
#    fig = plt.figure(figsize=(8*scl,4*scl))
#    fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,bottom=0.15,top=0.9)
#    gphot_bg = gt.counts2mag(data[band]['bg']/data[band]['t_eff'],band)
#    mcat_bg = gt.counts2mag(
#                    data[band]['skybg']*3600**2*mc.area(gt.aper2deg(4)),band)
#    delta = mcat_bg - gphot_bg
#    ix = (np.isfinite(delta))
#    plt.subplot(1,2,1,xlim=[14,25])
#    plt.title('{band} Background vs. Magnitude (MCAT)'.format(band=band))
#    plt.plot(data[band]['aper4'][ix],mcat_bg[ix],'.',color='k',alpha=0.2)
#    plt.subplot(1,2,2,xlim=[14,25],yticks=[])
#    plt.title('{band} Background vs. Magnitude (gPhoton)'.format(band=band))
#    plt.plot(data[band]['mag_bgsub_cheese'][ix],gphot_bg[ix],'.',
#                                                        color='k',alpha=0.2)
#fig.savefig('../calpaper/src/bg_v_mag.png')

"""Astrometry"""
a = 3600
for i,band in enumerate(bands):
    fig = plt.figure(figsize=(8*scl,8*scl))
    fig.subplots_adjust(left=0.12,right=0.95,hspace=0.02,wspace=0.02,
                                                        bottom=0.15,top=0.9)
    dRA = data[band]['ra']-data[band]['racent']
    dDec = data[band]['dec']-data[band]['deccent']
    # dRA v. dDec
    plt.subplot(2,2,1,xticks=[])
    plt.ylabel('{d}RA (arcsec)'.format(d=r'$\Delta$'))
    plt.title('{band} {d}Centroid (MCAT-gPhoton)'.format(
                                                     band=band,d=r'$\Delta$'))
    plt.axis([-0.004*a,0.004*a,-0.004*a,0.004*a])
    plt.plot(dRA*np.cos(data[band]['dec'])*a,dDec*a,'.',alpha=0.1,color='k',
                                                                 markersize=5)
    # dRA
    plt.subplot(2,2,2,yticks=[],xticks=[],ylim=[-0.004*a,0.004*a])
    plt.hist(dRA*np.cos(data[band]['ra'])*a,bins=500,orientation='horizontal',
                                                                    color='k')
    # dDec
    plt.subplot(2,2,3,yticks=[],xlim=[-0.004*a,0.004*a])
    plt.xlabel('{d}Dec (arcsec)'.format(d=r'$\Delta$'))
    plt.gca().invert_yaxis()
    plt.hist(dDec*a,bins=500,color='k')
    fig.savefig('../calpaper/src/dRA_v_dDec({band})'.format(band=band))

fig = plt.figure(figsize=(8*scl,4*scl))
fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,bottom=0.15,top=0.9)
for i,band in enumerate(bands):
    delta = mc.angularSeparation(data[band]['ra'],data[band]['dec'],
                                 data[band]['racent'],data[band]['deccent'])
    plt.subplot(1,2,i+1,yticks=[],xlim=[0.*a,0.002*a])
    plt.title('{band} Angular Separation (arcsec)'.format(
                                                    band=band,d=r'$\Delta$'))
    plt.hist(delta*a,bins=500,range=[0.*a,0.002*a],color='k')
    fig.savefig('../calpaper/src/angSep({band}).png'.format(band=band))

###############################################################################
"""Deadtime Sanity Checks
According to the calibration paper, the FUV deadtime correction should be
small (~ a few percent), but it is actually bigger than the NUV correction.
"""
fig = plt.figure(figsize=(8,4))
fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,bottom=0.15,top=0.9)
for i,band in enumerate(bands):
    plt.subplot(1,2,i+1,yticks=[])
    plt.title('{band} Deadtime Ratio Histogram'.format(band=band))
    plt.hist(data[band]['t_eff']/data[band]['t_raw'],bins=100,range=[0.2,1.2])

"""Response Sanity Checks"""
fig = plt.figure(figsize=(8,4))
fig.subplots_adjust(left=0.12,right=0.95,wspace=0.02,bottom=0.15,top=0.9)
for i,band in enumerate(bands):
    flat = mc.get_fits_data(flat_filename(band,'../cal/'))
    plt.subplot(1,2,i+1,yticks=[])
    plt.title('{band} Response Histogram'.format(band=band))
    plt.hist(flat.flatten(),bins=100,range=[0.2,1.2])
    plt.hist(data[band]['response'],bins=100,range=[0.2,1.2])
