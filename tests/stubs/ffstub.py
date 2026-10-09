"""A stand-in for ffmpeg and ffprobe (tests/tier2/conftest.py puts both names on PATH).

Media files are fake: text files of `key=value` lines (`frames=90`, `duration=3.0`,
`max_volume=-1.2`, `mean_volume=-20.0`, `silences=0-1.0,2.0-3.0`). Every call is appended as a
JSON line to FFSTUB_LOG. FFSTUB_FAIL names a job (`concat`, `mux`, `render`, `probe`, `volume`,
`silence`, `frame`) that exits 1 after writing a partial output; FFSTUB_DIE=render makes the
render stop reading stdin part-way. Nothing here is real ffmpeg output beyond its format.
"""

import json
import os
import struct
import sys
import zlib


def read_fake(path):
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    out[k] = v
    except OSError:
        pass
    return out


def write_fake(path, fields):
    with open(path, "w", encoding="utf-8") as f:
        for k, v in fields.items():
            f.write(f"{k}={v}\n")


def tiny_png(width=4, height=4, colour=(200, 40, 40)):
    """A real, minimal PNG of one colour, so the sheet can be pasted from stub frames."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + bytes(colour) * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def log(entry):
    with open(os.environ["FFSTUB_LOG"], "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def arg_after(args, flag, default=None):
    return args[args.index(flag) + 1] if flag in args else default


def fail_if(job, output=None):
    if os.environ.get("FFSTUB_FAIL") == job:
        if output:
            write_fake(output, {"partial": "yes"})
        sys.stderr.write(f"stub ffmpeg: {job} failed on purpose\n")
        sys.exit(1)


def ffprobe(args):
    path = args[-1]
    fake = read_fake(path)
    if not fake:
        sys.stderr.write(f"{path}: No such file or directory\n")
        return 1
    fail_if("probe")
    entries = arg_after(args, "-show_entries", "")
    if "nb_read_frames" in entries:
        print(json.dumps({"programs": [], "stream_groups": [],
                          "streams": [{"nb_read_frames": fake.get("frames", "0")}]}, indent=4))
    else:
        print(json.dumps({"programs": [], "stream_groups": [],
                          "streams": [{"index": 0, "codec_type": "video", "width": 1920, "height": 1080,
                                       "r_frame_rate": "30/1", "nb_frames": fake.get("frames", "0")},
                                      {"index": 1, "codec_type": "audio", "sample_rate": "48000", "channels": 1,
                                       "r_frame_rate": "0/0", "nb_frames": "1"}],
                          "format": {"duration": fake.get("duration", "0"), "size": str(os.path.getsize(path))}},
                         indent=4))
    return 0


def ffmpeg(args):
    output = args[-1]
    af = arg_after(args, "-af", "")
    if "-f" in args and arg_after(args, "-f") == "concat":
        inputs = []
        with open(arg_after(args, "-i"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("file "):
                    inputs.append(line.strip()[5:].strip("'"))
        fail_if("concat", output)
        frames = sum(int(read_fake(p).get("frames", 0)) for p in inputs)
        duration = sum(float(read_fake(p).get("duration", 0)) for p in inputs)
        write_fake(output, {"frames": frames, "duration": f"{duration:.6f}", "joined": len(inputs)})
        return 0
    if "-f" in args and arg_after(args, "-f") == "rawvideo":
        width, height = (int(v) for v in arg_after(args, "-s").split("x"))
        fail_if("render", output)
        frame_bytes = width * height * 4
        total = 0
        limit = frame_bytes * 2 if os.environ.get("FFSTUB_DIE") == "render" else None
        while True:
            chunk = sys.stdin.buffer.read(1 << 20)
            if not chunk:
                break
            total += len(chunk)
            if limit and total >= limit:
                sys.stderr.write("stub ffmpeg: died part-way on purpose\n")
                write_fake(output, {"frames": total // frame_bytes, "partial": "yes"})
                return 1
        fps = float(arg_after(args, "-r", "30"))
        write_fake(output, {"frames": total // frame_bytes, "duration": f"{total // frame_bytes / fps:.6f}",
                            "bytes": total})
        return 0
    if "volumedetect" in af:
        fail_if("volume")
        fake = read_fake(arg_after(args, "-i"))
        sys.stderr.write("[Parsed_volumedetect_0 @ 0x1] n_samples: 0\n")
        sys.stderr.write(f"[Parsed_volumedetect_0 @ 0x2] n_samples: 144000\n"
                         f"[Parsed_volumedetect_0 @ 0x2] mean_volume: {fake.get('mean_volume', '-20.0')} dB\n"
                         f"[Parsed_volumedetect_0 @ 0x2] max_volume: {fake.get('max_volume', '-1.0')} dB\n")
        return 0
    if "silencedetect" in af:
        fail_if("silence")
        fake = read_fake(arg_after(args, "-i"))
        for span in [s for s in fake.get("silences", "").split(",") if s]:
            a, b = span.split("-")
            sys.stderr.write(f"[Parsed_silencedetect_0 @ 0x1] silence_start: {a}\n")
            sys.stderr.write(f"[Parsed_silencedetect_0 @ 0x1] silence_end: {b} | silence_duration: {float(b) - float(a):.6f}\n")
        return 0
    if "-frames:v" in args:
        fail_if("frame", output)
        with open(output, "wb") as f:
            f.write(tiny_png())
        return 0
    if "-c:v" in args and arg_after(args, "-c:v") == "copy":
        fail_if("mux", output)
        inputs = [args[i + 1] for i, a in enumerate(args) if a == "-i"]
        fake = read_fake(inputs[0])
        fake["audio"] = os.path.basename(inputs[1])
        write_fake(output, fake)
        return 0
    sys.stderr.write(f"stub ffmpeg: unexpected arguments {args}\n")
    return 2


def main():
    name = os.environ.get("FFSTUB_NAME") or os.path.basename(sys.argv[0])
    args = sys.argv[1:]
    log({name: args})
    sys.exit(ffprobe(args) if name == "ffprobe" else ffmpeg(args))


if __name__ == "__main__":
    main()
