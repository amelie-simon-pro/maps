import cartopy.crs as ccrs
import numpy as np
import itertools

import netCDF4 as nc4
from netCDF4 import Dataset, date2index, num2date, date2num

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as colors
from matplotlib.colors import TwoSlopeNorm
import cartopy.feature as cfeature

from datetime import datetime
START = datetime.now() 
import os


#BEGIN CHOICE
model='era5' #'oisst' #'era5'
var_name='z500' # #'slp' 'z500', 'sst'
print(var_name)
print(var_name.lower())
time_reso="mth.mean"
spatial_reso='1440x720'
yearbeg=1982  
yearend=2022 
region='80W38E-20N75N'
lonmin_plot=-80 
lonmax_plot=38
latmin_plot=20 
latmax_plot=75 
delta_space=0.25
mask=-1 #-1 #4
#
import_data='y'
plot='y'
latex='y'
format_fig='png' #'eps'
#END CHOICE

# IMPORT
pathdata="/home ...TO FILL"
pathoutputfig = "TO FILL"
pathoutputlatex = "/home TO FILL"
data=f'{model}.{var_name}.{time_reso}.{yearbeg}{yearend}.{spatial_reso}.{region}'


if model == 'era5':
   model_fullname='CDS.ERA5'
   lat='lat'
   lon='lon'
elif model == 'oisst':
   model_fullname='NOAA.OISST.V2.HIGHRES'
   lat='lat'
   lon='lon'
   
if var_name == 'slp': # help with stat function of ferret
   levels_abs=np.linspace(1000,1025,100)
   ticks_abs=[1000,1005,1010,1015,1020,1025]
   levels_ano=np.linspace(-10,10,100)
   ticks_ano=[-10,-8,-6,-4,-2,0,2,4,6,8,10]
   levels_ano_small=np.linspace(-5,5,100)
   ticks_ano_small=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
   factor=100
   unit='hPa' 
if var_name == 'z500':
   levels_abs=np.linspace(5000,6000,100)
   ticks_abs=[5000,5500,6000]
   levels_ano=np.linspace(-200,200,100)
   levels_ano_small=np.linspace(-100,100,100)
   ticks_ano=[-200,-100,0,100,200]
   ticks_ano_small=[-100,-50,0,50,100]
   factor=9.80665
   unit='m'   
if var_name == 'sst':
   levels_abs=np.linspace(-5,30,100)
   ticks_abs=[-5,0,5,10,15,20,25,30]
   levels_ano=np.linspace(-3,3,100)
   ticks_ano=[-3,-2,-1,0,1,2,3]
   levels_ano_small=np.linspace(-3,3,100)
   ticks_ano_small=[-3,-2,-1,0,1,2,3]
   factor=1
   unit='ºC'    
print(data)
      
nb_year=yearend-yearbeg+1

if import_data == "y":
   ###############       
   # IMPORT DATA #
   ###############
   print("IMPORT DATA")
   
   #lon = np.arange(input_lonmin,input_lonmax,delta_space)
   #lat = np.arange(input_latmin,input_latmax,delta_space)
   #print("lon",lon)
   #print("lat",lat)
   #print("shape time",np.shape(time))
   
   file_name= f'{pathdata}/{model_fullname}/{data}.nc'
   print(file_name)
   fh = Dataset(file_name, mode='r')  
   var= fh.variables[f'{var_name}'][:] 
   #var= fh.variables[f'{var_name}'.lower()][:]   
   lat = fh.variables[f'{lat}'][:]
   lon = fh.variables[f'{lon}'][:]
   print("var",np.shape(var)) # (time,lat,lon)
   print("lon shape",np.shape(lon))
   print("lat shape",np.shape(lat))
   fh.close()
   
   mask_file=np.zeros((lat.shape[0],lon.shape[0]))
   if mask < 0:
      mask_file[:,:]=mask
   else:
      mask_file=np.load(f'{pathdata}/MASK/OceanMasks_{model}_{spatial_reso}_{region}.npy')
   print(mask_file)
   print("mask_file",np.shape(mask_file))
   
   time = np.arange(0,(yearend-yearbeg+1)*12,1)

