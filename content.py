import os


def get_list_uploads():
    uploads_count = []
    for filename in os.listdir('uploads/'):
        uploads_count.append(filename)
    return uploads_count
