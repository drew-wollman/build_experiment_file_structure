del concatenated.wmv
(for %%i in (*.wmv) do @echo file '%%i') > list.txt

ffmpeg -f concat -safe 0 -i list.txt -c copy concatenated.wmv

pause