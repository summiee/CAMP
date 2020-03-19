# CAMP endstation at FLASH

Clone repository
> git clone https://github.com/summiee/CAMP.git

Update repository (merge conflicts can occur)
> git pull 

Create conda environment from file
> conda env create -f CAMP.yml

Activate conda environment
> conda activate CAMP

Updata conda environment from file
> conda env update --name CAMP --file CAMP.yml

Update environment file
> conda env export > CAMP.yml

To run your code, you may need to add the top-level `/CAMP ` folder to the Python path with the command (best practice add the line to your .bashrc):
> export PYTHONPATH="$PYTHONPATH:/path/to/CAMP"
