"""Black-box measurement of plugins you own, on your machine.

Nothing here inspects, decompiles or copies a plugin. It renders test signals through a plugin
you have licensed and characterises the OUTPUT, which is ordinary measurement of software you own
and is how competitive DSP is actually built. The result is a behavioural spec you can implement
against from first principles.

    pip install pedalboard numpy scipy matplotlib

    python measure.py --list
    python measure.py --plugin "C:/Program Files/Common Files/VST3/True Iron.vst3" \
                      --tests alias,harmonics,response --out ../measurements/true-iron

Tests
  alias      7 kHz tone under drive -> is there energy where only fold-back could put it
  harmonics  1 kHz tone at several input levels -> H2..H10 profile vs level
  response   exponential sweep -> magnitude and phase (Farina deconvolution)
  curve      slow level ramp -> static input/output transfer (compressors, clippers)
  envelope   tone burst -> attack and release envelope (compressors)
  rt60       impulse -> octave-band RT60 and early/late energy split (reverbs)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

FS = 48000


# ----------------------------------------------------------------------------- signals
def sine(f, secs, amp_db=-6.0, fs=FS):
    t = np.arange(int(secs * fs)) / fs
    return (10 ** (amp_db / 20.0) * np.sin(2 * np.pi * f * t)).astype(np.float32)


def exp_sweep(f1=20.0, f2=20000.0, secs=5.0, amp_db=-12.0, fs=FS):
    """Farina exponential sweep plus its matched inverse filter."""
    n = int(secs * fs)
    t = np.arange(n) / fs
    k = np.log(f2 / f1)
    x = np.sin(2 * np.pi * f1 * secs / k * (np.exp(t * k / secs) - 1.0))
    # inverse: time-reversed sweep with a -6 dB/oct amplitude envelope
    inv = x[::-1] * np.exp(-t * k / secs)
    amp = 10 ** (amp_db / 20.0)
    return (amp * x).astype(np.float32), inv.astype(np.float32)


def level_ramp(secs=12.0, lo_db=-60.0, hi_db=0.0, f=1000.0, fs=FS):
    n = int(secs * fs)
    t = np.arange(n) / fs
    env = 10 ** (np.linspace(lo_db, hi_db, n) / 20.0)
    return (env * np.sin(2 * np.pi * f * t)).astype(np.float32), env


def burst(on=0.5, off=1.5, f=1000.0, amp_db=-3.0, quiet_db=-40.0, fs=FS):
    """Quiet -> loud -> quiet. Attack is measured on the step up, release on the step down."""
    q = 10 ** (quiet_db / 20.0)
    a = 10 ** (amp_db / 20.0)
    n_on, n_off = int(on * fs), int(off * fs)
    t = np.arange(n_off + n_on + n_off) / fs
    car = np.sin(2 * np.pi * f * t)
    env = np.concatenate([np.full(n_off, q), np.full(n_on, a), np.full(n_off, q)])
    return (car * env).astype(np.float32), env.astype(np.float32), n_off


def impulse(secs=8.0, fs=FS):
    x = np.zeros(int(secs * fs), dtype=np.float32)
    x[0] = 1.0
    return x


# ----------------------------------------------------------------------------- analysis
def spectrum(x, fs=FS):
    w = np.hanning(len(x))
    X = np.fft.rfft(x * w)
    mag = np.abs(X) / (np.sum(w) / 2.0)
    return np.fft.rfftfreq(len(x), 1 / fs), mag


def db(v, floor=1e-12):
    return 20 * np.log10(np.maximum(np.abs(v), floor))


def peak_near(freqs, mag, f0, tol_hz=25.0):
    m = (freqs > f0 - tol_hz) & (freqs < f0 + tol_hz)
    return float(mag[m].max()) if m.any() else 0.0


def alias_report(y, f0, fs=FS):
    """Energy that can only be fold-back: bins that are not near any true harmonic."""
    # analyse the steady middle of the render
    seg = y[int(0.25 * len(y)):int(0.85 * len(y))]
    freqs, mag = spectrum(seg, fs)
    nyq = fs / 2
    true_h = [f0 * k for k in range(1, int(nyq // f0) + 1)]
    # predicted fold locations for harmonics above nyquist
    folded = []
    k = int(nyq // f0) + 1
    while f0 * k < 12 * f0:
        f = f0 * k
        img = abs(f - fs * round(f / fs))
        if 20 < img < nyq:
            folded.append((k, img))
        k += 1
    fund = peak_near(freqs, mag, f0)
    mask = np.zeros_like(freqs, dtype=bool)
    for f in true_h:
        mask |= (freqs > f - 30) & (freqs < f + 30)
    mask |= freqs < 20
    inharmonic = float(np.sqrt(np.sum(mag[~mask] ** 2)))
    return {
        "fundamental_hz": f0,
        "fundamental_db": round(db(fund), 2),
        "inharmonic_energy_db_rel_fund": round(db(inharmonic / max(fund, 1e-12)), 2),
        "predicted_fold_bins": [
            {"harmonic": k, "folds_to_hz": round(img, 1),
             "measured_db_rel_fund": round(db(peak_near(freqs, mag, img) / max(fund, 1e-12)), 2)}
            for k, img in folded[:8]
        ],
        "verdict": ("clean" if db(inharmonic / max(fund, 1e-12)) < -70 else
                    "some aliasing" if db(inharmonic / max(fund, 1e-12)) < -45 else
                    "heavy aliasing"),
    }


def harmonic_profile(y, f0, fs=FS, n=10):
    seg = y[int(0.25 * len(y)):int(0.85 * len(y))]
    freqs, mag = spectrum(seg, fs)
    fund = peak_near(freqs, mag, f0)
    out = {}
    for k in range(2, n + 1):
        f = f0 * k
        if f >= fs / 2:
            break
        out[f"H{k}"] = round(db(peak_near(freqs, mag, f) / max(fund, 1e-12)), 2)
    even = [10 ** (out[k] / 20) for k in out if int(k[1:]) % 2 == 0]
    odd = [10 ** (out[k] / 20) for k in out if int(k[1:]) % 2 == 1]
    thd = np.sqrt(sum(10 ** (v / 10) for v in out.values()))
    return {
        "harmonics_db_rel_fund": out,
        "thd_percent": round(100 * float(thd), 4),
        "even_over_odd_db": round(db(np.sqrt(sum(np.square(even))) /
                                     max(np.sqrt(sum(np.square(odd))), 1e-12)), 2) if odd else None,
        "character": None,  # filled by caller commentary
    }


def deconvolve(y, inv, fs=FS):
    ir = np.convolve(y, inv, mode="full")
    ir = ir[np.argmax(np.abs(ir)) :]
    ir = ir[: int(2.0 * fs)]
    n = 1 << int(np.ceil(np.log2(len(ir))))
    H = np.fft.rfft(ir, n)
    f = np.fft.rfftfreq(n, 1 / fs)
    return ir, f, np.abs(H), np.unwrap(np.angle(H))


def rt60_octaves(ir, fs=FS):
    from scipy.signal import butter, sosfiltfilt
    out = {}
    for fc in [63, 125, 250, 500, 1000, 2000, 4000, 8000]:
        lo, hi = fc / np.sqrt(2), fc * np.sqrt(2)
        if hi >= fs / 2:
            continue
        sos = butter(4, [lo / (fs / 2), min(hi / (fs / 2), 0.999)], btype="band", output="sos")
        b = sosfiltfilt(sos, ir)
        # Schroeder backward integration
        e = np.cumsum(b[::-1] ** 2)[::-1]
        e = e / max(e[0], 1e-20)
        L = 10 * np.log10(np.maximum(e, 1e-20))
        try:  # fit -5 .. -25 dB and extrapolate to -60
            i1 = int(np.argmax(L < -5))
            i2 = int(np.argmax(L < -25))
            if i2 > i1 > 0:
                sl = np.polyfit(np.arange(i1, i2) / fs, L[i1:i2], 1)[0]
                out[f"{fc}Hz"] = round(float(-60.0 / sl), 3) if sl < 0 else None
            else:
                out[f"{fc}Hz"] = None
        except Exception:
            out[f"{fc}Hz"] = None
    return out


# ----------------------------------------------------------------------------- runner
def render(plugin, x, fs=FS):
    buf = np.stack([x, x]) if x.ndim == 1 else x
    y = plugin(buf, fs)
    return np.asarray(y)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugin")
    ap.add_argument("--tests", default="alias,harmonics,response")
    ap.add_argument("--out", default="../measurements/out")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fs", type=int, default=FS)
    a = ap.parse_args()

    try:
        from pedalboard import load_plugin
    except ImportError:
        print("pedalboard is required:  pip install pedalboard numpy scipy matplotlib")
        return 1

    if a.list:
        roots = [r"C:\Program Files\Common Files\VST3",
                 r"C:\Program Files\Steinberg\VSTPlugins",
                 r"C:\Program Files\VSTPlugins"]
        for r in roots:
            for dp, _, fns in os.walk(r):
                for fn in fns:
                    if fn.endswith(".vst3") or fn.endswith(".dll"):
                        print(os.path.join(dp, fn))
        return 0

    if not a.plugin:
        print("need --plugin (or --list)")
        return 1

    fs = a.fs
    os.makedirs(a.out, exist_ok=True)
    plug = load_plugin(a.plugin)
    name = os.path.splitext(os.path.basename(a.plugin))[0]
    report = {"plugin": name, "path": a.plugin, "fs": fs,
              "parameters": {k: str(v) for k, v in list(plug.parameters.items())[:60]}}

    tests = [t.strip() for t in a.tests.split(",")]

    if "alias" in tests:
        report["alias"] = {}
        for drive_db in (-12.0, -6.0, -1.0):
            y = render(plug, sine(7000, 2.0, drive_db, fs), fs)
            report["alias"][f"in_{drive_db}dB"] = alias_report(y, 7000, fs)

    if "harmonics" in tests:
        report["harmonics"] = {}
        for lvl in (-30.0, -24.0, -18.0, -12.0, -6.0, -3.0, -1.0):
            y = render(plug, sine(1000, 2.0, lvl, fs), fs)
            report["harmonics"][f"in_{lvl}dB"] = harmonic_profile(y, 1000, fs)

    if "response" in tests:
        x, inv = exp_sweep(fs=fs)
        y = render(plug, x, fs)
        ir, f, mag, ph = deconvolve(y, inv, fs)
        keep = (f > 15) & (f < fs / 2 * 0.98)
        idx = np.unique(np.geomspace(1, keep.sum() - 1, 512).astype(int))
        report["response"] = {
            "freq_hz": [round(float(v), 2) for v in f[keep][idx]],
            "mag_db": [round(float(v), 3) for v in db(mag[keep][idx] / max(mag[keep].max(), 1e-12))],
            "phase_rad": [round(float(v), 4) for v in ph[keep][idx]],
        }
        np.save(os.path.join(a.out, f"{name}_ir.npy"), ir)

    if "curve" in tests:
        x, env = level_ramp(fs=fs)
        y = render(plug, x, fs)
        win = int(0.02 * fs)
        n = len(y) // win
        i_db, o_db = [], []
        for k in range(n):
            s = slice(k * win, (k + 1) * win)
            i_db.append(round(float(db(np.sqrt(np.mean(x[s] ** 2)) * np.sqrt(2))), 3))
            o_db.append(round(float(db(np.sqrt(np.mean(y[s] ** 2)) * np.sqrt(2))), 3))
        report["curve"] = {"in_db": i_db, "out_db": o_db}

    if "envelope" in tests:
        x, env, n_off = burst(fs=fs)
        y = render(plug, x, fs)
        win = int(0.001 * fs)
        g = []
        for k in range(len(y) // win):
            s = slice(k * win, (k + 1) * win)
            xi = np.sqrt(np.mean(x[s] ** 2))
            yi = np.sqrt(np.mean(y[s] ** 2))
            g.append(round(float(db(yi / max(xi, 1e-12))), 3))
        report["envelope"] = {"ms_per_step": 1.0, "gain_db": g,
                              "step_up_at_ms": n_off / fs * 1000}

    if "rt60" in tests:
        y = render(plug, impulse(fs=fs), fs)
        report["rt60"] = rt60_octaves(y, fs)
        e = y ** 2
        cut = int(0.08 * fs)
        report["early_late"] = {
            "early_0_80ms_frac": round(float(np.sum(e[:cut]) / max(np.sum(e), 1e-20)), 4)
        }
        np.save(os.path.join(a.out, f"{name}_reverb_ir.npy"), y)

    p = os.path.join(a.out, f"{name}.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    print(f"wrote {p}")
    for t in tests:
        if t == "alias" and "alias" in report:
            for k, v in report["alias"].items():
                print(f"  alias {k}: {v['verdict']} ({v['inharmonic_energy_db_rel_fund']} dB rel fund)")
        if t == "rt60" and "rt60" in report:
            print("  rt60:", report["rt60"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
