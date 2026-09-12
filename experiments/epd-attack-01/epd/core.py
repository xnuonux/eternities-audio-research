"""EPD Attack 01: bounded offline research processors, not validated perceptual models.

All processors use entire clips (noncausal) and allocate memory. NOT a real-time
callback implementation. A neutral setting returns an exact copy of the input.
No model score is interpreted as a human percept or a probability of one.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import signal, optimize
import pyloudnorm as pyln

VERSION = '0.0.1-research'


def audio_array(x, fs: int) -> np.ndarray:
    if np.iscomplexobj(x): raise ValueError("Complex-valued audio is unsupported.")
    a = np.asarray(x, dtype=np.float64)
    if not isinstance(fs, (int, np.integer)) or not 8000 <= fs <= 192000:
        raise ValueError('Sample rate must be an integer in [8000, 192000].')
    if a.ndim not in (1, 2) or len(a) < 64 or (a.ndim == 2 and a.shape[1] not in (1, 2)):
        raise ValueError('Expected at least 64 samples, mono or stereo (samples, channels).')
    if not np.all(np.isfinite(a)) or np.max(np.abs(a)) > 64:
        raise ValueError('Audio is nonfinite or exceeds the research limit of 64 full scale.')
    return a


def bounded(value: float, low: float, high: float, name='parameter') -> float:
    value = float(value)
    if not np.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} must be finite and in [{low}, {high}].')
    return value


def rms(x) -> float:
    return float(np.sqrt(np.mean(np.square(x))))


def db(x: float) -> float:
    return float(20 * np.log10(max(float(x), 1e-15)))


def peak16(x) -> float:
    """Independent 16x windowed-sinc reconstruction estimate, NOT a certified meter."""
    return float(np.max(np.abs(signal.resample_poly(x, 16, 1, axis=0,
                               window=('kaiser', 12.0)))))


def lufs(x, fs: int) -> float:
    if len(x) < int(.4 * fs) or rms(x) < 1e-14:
        return float('-inf')
    return float(pyln.Meter(fs).integrated_loudness(x))


def normalize_group(clips: list[np.ndarray], fs: int, target=-23.0, ceiling=-3.0):
    """One level target per comparison family; lower EVERY clip if headroom requires.
    No limiting/clipping, no separate peak normalization. Equal LUFS does not imply
    equal subjective loudness. Silent stimuli are forbidden in these comparisons.
    """
    levels = [lufs(c, fs) for c in clips]
    if not np.all(np.isfinite(levels)):
        raise ValueError('Comparison stimuli must have measurable nonzero loudness.')
    normalized = [c * 10 ** ((target - lv) / 20) for c, lv in zip(clips, levels)]
    highest = max(db(peak16(c)) for c in normalized)
    target -= max(0.0, highest - ceiling + .02)
    return [c * 10 ** ((target - lv) / 20) for c, lv in zip(clips, levels)], target


def fade(x, fs, seconds=.035):
    y = np.array(x, copy=True)
    n = min(int(fs * seconds), len(y)//2)
    if n > 0:
        f = np.sin(np.linspace(0, np.pi/2, n))**2
        y[:n] *= f if y.ndim == 1 else f[:, None]
        y[-n:] *= f[::-1] if y.ndim == 1 else f[::-1, None]
    return y


def spectrum_parts(x, fs, bands=8):
    """Smooth log-spaced FFT partition of unity. Perfect sum before modification.
    Circular/offline filtering; use fades for finite experiment clips. Not a
    gammatone cochlea or a source separator. Bands are NOT auditory objects.
    """
    x = audio_array(x, fs)
    if not isinstance(bands, int) or not 2 <= bands <= 32:
        raise ValueError('bands must be an integer between 2 and 32')
    mono = x.ndim == 1
    a = x[:, None] if mono else x
    f = np.fft.rfftfreq(len(a), 1/fs)
    centers = np.geomspace(90, min(fs*.42, 12000), bands)
    lf = np.log(np.maximum(f, 1))
    lc = np.log(centers)
    w = np.zeros((bands, len(f)))
    for j in range(bands):
        if j == 0: w[j, lf <= lc[0]] = 1
        if j == bands-1: w[j, lf >= lc[-1]] = 1
        if j > 0:
            m = (lf >= lc[j-1]) & (lf < lc[j])
            w[j, m] = np.sin(.5*np.pi*(lf[m]-lc[j-1])/(lc[j]-lc[j-1]))**2
        if j < bands-1:
            m = (lf >= lc[j]) & (lf < lc[j+1])
            w[j, m] = np.cos(.5*np.pi*(lf[m]-lc[j])/(lc[j+1]-lc[j]))**2
    parts = np.fft.irfft(w[:, :, None] * np.fft.rfft(a, axis=0)[None], n=len(a), axis=1)
    return parts[:, :, 0] if mono else parts


def envelopes(parts, fs, cut=18.0):
    a = np.abs(signal.hilbert(parts, axis=1))
    if parts.ndim == 3: a = np.sqrt(np.mean(a*a, axis=2))
    sos = signal.butter(2, cut, fs=fs, output='sos')
    return np.maximum(signal.sosfiltfilt(sos, a, axis=1), 1e-12)


def coherence(env) -> float:
    """Mean envelope Pearson correlation; diagnostic, never a source-count score."""
    energy = np.mean(env*env, axis=1)
    valid = (np.std(env, axis=1) > 1e-10) & (energy > max(float(np.max(energy))*1e-6, 1e-24))
    if np.sum(valid) < 2: return 0.0
    c = np.corrcoef(env[valid])
    return float(np.mean(c[np.triu_indices(len(c), 1)]))


def bind(x, fs: int, coupling: float = .7, max_change_db: float = 6, bands: int = 8):
    """BIND-CF: reshape intrinsic cross-band amplitude co-movement.
    Positive coupling replaces standardized log-envelope movement by the mean.
    Negative coupling removes its projection (when residual structure exists).
    Per-band variance is rescaled; gains are bounded. No pitch or spatial change
    is requested, but perceptual pitch/tone/width are NOT guaranteed invariant.
    This is an AM cue manipulator, not validated 'objecthood control'.
    """
    x = audio_array(x, fs); c = bounded(coupling, -1, 1, 'coupling')
    lim = bounded(max_change_db, 0, 18, 'max_change_db')
    if c == 0 or lim == 0 or rms(x) < 1e-14: return x.copy()
    p = spectrum_parts(x, fs, bands)
    env = envelopes(p, fs)
    floor = np.max(env, axis=1, keepdims=True)*.01 + 1e-12
    le = np.log(np.maximum(env, floor))
    mu = np.mean(le, axis=1, keepdims=True)
    sd = np.std(le, axis=1, keepdims=True)
    z = (le-mu)/np.maximum(sd, 1e-6)
    active = (np.mean(env*env, axis=1) > np.max(np.mean(env*env,axis=1))*1e-5)
    common = np.mean(z[active], axis=0)
    common /= max(float(np.std(common)), 1e-6)
    if c > 0:
        dest = (1-c)*z + c*common
    else:
        projection = np.mean(z * common, axis=1, keepdims=True)
        dest = z - (-c)*projection*common
    dest -= np.mean(dest, axis=1, keepdims=True)
    ds = np.std(dest, axis=1, keepdims=True)
    dest = np.where(ds > .025, dest/np.maximum(ds, 1e-6), z)
    gain_log = np.clip(mu + sd*dest - le, -lim*np.log(10)/20, lim*np.log(10)/20)
    gain_log[~active] = 0
    # Do not fill intentional silence or near-silent tails.
    gate = np.minimum(1.0, env/(floor*2))
    g = np.exp(gain_log*gate)
    y = np.sum(p*(g if p.ndim == 2 else g[:, :, None]), axis=0)
    return y


def continuum(x, fs: int, amount: float = .7, focus_hz=8, max_change_db=9, bands=8):
    """CONTINUUM-EC: reduce within-band event contrast, preserve slow envelope.
    Blend log envelopes toward a slow (focus_hz) trend, with linked stereo gains.
    No grains/events are added, no sample timeline is reordered. This is a
    bounded modulation-envelope compressor, not retrieval of hidden events.
    Baseline: broadband version of the SAME operation; compare before inventing
    a new category. It can change tone, transient audibility and apparent rhythm.
    """
    if not isinstance(bands, int) or not 1 <= bands <= 32: raise ValueError('bands must be 1..32')
    x = audio_array(x, fs); a = bounded(amount, 0, 1, 'amount')
    fc = bounded(focus_hz, .5, 30, 'focus_hz')
    lim = bounded(max_change_db, 0, 18, 'max_change_db')
    if a == 0 or lim == 0 or rms(x) < 1e-14: return x.copy()
    p = spectrum_parts(x, fs, bands) if bands > 1 else x[None]
    e = envelopes(p, fs, cut=100)
    floor = np.max(e, axis=1, keepdims=True)*.008 + 1e-12
    le = np.log(np.maximum(e, floor))
    slow = signal.sosfiltfilt(signal.butter(2, fc, fs=fs, output='sos'), le, axis=1)
    g = np.exp(np.clip(a*(slow-le), -lim*np.log(10)/20, lim*np.log(10)/20))
    # Keep silent inputs exactly silent; never create new carrier/noise.
    return np.sum(p*(g if p.ndim == 2 else g[:, :, None]), axis=0)


@dataclass
class ModalModel:
    frequencies: np.ndarray
    decay_seconds: np.ndarray
    sin_weights: np.ndarray
    cos_weights: np.ndarray
    fit_relative_error: float = float('nan')

    def validate(self, fs):
        arrays = [np.asarray(v, float) for v in (self.frequencies, self.decay_seconds,
                                               self.sin_weights, self.cos_weights)]
        n = len(arrays[0])
        if n < 1 or n > 32 or any(v.shape != (n,) or not np.all(np.isfinite(v)) for v in arrays):
            raise ValueError('Invalid modal bank dimensions or values.')
        if np.any((arrays[0] <= 20) | (arrays[0] >= fs*.45)) or np.any((arrays[1] < .005) | (arrays[1] > 5)):
            raise ValueError('Modal frequencies/decays outside supported range.')


def modal_render(model: ModalModel, fs: int, length: int, gains=None):
    model.validate(fs)
    if not isinstance(length, (int,np.integer)) or length < 1: raise ValueError('Invalid length')
    t = np.arange(length)/fs
    g = np.ones(len(model.frequencies)) if gains is None else np.asarray(gains, float)
    if g.shape != model.frequencies.shape or not np.all(np.isfinite(g)):
        raise ValueError('Invalid modal gains')
    y = np.zeros(length)
    for f, tau, s, co, gain in zip(model.frequencies, model.decay_seconds,
                                  model.sin_weights, model.cos_weights, g):
        y += gain*np.exp(-t/tau)*(s*np.sin(2*np.pi*f*t)+co*np.cos(2*np.pi*f*t))
    return y


def fit_modal(x, fs, modes=8):
    """Fit one isolated mono impact with damped sinusoids. No separation of a mix.
    Uses spectral peaks and separable nonlinear least squares. Fit quality is
    returned, not silently treated as reliable causal recovery.
    """
    x = audio_array(x, fs)
    if x.ndim != 1: raise ValueError('Modal fit requires isolated mono audio.')
    if rms(x) < 1e-12 or len(x)/fs < .2: raise ValueError('Need at least .2 s of an audible isolated impact.')
    if not isinstance(modes, int) or not 1 <= modes <= 12: raise ValueError('modes must be 1..12')
    # Downsample for bounded-cost optimization, retaining <3.2kHz here.
    rate = min(fs, 8000)
    y = signal.resample_poly(x[:min(len(x),int(fs*.75))], rate, fs)
    t = np.arange(len(y))/rate
    fftn = max(16384, 2**int(np.ceil(np.log2(len(y)))))
    sp = np.abs(np.fft.rfft(y*np.exp(-t/.5), n=fftn))
    f = np.fft.rfftfreq(fftn, 1/rate)
    inds, _ = signal.find_peaks(sp, distance=max(1,int(30/(rate/fftn))))
    inds = inds[(f[inds] > 65) & (f[inds] < rate*.4)]
    if len(inds) < modes: raise ValueError('Insufficient separated spectral peaks for the requested fit.')
    freq = np.sort(f[inds[np.argsort(sp[inds])[-modes:]]])
    # Sparse evaluation includes both attack and tail.
    stride = max(1, len(y)//1400); tt=t[::stride]; yy=y[::stride]
    def basis(p, time):
        ff=p[:modes]; decay=np.exp(p[modes:])
        phase=2*np.pi*time[:,None]*ff[None,:]
        envelope=np.exp(-time[:,None]/decay[None,:])
        return np.concatenate([envelope*np.sin(phase), envelope*np.cos(phase)], axis=1)
    def residual(p):
        b=basis(p,tt); w=np.linalg.lstsq(b,yy,rcond=1e-8)[0]
        return b@w-yy
    p=np.r_[freq,np.full(modes,np.log(.16))]
    lo=np.r_[freq-12,np.full(modes,np.log(.012))]
    hi=np.r_[freq+12,np.full(modes,np.log(1.8))]
    res=optimize.least_squares(residual,p,bounds=(lo,hi),max_nfev=65,ftol=1e-8,xtol=1e-8)
    b=basis(res.x,t); w=np.linalg.lstsq(b,y,rcond=1e-8)[0]
    err=rms(b@w-y)/max(rms(y),1e-12)
    return ModalModel(res.x[:modes],np.exp(res.x[modes:]),w[:modes],w[modes:],err)


def contact_spectrum(freq, duration):
    # Unit-area half-sine contact, numerically integrated at 257 points.
    u=np.linspace(0,1,257)
    p=.5*np.pi*np.sin(np.pi*u)
    return np.trapezoid(p[None,:]*np.exp(-2j*np.pi*np.asarray(freq)[:,None]*duration*u),u,axis=1)


def power(x, fs: int, model: ModalModel, effort: float = .7, reference_contact_ms=.35):
    """POWER-CT: contact-duration counterfactual on ONE fitted modal impact.
    It does not infer watts, singer effort, mass or force. All these require
    assumptions/data beyond a single recording. Neutral preserves residual.
    Mode frequencies and decays remain fixed. At present this is amplitude
    reweighting of modes (contact hardness cue), not a validated power effect.
    """
    x=audio_array(x,fs)
    if x.ndim != 1: raise ValueError('POWER-CT currently accepts mono isolated impacts only.')
    e=bounded(effort,-1,1,'effort'); model.validate(fs)
    ref=bounded(reference_contact_ms,.03,2,'reference_contact_ms')/1000
    if e == 0 or rms(x)<1e-14: return x.copy()
    target=ref * 2**(-2.2*e)
    ratio=np.abs(contact_spectrum(model.frequencies,target))/np.maximum(np.abs(contact_spectrum(model.frequencies,ref)), .06)
    ratio=np.clip(ratio,10**(-12/20),10**(12/20))
    return x+modal_render(model,fs,len(x),ratio)-modal_render(model,fs,len(x))


def static_eq_match(reference, target, fs, smoothing_hz=75):
    """Adversarial whole-clip static zero-phase EQ fitted to target power spectrum.
    This is an ORACLE comparison fitted on the tested clip, not a fair trained
    generalizing competitor. Limits +/-12 dB. State this in every interpretation.
    """
    from scipy.ndimage import gaussian_filter1d
    x=audio_array(reference,fs); y=audio_array(target,fs)
    if x.shape != y.shape: raise ValueError('Shape mismatch')
    a=np.fft.rfft(x,axis=0); b=np.fft.rfft(y,axis=0)
    sigma=max(1, smoothing_hz/(fs/len(x)))
    ap=gaussian_filter1d(np.abs(a)**2,sigma,axis=0)
    bp=gaussian_filter1d(np.abs(b)**2,sigma,axis=0)
    ratio=np.sqrt((bp+np.max(bp)*1e-9)/(ap+np.max(ap)*1e-9+1e-30))
    return np.fft.irfft(a*np.clip(ratio,.25,4),n=len(x),axis=0)
