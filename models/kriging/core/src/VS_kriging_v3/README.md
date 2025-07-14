# to compile in WSL2
. ~/intel/oneapi/setvars.sh
cd $path_to_dir
ifort -o ../out/main.exe ./Common_modules.F90 ./Common_geometry.F90 ./Eval_dailyET.F90 ./Eval_dailyT.f90 ./Kriging_algorithm.F90 ./Kriging_input.F90 ./Kriging_output.F90 ./Kriging_main.F90