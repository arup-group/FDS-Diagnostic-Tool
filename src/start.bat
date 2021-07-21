push %~dp0
call activate fds_diagnostics
python main.py
call conda deactivate
popd