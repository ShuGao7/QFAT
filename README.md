# QFAT
Overview
The Quantitative Flood Analysis Tool(QFAT) can be utilized to directly read data files produced by an ADvanced CIRCulation model (ADCIRC) storm surge simulation. It can also be used to compute various flood quantities, such as average water surface elevation, average inundation depth, average inundation time, total inundated area, total surge volume, and percent of land inundated for a given area.

Prerequisites
The executable program is a 64 bit Python-based ArcGIS tool. The following products are required to run this program: 
1.	ArcGIS for Desktop. 
ArcGIS for Desktop requires Microsoft .NET Framework Version 3.5 SP1. If .NET Framework 3.5 SP1 is not detected on the installer’s workstation, the ArcGIS for Desktop setup will not proceed.
2.	Python 2.7 (64 bit)
ArcGIS for Desktop geoprocessing tools and the QFAT tools require that Python 2.7.8 be previously installed on the workstation. 
3.	ArcGIS Background Geoprocessing (64 bit)
If you have installed the 64 bit ArcGIS, there should be an “ArcGISx6410.3” folder under “C:\Python27”. If not, the Background Geoprocessing (64 bit) must be installed. This is available as a separate installation in addition to ArcGIS for Desktop. Using ArcGIS 10.3 as an example, the installation file name is “ArcGIS_BackgroundGP_for_Desktop_103.exe”. 
4.	Add path file
Open the “site-package” folder in the “dist” folder. There is a “Desktop10.3_64bit.pth” file under the “site-packages” folder. Open the .pth file using notepad. If your ArcGIS and Python paths are different from the paths in the “Desktop10.3_64bit.pth” file, please change the paths.

Cite the code: [![DOI](https://zenodo.org/badge/287140431.svg)](https://zenodo.org/badge/latestdoi/287140431)
