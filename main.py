import sys
import hashlib

import zipfile

def main():
    unzip("s.zip","aaa")


def hash():
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(sys.argv[1], 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)

    print("MD5: {0}".format(md5.hexdigest()))
    print("SHA1: {0}".format(sha1.hexdigest()))


def unzip(unzip_file, to_dir):
    with zipfile.ZipFile(f'send_books/{unzip_file}') as existing_zip:
        existing_zip.extractall(f'temp/{to_dir}')

if __name__ == "__main__":
    main()