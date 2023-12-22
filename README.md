# Application For Tunes

This script was written in order to aid in building my personal playlist.
It utilizes Spotify A.P.I. for metadata content and uses the Invidious A.P.I.
to provide the U.R.L. audio source(s). It uses the [yt-dlp](https://github.com/yt-dlp/yt-dlp) video downloader
and appends the corresponding metadata adhereing to the [ID3tag standard](https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.4.0-structure.html).

![](./media/demo_song_search.gif)

## Installing Dependencies

While there are many ways to skin the cat per say, we reccomend using
the [Mamba](https://github.com/mamba-org/mamba) project for quick and frictionless experience. After installing [miniforge](https://github.com/conda-forge/miniforge)
and opening Miniforge Prompt, begin by cloning the repository to your machine 
(assuming SSH, which you can set up by following [this](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) tutorial) and entering the resulting directory using:

```
git clone git@github.com:me11203sci/Application-For-Tunes.git 
cd Application-For-Tunes/
```

then use the included `enviroment.yaml` file to create the python enviroment using the following
command:

```
mamba env create --file enviroment.yaml 
```

Assuming there are no errors, then run:

```
mamba activate aft_dev
```

And you should be good to go!

## Usage

Ensure that the repository is cloned to your local machine, then proceed.

### Spotify Credentials

Before running the script, you need to provide valid Spotify application credentials in order
to make calls to the Spotify A.P.I.:
1. Begin by creating a Spotify Developer Account [here](https://developer.spotify.com/).
2. Once you have logged in, go to the [Developer Dashboard](https://developer.spotify.com/dashboard) and create a new application. Any link should work for the Redirect U.R.I., it is not important for our purposes. Be sure to select the tickbox labeled "Web API".
3. Wait a bit for your application to be approved. Once that happens, open the application settings. Here you should be able to see both your Client ID and a Client Secret.

Finally, create a `.env` file in the project repository structured as follows:

```
spotify_id=[REPLACE EVERYTING AFTER EQUAL SIGN WITH CLIENT ID]
spotify_secret=[REPLACE EVERYTING AFTER EQUAL SIGN WITH CLIENT SECRET]
```

### Running the Script

The script can be run with the following command:

```
python aft.py
```

#### Note for Windows Users

Some Windows Users may experience the following error:
![](./media/windows_error.png)

This is a known issue with an simple solution. You may notice the following output when running aft and passing it the optional help flag:

```{: .no-copy}
python aft.py -h
usage: aft.py [-h] [-d] [-p PATH]

Search for and download mp3 files and their corresponding metadata.

options:
  -h, --help            show this help message and exit
  -d, --downscale_image
                        Downscale album art to 480 x 480 for display on small 
                        devices.
  -p PATH, --ffmpeg-location PATH
                        For Windows Users. Allows for the passing of the path to 
                        the ffmpeg excutable.
```

If Windows fails to point the program to the proper ffmpeg executable, then open the folder
in which you installed mamba and make sure ffmpeg is in fact installed. If it is, then copy the 
path to . For example, assuming you installed miniforge:

```
python aft.py -p 'C:\Users\<windows_username>\miniforge\Library\bin\ffmpeg.exe'
```
