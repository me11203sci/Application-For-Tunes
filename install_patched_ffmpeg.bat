REM
REM Make sure that when this is executed while the aft enviroment is active.
@ echo off
set MAMBA_PATH=%CONDA_PREFIX%\Library\bin
echo "Downloading and unpacking patched ffmpeg..."
curl -s -L https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip -O
tar -xf ffmpeg-master-latest-win64-gpl.zip
echo "Installing patched ffmpeg..."
copy /Y ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe %MAMBA_PATH%
copy /Y  ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe %MAMBA_PATH%
del /Q ffmpeg-master-latest-win64-gpl.zip
rd /S /Q ffmpeg-master-latest-win64-gpl
echo "Done."
