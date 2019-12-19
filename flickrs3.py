import os
import webbrowser

import boto3
import flickrapi
import requests
import unidecode

# SETTABLE PARAMETERS
flickr_api_key = os.environ['FLICKR_KEY']
flickr_api_secret = os.environ['FLICKR_SECRET']
flickr_url = os.environ['FLICKR_URL']
bucket = os.environ['FLICKR_BUCKET']
s3_region = os.environ['S3_REGION']
storage_class = os.environ.get('S3_STORAGE_CLASS', 'STANDARD_IA')
if 'S3_PATH' in os.environ:
    s3_path = '{}/'.format(os.environ['S3_PATH'])
else:
    s3_path = ''


def addPhoto(photo, photoset=None):
    client = boto3.client('s3')
    url = flickr.photos_getSizes(photo_id = photo.attrib['id'])
    realUrl = None
    for url in url.find('sizes').findall('size'):
        if url.attrib['label'] == 'Original':
            realUrl = url.attrib['source']

    if realUrl:
        keyId = '{}{}.jpg'.format(s3_path, photo.attrib['id'])
        dataKeyId = '{}.metadata'.format(keyId)

        # Upload photo
        objects = client.list_objects(Bucket=bucket, Prefix=keyId)
        if 'Contents' not in objects or len(objects['Contents']) == 0:
            print('{} not found on S3; uploading'.format(keyId))
            response = requests.get(realUrl)
            assert response.status_code == 200

            print('Uploading "{}" to {}/{}'.format(photo.attrib['title'], bucket, keyId))
            metadata = {
                'flickrInfo': dataKeyId,
            }
            if photoset is not None:
                metadata['inFlickrSet'] = photoset.attrib['id']
                metadata['inFlickrSetTitle'] = unidecode.unidecode(photoset.find('title').text)
                if photoset.find('description').text is not None:
                    metadata['inFlickrSetDescription'] = unidecode.unidecode(photoset.find('description').text)
            client.put_object(Body=response.content, Bucket=bucket, Key=keyId, Metadata=metadata, StorageClass=storage_class)

        # Upload metadata
        objects = client.list_objects(Bucket=bucket, Prefix=dataKeyId)
        if 'Contents' not in objects or len(objects['Contents']) == 0:
            print('{} not found on S3, setting metadata'.format(dataKeyId))
            photoInfo = flickr.photos_getInfo(photo_id = photo.attrib['id'], format = 'rest')
            client.put_object(Body=photoInfo, Bucket=bucket, Key=dataKeyId, StorageClass=storage_class)


if __name__ == '__main__':
    print('Establishing S3 connection...')
    client = boto3.client('s3')
    buckets = client.list_buckets()

    if bucket not in [x['Name'] for x in buckets['Buckets']]:
        print('Bucket not found, creating...')
        create_bucket_configuration = {
            'LocationConstraint': s3_region,
        }
        response = client.create_bucket(Bucket=bucket, CreateBucketConfiguration=create_bucket_configuration)

    flickr = flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret)

    if not flickr.token_valid(perms='write'):
        flickr.get_request_token(oauth_callback='oob')

        authorize_url = flickr.auth_url(perms='write')
        webbrowser.open_new_tab(authorize_url)

        verifier = str(input('Verifier code: '))
        flickr.get_access_token(verifier)

    userIdResponse = flickr.urls_lookupUser(url = flickr_url)
    userId = userIdResponse.find('user').attrib['id']

    photosets = flickr.photosets_getList(user_id=userId).find('photosets')
    for photoset in photosets.findall('photoset'):
        print('Found set:', photoset.find('title').text)
        print('Fetching photos...')
        photos = flickr.photosets_getPhotos(photoset_id = photoset.attrib['id']).find('photoset')
        print(photos.attrib['total'], 'found')

        for photo in photos.findall('photo'):
            addPhoto(photo, photoset)

    # add photos out of sets
    print('Transferring photos outside of any set...')
    photos = flickr.photos_getNotInSet().find('photos')
    for photo in photos:
        addPhoto(photo)

