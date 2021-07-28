#### **Requirements**
- conda 4.9 or higher (default Arup Shop Anaconda/Miniconda installation)

#### **FDS Compatible Versions**
Tested for FDS versions:
 - 6.1.2
 - 6.7.3

#### **How to install?**
1. Open console window in the downloaded repository folder.
2. Type `cd src`.
3. Type `conda env create -f requirements.yml`.
#### **How to use ?**
*Configure output*
1. Open `src\config.json` file.
2. Update "output_loc" field with pathway to a common folder where diagnostic result will be output (e.g "C:\\local_work\\digital_projects\\fds_diagnostics"). <br>
**Note: Do not forget enclosing "" and use \\\ instead of \\.** <br>
3. Update other config options - see documentation for more information.
4. Open `src\submit_sim.txt` and paste the file path to each simulation root folder. <br>
**Note: Paste the path as copied from Windows explorer. No need for enclosing "" and  for \\\ . <br>**
   To test the tool you can use any of the simulations saved in `fds_diagnostics\test_sims`. <br>
   
*Start  the tool* <br>

1. Double click on `src\start.bat` or type `start.bat` from src folder in the console.

_Example output_ <br>
See `fds_diagnostics\examples` for sample run of full output.