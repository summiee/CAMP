# CAMP endstation at FLASH

Jupyter notebooks to work with the Python DOOCS API (pydoocs).

* Save ADC traces to disk 
* Save images traces to diskydoocs)

If necessary add conda channels
> conda config --add channels http://doocspkgs.desy.de/pub/doocsconda/
> conda config --add channels http://www.desy.de/~wwwuser/flashconda

Clone repository
> git clone https://github.com/summiee/CAMP.git

Create and activate conda environment
> conda create --name flash --file requirements.txt
> conda activate flash

Interactive Jupyter notebooks to be rendered with [Voila](https://github.com/voila-dashboards/voila).

* Time-of-Flight Mass calibration (online via pydoocs)

> voila ToF_calibration.ipynb

