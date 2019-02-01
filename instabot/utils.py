import boto3
import os
import random
from collections import OrderedDict

from huepy import bold, green, orange

s3_client = boto3.client('s3')
INSTABOT_S3_BUCKET = os.getenv('INSTABOT_S3_BUCKET', '')


class file(object):
    def __init__(self, fname, verbose=True):
        self.fname = fname
        self.verbose = verbose
        open(self.fname, 'a').close()

    @property
    def list(self):
        with open(self.fname, 'r') as f:
            lines = [x.strip('\n') for x in f.readlines()]
            return [x for x in lines if x]

    @property
    def set(self):
        return set(self.list)

    def __iter__(self):
        for i in self.list:
            yield next(iter(i))

    def __len__(self):
        return len(self.list)

    def append(self, item, allow_duplicates=False):
        if self.verbose:
            msg = "Adding '{}' to `{}`.".format(item, self.fname)
            print(bold(green(msg)))

        if not allow_duplicates and str(item) in self.list:
            msg = "'{}' already in `{}`.".format(item, self.fname)
            print(bold(orange(msg)))
            return

        with open(self.fname, 'a') as f:
            f.write('{item}\n'.format(item=item))

    def remove(self, x):
        x = str(x)
        items = self.list
        if x in items:
            items.remove(x)
            msg = "Removing '{}' from `{}`.".format(x, self.fname)
            print(bold(green(msg)))
            self.save_list(items)

    def random(self):
        return random.choice(self.list)

    def remove_duplicates(self):
        return list(OrderedDict.fromkeys(self.list))

    def save_list(self, items):
        with open(self.fname, 'w') as f:
            for item in items:
                f.write('{item}\n'.format(item=item))


class s3_file(file):

    def __init__(self, fname, verbose=True):
        self.fname = fname
        self.verbose = verbose

    def get_file(self):
        return s3_client.get_object(
            Bucket=INSTABOT_S3_BUCKET, Key=self.fname
        )['Body']

    def write_file(self, content):
        s3_client.put_object(
            Bucket=INSTABOT_S3_BUCKET, Key=self.fname,
            Body=content
        )

    @property
    def list(self):
        lines = [x.strip('\n') for x in self.get_file().readlines()]
        return [x for x in lines if x]

    def append(self, item, allow_duplicates=False):
        if self.verbose:
            msg = "Adding '{}' to `{}`.".format(item, self.fname)
            print(bold(green(msg)))

        if not allow_duplicates and str(item) in self.list:
            msg = "'{}' already in `{}`.".format(item, self.fname)
            print(bold(orange(msg)))
            return

        file_content = self.get_file().read()
        new_content = file_content + '{item}\n'.format(item=item)
        self.write_file(new_content)

    def save_list(self, items):
        content = '\n'.join(items)
        self.write_file(content)
