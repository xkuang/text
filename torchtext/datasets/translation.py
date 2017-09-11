import os
import tarfile
from six.moves import urllib


from .. import data


class TranslationDataset(data.Dataset):
    """Defines a dataset for machine translation."""

    @staticmethod
    def sort_key(ex):
        return data.interleave_keys(len(ex.src), len(ex.trg))

    def __init__(self, path, exts, fields, **kwargs):
        """Create a TranslationDataset given paths and fields.

        Arguments:
            path: Common prefix of paths to the data files for both languages.
            exts: A tuple containing the extension to path for each language.
            fields: A tuple containing the fields that will be used for data
                in each language.
            Remaining keyword arguments: Passed to the constructor of
                data.Dataset.
        """
        if not isinstance(fields[0], (tuple, list)):
            fields = [('src', fields[0]), ('trg', fields[1])]

        src_path, trg_path = tuple(os.path.expanduser(path + x) for x in exts)

        examples = []
        with open(src_path) as src_file, open(trg_path) as trg_file:
            for src_line, trg_line in zip(src_file, trg_file):
                src_line, trg_line = src_line.strip(), trg_line.strip()
                if src_line != '' and trg_line != '':
                    examples.append(data.Example.fromlist(
                        [src_line, trg_line], fields))

        super(TranslationDataset, self).__init__(examples, fields, **kwargs)


class Multi30k(TranslationDataset):
    """Defines a dataset for the multi-modal WMT 2017 task"""

    train_url = 'http://www.quest.dcs.shef.ac.uk/wmt16_files_mmt/training.tar.gz'
    val_url = 'http://www.quest.dcs.shef.ac.uk/wmt16_files_mmt/validation.tar.gz'
    test_url = 'https://staff.fnwi.uva.nl/d.elliott/wmt16/mmt16_task1_test.tgz'
    dirname = 'multi30k'

    @classmethod
    def download(cls, root):
        path = os.path.join(root, cls.dirname)
        if not os.path.isdir(path):
            os.makedirs(path)
        for url in [cls.train_url, cls.val_url, cls.test_url]:
            gz_name = os.path.basename(url)
            fpath = os.path.join(path, gz_name)
            if not os.path.isfile(fpath):
                print('downloading {}'.format(gz_name))
                urllib.request.urlretrieve(url, fpath)
            with tarfile.open(fpath, 'r:gz') as tar:
                dirs = [member for member in tar.getmembers()]
                tar.extractall(path=path, members=dirs)
        return os.path.join(path, '')

    @classmethod
    def splits(cls, exts, fields, root='.',
               train='train', val='val', test='test', **kwargs):
        """Create dataset objects for splits of the Multi30k dataset.

        Arguments:

            root: directory containing Multi30k data
            exts: A tuple containing the extension to path for each language.
            fields: A tuple containing the fields that will be used for data
                in each language.
            train: The prefix of the train data. Default: 'train'.
            validation: The prefix of the validation data. Default: 'val'.
            test: The prefix of the test data. Default: 'test'.
            Remaining keyword arguments: Passed to the splits method of
                Dataset.
        """
        path = cls.download(root)

        train_data = None if train is None else cls(
            os.path.join(path, train), exts, fields, **kwargs)
        val_data = None if val is None else cls(
            os.path.join(path, val), exts, fields, **kwargs)
        test_data = None if test is None else cls(
            os.path.join(path, test), exts, fields, **kwargs)
        return tuple(d for d in (train_data, val_data, test_data)
                     if d is not None)
