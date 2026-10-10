import hashlib
from app.services import sha256_file
def test_identical_contents_hash_same(tmp_path):
    a=tmp_path/"one.txt";b=tmp_path/"renamed.pdf";a.write_bytes(b"same");b.write_bytes(b"same")
    assert sha256_file(a)==sha256_file(b)==hashlib.sha256(b"same").hexdigest()
def test_different_contents_hash_different(tmp_path):
    a=tmp_path/"a.txt";b=tmp_path/"b.txt";a.write_bytes(b"one");b.write_bytes(b"two")
    assert sha256_file(a)!=sha256_file(b)
