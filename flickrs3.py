import flickrapi
import urllib
from boto.s3.key import Key
from boto.s3 import Connection
import os
import sys

# SETTABLE PARAMETERS
flickr_api_key = os.environ['FLICKR_KEY']
flickr_api_secret = os.environ['FLICKR_SECRET']

s3_access_key = os.environ['S3_KEY']
s3_secret_key = os.environ['S3_SECRET']
bucket = os.environ['FLICKR_BUCKET']
flickr_url = os.environ['FLICKR_URL']

class LineOutput:
    last = 0
    out = sys.stdout

    def _message(self, msg):
        if self.out.isatty():
            self.out.write("\r")
            self.out.write(msg)
            if len(msg) < self.last:
                i = self.last - len(msg)
                self.out.write(" " * i + "\b" * i)
            self.out.flush()
            self.lastMessage = msg
            self.last = len(msg)

    def __del__(self):
        if self.last:
            self._message("")
            print >> self.out, "\r",
            self.out.flush()

    def __init__(self, f = sys.stdout):
        self.last = 0
        self.lastMessage = ''
        self.out = f

def makeBotoCallback():
    c = LineOutput()
    def callbackFunc(sent, total):
        c._message("Uploading: %.2f%% (%d/%d)\r" % ((float(sent)/float(total))*100.0, sent, total))

    return callbackFunc
    
def makeFlickrCallback():
    c = LineOutput()
    def callbackFunc(blocks, blockSize, total):
        sent = blocks * blockSize
        c._message("Downloading: %.2f%% (%d/%d)\r" % ((float(sent)/float(total))*100.0, sent, total))

    return callbackFunc

def addPhoto(photo):
    url = flickr.photos_getSizes(photo_id = photo.attrib['id'])
    realUrl = None
    for url in url.find('sizes').findall('size'):
        if url.attrib['label'] == "Original":
            realUrl = url.attrib['source']

    if realUrl:
        keyId = photo.attrib['id'] + ".jpg"
        dataKeyId = keyId + ".metadata"

        # Upload photo
        if bucket.get_key(keyId) is None:
            print "%s not found on S3; uploading" % keyId
            f, h = urllib.urlretrieve(realUrl, reporthook = makeFlickrCallback())
            key = Key(bucket)
            key.key = keyId


            print "Uploading %s to %s/%s" % (photo.attrib['title'], bucket.name, key.key)
            key.set_metadata('flickrInfo', key.key + ".metadata")
            key.set_metadata('inFlickrSet', set.attrib['id'])
            key.set_contents_from_filename(f, cb = makeBotoCallback())
            os.unlink(f)

        # Upload metadata
        if bucket.get_key(dataKeyId) is None:
            print "%s not found on S3, setting metadata" % dataKeyId
            photoInfo = flickr.photos_getInfo(photo_id = photo.attrib['id'], format = "rest")
            key = Key(bucket)
            key.key = dataKeyId
            key.set_contents_from_string(photoInfo) 

print "Establishing S3 connection..."
s3conn = Connection(s3_access_key, s3_secret_key)
buckets = s3conn.get_all_buckets()
if bucket not in [x.name for x in buckets]:
    print "Bucket not found, creating..."
    s3conn.create_bucket(bucket)
bucket = s3conn.get_bucket(bucket)

flickr = flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret)

(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

userIdResponse = flickr.urls_lookupUser(url = flickr_url)
userId = userIdResponse.find('user').attrib['id']

sets = flickr.photosets_getList(user_id=userId).find('photosets')
for set in sets.findall('photoset'):
    print "Found set: ", set.find("title").text
    print "Fetching photos...",
    photos = flickr.photosets_getPhotos(photoset_id = set.attrib['id']).find('photoset')
    print photos.attrib['total'], "found"

    for photo in photos.findall('photo'):
        addPhoto(photo)

# add photos out of sets
print "Transferring photos outside of any set..."
photos = flickr.photos_getNotInSet().find('photos')
for photo in photos:
    addPhoto(photo)

