"""Offline processor CLI. Writes a NEW WAV; refuses input overwrite."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import soundfile as sf
from .core import *


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('processor',choices=['bind','power','continuum'])
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--amount',type=float,default=.7)
    p.add_argument('--modes',type=int,default=6)
    p.add_argument('--max-change-db',type=float,default=6)
    p.add_argument('--target-lufs',type=float,default=-23)
    args=p.parse_args()
    if args.input.resolve()==args.output.resolve() or args.output.exists():
        p.error('Output must be a new file, different from the input.')
    x,fs=sf.read(args.input)
    if len(x)>fs*60: p.error('Prototype accepts at most 60 s to bound memory cost.')
    info={'processor':args.processor,'version':VERSION,'source':str(args.input),'noncausal':True}
    if args.processor=='bind': y=bind(x,fs,args.amount,args.max_change_db)
    elif args.processor=='continuum':y=continuum(x,fs,args.amount,max_change_db=args.max_change_db)
    else:
        if x.ndim!=1 or len(x)>fs*2: p.error('POWER-CT accepts ONE mono isolated impact, <=2 s, onset at sample zero.')
        model=fit_modal(x,fs,args.modes)
        info['fit_relative_error']=model.fit_relative_error
        info['modal_frequencies']=model.frequencies.tolist()
        if model.fit_relative_error>.35: p.error(f'Poor modal fit ({model.fit_relative_error:.3f}); refusing causal-looking output.')
        y=power(x,fs,model,args.amount)
    if rms(x)>1e-14:
        pair,target=normalize_group([x,y],fs,args.target_lufs)
        y=pair[1];info['target_lufs']=target
    args.output.parent.mkdir(parents=True,exist_ok=True)
    sf.write(args.output,y,fs,subtype='PCM_24')
    info['output']=str(args.output);info['warning']='Offline research output, not a validated perceptual transformation.'
    args.output.with_suffix('.json').write_text(json.dumps(info,indent=2))
    print(json.dumps(info,indent=2))

if __name__=='__main__':main()
