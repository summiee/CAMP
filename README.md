# CAMP endstation at FLASH

Clone repository
> git clone https://github.com/summiee/CAMP.git

Create and activate conda environment
> conda env create -f CAMP.yml

> conda activate CAMP

Update environment.yml
> conda env export > CAMP.yml

To run your code, you may need to add the top-level `/CAMP ` folder to the Python path with the comand:
> export PYTHONPATH="$PYTHONPATH:/path/to/CAMP"