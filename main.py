'''software to download youtube video'''
import io
import threading
import cloudscraper
import PySimpleGUI as sg
from PIL import Image
from pytube import YouTube
from Load import convert_to_bytes


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


def completed(stream, path):

    splited = path.split( "/" )
    splited.pop()
    path = "/".join(splited)

    saves(path)
    print("completed")

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
                        size=(20, 20), key='progress',bar_color=['Green','Black'])],
        [sg.OK()]
    ]

    layout = [[sg.Text("YouTube Downloader")],
        [sg.Image(data=IM, key="-IMAGE-", size=(200, 200)),
         sg.VSeperator(),
         sg.Column(details),
         ],
        [
            sg.Text("Url "), sg.Input(
                "", key="URL"), sg.Button("Search")
        ],
        [
            sg.Text("Folder:"), sg.Input(
                key='-FOLDER-'), sg.FolderBrowse('Select')
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
                                 args=(target, values["-FOLDER-"], ),
                                 daemon=True).start()
            except Exception:
                window['title'].update(
                    value="Check resolution failed", text_color="Red"
                )
            continue
        if event == "update_progress":
            window["progress"].update(values[event])
            continue
        if event == "Search":
            try:
                if not values["URL"]:
                    raise Exception("URL undefined")

                youtube = YouTube(
                    values["URL"], on_progress_callback=progress, on_complete_callback=completed)
                window['title'].update(value=youtube.title, text_color="White")
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
            continue
        
    window.close()


def Download(target, path):
    target.download(path)

def saves(path):
    import json
    data = {
        "LINK": "https://www.youtube.com/watch?v=(index_video)",
        "PATH": path
    }
    
    with open("./SAVES/save.mmr", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    f.close()
    
def load():
    import json
    
    with open("./SAVES/save.mmr") as data_file:
        data_loaded = json.load(data_file)
        return data_loaded;
        
     
    
    
if __name__ == "__main__":
    main()
