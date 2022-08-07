'''software to download youtube video'''
import io
import PySimpleGUI as sg
from PIL import Image
from pytube import YouTube
import cloudscraper
from Load import convert_to_bytes
import threading

FILENAME = "./IMG/NoVideo.png"
window = None
IM = convert_to_bytes(FILENAME, (200, 200))


sg.theme('DarkGreen3')


def get_image_url(url):
    '''Takes in an url image, returns an Pil image'''
    jpg_data = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }).get(url).content

    pil_image = Image.open(io.BytesIO(jpg_data))
    png_bio = io.BytesIO()
    pil_image.thumbnail(size=(200, 200))
    pil_image.save(png_bio, format="PNG")

    png_data = png_bio.getvalue()

    return png_data


def get_options(yt_streams):
    '''Takes an array streams, returns an array of resolutions'''
    filtred = yt_streams.filter(progressive=True)
    res = []
    for stream in filtred:
        size = round(stream.filesize*1.192*10**(-7))
        res.append("{res} {size}MB {itag}"
                   .format(
                       res=stream.resolution, size=size, itag=stream.itag)
                   )
    return res


def progress(stream, data, bytes):

    percent = (stream.filesize - bytes) / stream.filesize * 100
    window.write_event_value('update_progress', percent)


def main():
    '''main function'''
    global window
    youtube = None
    itag = 2
    details = [
        [sg.Text(key="title", size=(35, 2))],
        [sg.Combo(values=[], key='res', size=(5, 8))],
        [sg.ProgressBar(max_value=100, orientation='h',
                        size=(20, 20), key='progress')],
        [sg.OK()]
    ]

    layout = [
        [sg.Image(data=IM, key="-IMAGE-", size=(200, 200)),
         sg.VSeperator(),
         sg.Column(details),
         ],
        [
            sg.Text("Url "), sg.Input(
                "https://www.youtube.com/watch?v=NRP4bOWoZpw", key="URL"), sg.Button("Search")
        ],
        [
            sg.Text("Default folder:"), sg.Input(
                key='-FOLDER-'), sg.FilesBrowse('Select')
        ]

    ]
    window = sg.Window("YouTube Downloader", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "OK":
            try:
                if not values["res"]:
                    raise Exception("resolution failed") 
                target = youtube.streams.get_by_itag(
                    values["res"].split(" ")[itag]
                )
                window["progress"].update(0)
                threading.Thread(target=Download,
                        args=(target, ),
                        daemon=True).start()
            except Exception:
                window['title'].update(
                        value="Check resolution failed", text_color="Red"
                    )
                
        if event == "update_progress":
            window["progress"].update(values[event])

        if event == "Search":
            try:
                if not values["URL"]:
                    raise Exception("URL undefined")
                
                youtube = YouTube(values["URL"], on_progress_callback=progress)
                window['title'].update(value=youtube.title,text_color="White")
                data = get_image_url(youtube.thumbnail_url)
                window["-IMAGE-"].update(data=data)
                window["res"].update(
                    values=get_options(
                        youtube.streams
                    )
                )
            except Exception:
                window['title'].update(
                    value="Error Search ...", text_color="Red")
                window["-IMAGE-"].update(data=IM)

    window.close()

def Download(target):
    target.download()

if __name__ == "__main__":
    main()
