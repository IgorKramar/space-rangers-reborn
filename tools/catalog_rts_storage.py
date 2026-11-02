#!/usr/bin/env python3
"""Decode STRG robot config using the existing separately pinned reader.

This subprocess isolates rangers-utils from ranger-tools (same package name).
Only reads input. Output is original game data and must remain private.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

PIN="c37e2f292cb335400d244eaba82b6c32dc19b281"
def decode(path, parser):
    actual=subprocess.check_output(["git","-C",str(parser),"rev-parse","HEAD"],text=True).strip()
    if actual!=PIN:raise ValueError("Unexpected rangers-utils revision")
    sys.path.insert(0,str(parser))
    from rangers.storage import Storage
    storage=Storage.from_file(str(path))
    records={r.name:r for r in storage.records}
    if len(records)!=len(storage.records):raise ValueError("Duplicate storage record")
    seen=set()
    def block(name,ancestors=()):
        if name in ancestors:raise ValueError("Cyclic storage block")
        seen.add(name)
        record=records[name]
        cols={x.name:[b.decode("utf-16le") for b in x.datatable.entries] for x in record.items}
        if set(cols)!={"0","1","2","3"}:raise ValueError("Unexpected storage columns")
        if len(cols["0"])!=len(cols["1"]) or len(cols["2"])!=len(cols["3"]):raise ValueError("Unpaired storage columns")
        result={}
        pairs=list(zip(cols["0"],cols["1"]))+[(k,block(v,(*ancestors,name))) for k,v in zip(cols["2"],cols["3"])]
        for k,v in pairs:
            if k not in result:result[k]=v
            elif isinstance(result[k],list):result[k].append(v)
            else:result[k]=[result[k],v]
        return result
    roots={r.name:block(r.name) for r in storage.records if not r.name.isdecimal()}
    if seen!=set(records):raise ValueError("Unreachable storage records")
    return roots

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--rangers-utils",type=Path,required=True);ap.add_argument("--file",type=Path,required=True)
    a=ap.parse_args();print(json.dumps(decode(a.file,a.rangers_utils),ensure_ascii=False))
