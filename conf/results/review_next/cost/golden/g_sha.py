"""golden helper: streaming sha256 of the given files (symlinks resolved) -> 'sha256  size  realpath  path'."""
import hashlib, os, sys
for p in sys.argv[1:]:
    rp = os.path.realpath(p)
    h = hashlib.sha256()
    with open(rp, "rb") as f:
        for blk in iter(lambda: f.read(1 << 24), b""):
            h.update(blk)
    print(h.hexdigest(), os.path.getsize(rp), rp, p, flush=True)