if plot == 'y':
   ###############        
   # PLOT FIGURE #
   ###############
   print('PLOT')

   # climatology per month
   for nb_mth in range(0,12):
      fig = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      #ax.add_feature(cfeature.LAND,zorder=100, edgecolor='k')
      ax.coastlines()
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f' {var_name} in {unit} - Month {nb_mth+1} Climatology in {yearbeg}{yearend} ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot]) 
      plt.contourf(lon,lat,np.average(var[nb_mth::12,:,:],axis=0)/factor, levels=levels_abs, cmap=plt.cm.RdBu_r,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal",ticks=ticks_abs, pad=0.1)
      cb.ax.tick_params(labelsize=16)
      fig.savefig(f'{pathoutputfig}/map_{data}.{nb_mth+1}.clim{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig)
   

   # anomaly per month
   for nb_yr in range(yearbeg,yearend+1): 
      print(nb_yr)         
      for nb_mth in range(0,12): #range(0,9):
         print(nb_mth)
         fig2 = plt.figure(figsize=(8,6))
         ax = plt.axes(projection=ccrs.PlateCarree())
         ax.coastlines()
         gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
         gl.top_labels = False
         gl.right_labels = False
         gl.xlabel_style = dict(fontsize=16)
         gl.ylabel_style = dict(fontsize=16)
         ax.set_xlabel('Longitude(°)')	
         ax.set_label('Latitude(°)')
         plt.title(f'{var_name} in {unit} - {nb_yr}-{nb_mth+1} anomaly with the average of months {nb_mth+1} in {yearbeg}{yearend} ')
         plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
         plt.contourf(lon,lat,(var[nb_mth+12*(nb_yr-yearbeg),:,:]- np.average(var[nb_mth::12,:,:],axis=0))/factor ,levels=levels_ano, cmap=plt.cm.RdBu_r,extend='both')
         cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano,pad=0.1)
         cb.ax.tick_params(labelsize=16) 
         fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr}-{nb_mth+1}.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
         plt.close(fig2)
        
   for nb_yr in range(yearbeg,yearend+1): #range(2018,2019):
      # anomalie par JJAS 
      print("JJAS", nb_yr)         
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} - {nb_yr}-JJAS anomaly with the average of months JJAS in {yearbeg}{yearend} ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
      plt.contourf(lon,lat,( (var[5+12*(nb_yr-yearbeg),:,:]- np.average(var[5::12,:,:],axis=0)) + (var[6+12*(nb_yr-yearbeg),:,:]- np.average(var[6::12,:,:],axis=0)) + (var[7+12*(nb_yr-yearbeg),:,:]- np.average(var[7::12,:,:],axis=0)) + (var[8+12*(nb_yr-yearbeg),:,:]- np.average(var[8::12,:,:],axis=0)) )/(4.*factor) ,levels=levels_ano_small, cmap=plt.cm.RdBu_r,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano_small,pad=0.1)
      cb.ax.tick_params(labelsize=16) 
      fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr}-JJAS.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)
      

      # anomaly per JJA
      print("JJA", nb_yr)         
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} - {nb_yr}-JJA anomaly with the average of months JJA in {yearbeg}{yearend} ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
      plt.contourf(lon,lat,( (var[5+12*(nb_yr-yearbeg),:,:]- np.average(var[5::12,:,:],axis=0)) + (var[6+12*(nb_yr-yearbeg),:,:]- np.average(var[6::12,:,:],axis=0)) + (var[7+12*(nb_yr-yearbeg),:,:]- np.average(var[7::12,:,:],axis=0)) )/(3.*factor) ,levels=levels_ano_small, cmap=plt.cm.RdBu_r,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano_small,pad=0.1)
      cb.ax.tick_params(labelsize=16) 
      fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr}-JJA.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)
      
      # anomaly per JFM
      print("JFM", nb_yr)         
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} - {nb_yr}-JFM anomaly with the average of months JJAS in {yearbeg}{yearend} ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
      plt.contourf(lon,lat,( (var[0+12*(nb_yr-yearbeg),:,:]- np.average(var[0::12,:,:],axis=0)) + (var[1+12*(nb_yr-yearbeg),:,:]- np.average(var[1::12,:,:],axis=0)) + (var[2+12*(nb_yr-yearbeg),:,:]- np.average(var[2::12,:,:],axis=0)) )/(3.*factor) ,levels=levels_ano_small, cmap=plt.cm.RdBu_r,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano_small,pad=0.1)
      cb.ax.tick_params(labelsize=16) 
      fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr}-JFM.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)
   
      # anomaly per JJ   
      print("JJ", nb_yr)         
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} - {nb_yr}-JJ anomaly with the average of months JJ in {yearbeg}{yearend} ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
      plt.contourf(lon,lat,( (var[5+12*(nb_yr-yearbeg),:,:]- np.average(var[5::12,:,:],axis=0)) + (var[6+12*(nb_yr-yearbeg),:,:]- np.average(var[6::12,:,:],axis=0))  )/(2.*factor) ,levels=levels_ano_small, cmap=plt.cm.RdBu_r,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano_small,pad=0.1)
      cb.ax.tick_params(labelsize=16) 
      fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr}-JJ.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)
    
      # anomaly per AS 
      print("AS", nb_yr)         
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} - {nb_yr}-AS anomaly with the average of months AS in {yearbeg}{yearend} ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
      plt.contourf(lon,lat,( (var[7+12*(nb_yr-yearbeg),:,:]- np.average(var[7::12,:,:],axis=0)) + (var[8+12*(nb_yr-yearbeg),:,:]- np.average(var[8::12,:,:],axis=0))  )/(2.*factor) ,levels=levels_ano_small, cmap=plt.cm.RdBu_r,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano_small,pad=0.1)
      cb.ax.tick_params(labelsize=16) 
      fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr}-AS.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)
      
      if nb_yr != yearend:
         print("DJFM", nb_yr)         
         fig2 = plt.figure(figsize=(8,6))
         ax = plt.axes(projection=ccrs.PlateCarree())
         ax.coastlines()
         gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
         gl.top_labels = False
         gl.right_labels = False
         gl.xlabel_style = dict(fontsize=16)
         gl.ylabel_style = dict(fontsize=16)
         ax.set_xlabel('Longitude(°)')	
         ax.set_label('Latitude(°)')
         plt.title(f'{var_name} in {unit} - {nb_yr+1}-DJFM anomaly with the average of months DJFM in {yearbeg}{yearend} ')
         plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
         plt.contourf(lon,lat,( (var[11+12*(nb_yr-yearbeg),:,:]- np.average(var[11::12,:,:],axis=0)) + (var[12+12*(nb_yr-yearbeg),:,:]- np.average(var[12::12,:,:],axis=0)) + (var[13+12*(nb_yr-yearbeg),:,:]- np.average(var[13::12,:,:],axis=0)) + (var[14+12*(nb_yr-yearbeg),:,:]- np.average(var[14::12,:,:],axis=0)) )/(4.*factor) ,levels=levels_ano, cmap=plt.cm.RdBu_r,extend='both')
         cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano,pad=0.1)
         cb.ax.tick_params(labelsize=16) 
         fig2.savefig(f'{pathoutputfig}/map_{data}.{nb_yr+1}-DJFM.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
         plt.close(fig2)
   
 
   print("DJFM 1982", nb_yr)         
   fig2 = plt.figure(figsize=(8,6))
   ax = plt.axes(projection=ccrs.PlateCarree())
   ax.coastlines()
   gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
   gl.top_labels = False
   gl.right_labels = False
   gl.xlabel_style = dict(fontsize=16)
   gl.ylabel_style = dict(fontsize=16)
   ax.set_xlabel('Longitude(°)')	
   ax.set_label('Latitude(°)')
   plt.title(f'{var_name} in {unit} - 1982-DJFM anomaly with the average of months DJFM in {yearbeg}{yearend} ')
   plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
   plt.contourf(lon,lat,( (var[0+12*(nb_yr-yearbeg),:,:]- np.average(var[0::12,:,:],axis=0)) + (var[1+12*(nb_yr-yearbeg),:,:]- np.average(var[1::12,:,:],axis=0)) + (var[2+12*(nb_yr-yearbeg),:,:]- np.average(var[2::12,:,:],axis=0))  )/(4.*factor) ,levels=levels_ano, cmap=plt.cm.RdBu_r,extend='both')
   cb = plt.colorbar(ax=ax, orientation="horizontal", ticks=ticks_ano,pad=0.1)
   cb.ax.tick_params(labelsize=16) 
   fig2.savefig(f'{pathoutputfig}/map_{data}.1982-DJFM.mthAnomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
   plt.close(fig2)
      

   if var_name == 'sst':
      var_mask=np.zeros((var.shape[0],var.shape[1],var.shape[2]))
      for i in range(var.shape[2]):
         for j in range(var.shape[1]):
            if(mask_file[j,i]==mask and var[0,j,i]<100):
               var_mask[:,j,i]=var[:,j,i]     
      var_mask[var_mask==0]=np.nan
      color=plt.cm.Reds
      levels= np.linspace(0,4,11)
   else:
      var_mask=var
      color=plt.cm.RdBu_r
      levels= np.linspace(-5,5,11)
     
   print("CLIMATO JJAS")         
   fig2 = plt.figure(figsize=(8,6))
   ax = plt.axes(projection=ccrs.PlateCarree())
   ax.coastlines()
   ax.add_feature(cfeature.LAND)
   gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
   gl.top_labels = False
   gl.right_labels = False
   gl.xlabel_style = dict(fontsize=16)
   gl.ylabel_style = dict(fontsize=16)
   ax.set_xlabel('Longitude(°)')	
   ax.set_label('Latitude(°)')
   plt.title(f'{var_name} in {unit} - Climato JJAS in {yearbeg}{yearend} ')
   plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])    
   plt.contourf(lon,lat,( np.average(var_mask[5::12,:,:],axis=0) + np.average(var_mask[6::12,:,:],axis=0) + np.average(var_mask[7::12,:,:],axis=0) + np.average(var_mask[8::12,:,:],axis=0) )/(4.*factor), cmap=plt.cm.RdBu_r,extend='both')
   cb = plt.colorbar(ax=ax, orientation="horizontal", pad=0.1)
   cb.ax.tick_params(labelsize=16)
   fig2.savefig(f'{pathoutputfig}/map_{data}.climato-JJAS.{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
   plt.close(fig2)
     
   
   # N months averaged of one particular year
   mth_start=6 #6=june
   nb_total_mth=4
   mth_end=mth_start+nb_total_mth
   for year_target in [yearend, 2003, 2018]:
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      ax.add_feature(cfeature.LAND)
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} -  {year_target} mth start{mth_start} - mth end {mth_end}')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])
      plt.contourf(lon,lat,(np.average(var_mask[(year_target-yearbeg)*12+mth_start-1:(year_target-yearbeg)*12+mth_start-1+nb_total_mth,:,:],axis=0))/factor, cmap=color,extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", pad=0.1)
      cb.ax.tick_params(labelsize=16)
      fig2.savefig(f'{pathoutputfig}/map_{data}.{year_target}-mthstart{mth_start}.nbmth{nb_total_mth}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)
      
      # anomaly
      fig2 = plt.figure(figsize=(8,6))
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.coastlines()
      ax.add_feature(cfeature.LAND)
      gl = ax.gridlines(draw_labels = True,linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
      gl.top_labels = False
      gl.right_labels = False
      gl.xlabel_style = dict(fontsize=16)
      gl.ylabel_style = dict(fontsize=16)
      ax.set_xlabel('Longitude(°)')	
      ax.set_label('Latitude(°)')
      plt.title(f'{var_name} in {unit} - Anomalous mth start{mth_start} - mth end {mth_end} {year_target} (Climato {yearbeg}{yearend}) ')
      plt.axis([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot])
      cont=0
      indices=np.arange(mth_start-1, var_mask.shape[0], 12)
      for mth in range(1,nb_total_mth):
         arr = np.arange(mth_start+cont, var_mask.shape[0], 12)
         indices=np.concatenate((indices,arr))
         cont+=1
      var_indices=var_mask[indices,:,:]
      plt.contourf(lon,lat,( (np.average(var_mask[(year_target-yearbeg)*12+mth_start-1:(year_target-yearbeg)*12+mth_start-1+nb_total_mth,:,:],axis=0))  -  ( np.average(var_indices,axis=0))    )/factor, norm=TwoSlopeNorm(0), cmap=plt.cm.RdBu_r , extend='both')
      cb = plt.colorbar(ax=ax, orientation="horizontal", pad=0.1)
      cb.ax.tick_params(labelsize=16)
      fig2.savefig(f'{pathoutputfig}/map_{data}.{year_target}-mthstart{mth_start}.nbmth{nb_total_mth}.Anomaly{yearbeg}{yearend}.{format_fig}', format=f'{format_fig}')
      plt.close(fig2)

   ##############        
   # PLOT LATEX #
   ##############
if latex == "y":
   print('latex')
   if region=='20W45E-25N70N':
      trim_a = "10 45 25 36"
      scale="0.34"
   if region=='8W2E-43N51N':
      trim_a = "10 45 25 36"
      scale="0.34"
   else:
      trim_a = "30 55 55 75"
      scale="0.4"
   fileout = f'{pathoutputlatex}/map_mthAnomaly_{data}.pdf'
   filename = f'map_mthAnomaly_{data}'
   
   with open("tmp_mthano.tex", "w") as file:
      file.write(r'''
\documentclass[12pt]{article}
\usepackage[dvips]{graphicx}
\usepackage[dvipsnames]{xcolor}
\usepackage[utf8x]{inputenc}
\usepackage{color}
\usepackage{float}
\usepackage{hyperref}
\hypersetup{
    colorlinks,
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=black
}
%
\usepackage{geometry}
 \geometry{
 a4paper,
 total={170mm,257mm},
 left=5mm,
 top=5mm,
 }
%
\usepackage{fullpage}
\pagestyle{empty}

\usepackage{fancyvrb}
% redefine \VerbatimInput
\RecustomVerbatimCommand{\VerbatimInput}{VerbatimInput}%
{fontsize=\footnotesize,
 %
 frame=lines,  % top and bottom rule only
 framesep=2em, % separation between frame and text
 rulecolor=\color{Gray},
 %
 label=\fbox{\color{Black} SUMMARY},
 labelposition=topline,
 %
 commandchars=\|\(\), % escape character and argument delimiters for
                      % commands within the verbatim
 commentchar=*        % comment character
}

%
\begin{document}
%
\title{
Map of monthly anomaly \newline '''+data + r''' 
 }
\vspace{5cm}
\author{WORK DOCUMENT - Amélie Simon}
\maketitle
%\tableofcontents
%
\clearpage
%\thispagestyle{empty}
%\pagestyle{empty}
'''
)

   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_mth in range(1,7,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+ str(nb_mth) + r'''.clim'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+ str(nb_mth+6) + r'''.clim'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
         
   # JJAS and DJFM        
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1982,1988,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1988,1994,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1994,2000,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2000,2006,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2006,2012,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2012,2018,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2018,2023,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJAS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-DJFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
         
         
   # JJA and JFM        
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1982,1988,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1988,1994,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1994,2000,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2000,2006,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2006,2012,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2012,2018,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2018,2023,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJA.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JFM.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
         
   # JJ and AS      
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''      \clearpage \begin{figure}[p]''')
   for nb_yr in range(1982,1988,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1988,1994,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(1994,2000,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2000,2006,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2006,2012,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2012,2018,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   with open("tmp_mthano.tex", "a") as file:
      file.write(
r'''\begin{figure}[p]''')
   for nb_yr in range(2018,2023,1):
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-JJ.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-AS.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
   with open("tmp_mthano.tex", "a") as file:
      file.write(r'''
\end{figure} '''
         )
   
         
         
   for nb_yr in range(1982,2023):
      print(nb_yr)
      with open("tmp_mthano.tex", "a") as file:
         file.write(
r'''\begin{figure}[p]''')
      for nb_mth in range(1,7,1):
         with open("tmp_mthano.tex", "a") as file:
            file.write(r'''
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-''' + str(nb_mth) + r'''.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
\noindent\includegraphics[scale=''' + scale + r''', trim=''' + trim_a + r''', clip=true]{''' + pathoutputfig + r'''/map_''' + data+r'''.'''+str(nb_yr) + r'''-''' + str(nb_mth+6) + r'''.mthAnomaly'''+str(yearbeg)+str(yearend)+r'''.png}
            ''')
      with open("tmp_mthano.tex", "a") as file:
         file.write(r'''
\end{figure} '''
         )

   with open("tmp_mthano.tex", "a") as file:
      file.write(r''' 
%
\end{document}
'''
)

   if format_fig == 'eps':
      os.system("latex tmp_mthano.tex")
      os.system("dvipdf -R0 tmp_mthano.dvi " + fileout)
   
   if format_fig == 'png':
      os.system("pdflatex -jobname="+filename+" -output-directory="+pathoutputlatex+" tmp_mthano.tex ")
   print(f'{fileout}')


END = datetime.now()
DIFF = (END - START)
print(f'It took {int(DIFF.total_seconds() / 60)} minutes')

