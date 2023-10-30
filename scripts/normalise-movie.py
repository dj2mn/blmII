#!/usr/bin/env python3

import os
import subprocess
import argparse
import pdb

def convert_movies(directory, remove_audio):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            # check if file is a movie file
            if filename.endswith(('.mov', '.mp4', '.avi')):
#            if filename.startswith(('2014')):
                scaling = False
                rotating = False

                print(filepath)
                # get resolution using ffprobe
                ffprobe_command = f'ffprobe -v 0 -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{filepath}"'
                output = subprocess.check_output(ffprobe_command, shell=True).decode('utf-8').strip().split('x')
                print(f'ffprobe dimensions = "{output}"')
#                if len(output) != 2:
#                    continue
                width = output[0]
                height = output[1]

                if (width >= '1920' and (width > height)) or (height >= '1920' and (height > width)):
                    scaling = True
                else:
                    scaling = False

                # check orientation
                ffprobe_command = f'ffprobe -hide_banner -v 0 -select_streams v:0 -show_entries stream_side_data=rotation -of compact=nk=1:p=0 "{filepath}"'
                output = subprocess.check_output(ffprobe_command, shell=True).decode('utf-8').strip()
                print(f'ffprobe rotation = {output}')
                if output:
                    match output:
                        case '-90':
                            tr = 'clock'
                            rotating = True
                        case '90':
                            tr = 'cclock'
                            rotating = True
                        case _:
                            tr = ''
                            rotating = False

                if rotating and scaling:
                    print("rotating and scaling")
                    filter_string = f'-vf transpose={tr},scale=1080:-1'
                elif rotating and not scaling:
                    print("rotating")
                    filtr_string = f'-vf transpose={tr}'
                elif scaling and not rotating:
                    print("scaling")
                    filter_string = f'-vf scale=1080:-1'
                else:
                    print("not filtering")
                    filter_string = ""

                output_filename = os.path.splitext(filename)[0] + '_converted.mp4'
                ffmpeg_command = f'ffmpeg -hide_banner -y -i "{filepath}" -an {filter_string} "{output_filename}"'
                print(ffmpeg_command)
                subprocess.call(ffmpeg_command, shell=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', nargs='?', default='.', help='directory to scan for movie files')
    parser.add_argument('-an', '--remove-audio', action='store_true', help='remove audio track')
    args = parser.parse_args()

    convert_movies(args.directory, args.remove_audio)
