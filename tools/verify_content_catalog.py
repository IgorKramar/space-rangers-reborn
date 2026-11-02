#!/usr/bin/env python3
"""Verify catalog completeness and parser adapters against private local inputs."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
from collections import Counter
import json
from pathlib import Path
import struct
import sys
from catalog_game_content import (digest, file_digest, leaves, legacy_scr_schema,
                                  read_schema, dump)

def reconcile(expected, declared, label):
    expected=set(expected);declared=list(declared)
    if not expected:raise AssertionError(f"Empty expected inventory: {label}")
    if len(declared)!=len(set(declared)):raise AssertionError(f"Duplicate manifest entries: {label}")
    missing=expected-set(declared);extra=set(declared)-expected
    if missing or extra:raise AssertionError(f"Inventory mismatch {label}: missing={len(missing)}, extra={len(extra)}")


def verify_quest_graph(quest, label):
    ids=[location['id'] for location in quest['locations']]
    if len(ids)!=len(set(ids)):
        raise AssertionError(f"Duplicate QMM location IDs: {label}")
    if len(ids)!=quest['locations_cnt'] or len(quest['jumps'])!=quest['jumps_cnt']:
        raise AssertionError(f"QMM graph count mismatch: {label}")
    known=set(ids)
    for jump in quest['jumps']:
        if len(jump['from_to'])!=2 or any(endpoint not in known for endpoint in jump['from_to']):
            raise AssertionError(f"Invalid QMM jump endpoints: {label}, jump={jump['id']}")


def main():
    if not __debug__:
        raise RuntimeError("Run verification without Python optimization (-O)")
    ap=argparse.ArgumentParser();ap.add_argument("--ranger-tools",type=Path,required=True)
    ap.add_argument("--private-out",type=Path,required=True);ap.add_argument("--export-out",type=Path,required=True)
    ap.add_argument("--install",type=Path,required=True)
    a=ap.parse_args();sys.path.insert(0,str(a.ranger_tools.resolve()))
    # Completeness comes from installation inventory, not only exported rows.
    sources=json.loads((a.export_out/'resource-sources.json').read_text())
    installed=[p.relative_to(a.install).as_posix() for p in a.install.rglob('*')
               if p.is_file() and p.suffix.lower() in {'.dat','.pkg'}]
    reconcile(installed,[s['source'] for s in sources],'DAT/PKG sources')
    entries=json.loads((a.export_out/'archive-entry-index.json').read_text())
    manifests={'.scr':json.loads((a.export_out/'script-payloads.json').read_text()),
               'quest':json.loads((a.export_out/'text-quest-payloads.json').read_text())}
    for kind,rows in manifests.items():
        extensions={'.scr'} if kind=='.scr' else {'.qm','.qmm'}
        expected=[(r['archive'],r['path']) for r in entries if Path(r['path']).suffix.lower() in extensions]
        reconcile(expected,[(r['archive'],r['path']) for r in rows],kind+' payload manifest')
        raw_expected=[];decoded_expected=[]
        for row in rows:
            assert row['status']=='decoded',row['path']
            relative=Path(row['archive'].replace('/','__'))/Path(row['path']).name
            raw=a.private_out/'payloads'/relative
            decoded=a.private_out/'decoded'/relative.with_suffix(relative.suffix+'.json')
            assert raw.is_file() and decoded.is_file(),row['path']
            assert file_digest(raw)==row['sha256'],row['path']
            raw_expected.append(relative.as_posix());decoded_expected.append(relative.with_suffix(relative.suffix+'.json').as_posix())
        raw_actual=[p.relative_to(a.private_out/'payloads').as_posix() for p in (a.private_out/'payloads').rglob('*')
                    if p.is_file() and p.suffix.lower() in extensions]
        decoded_actual=[p.relative_to(a.private_out/'decoded').as_posix() for p in (a.private_out/'decoded').rglob('*.json')
                        if Path(p.stem).suffix.lower() in extensions]
        reconcile(raw_expected,raw_actual,kind+' private raw files')
        reconcile(decoded_expected,decoded_actual,kind+' private decoded files')
    from rangers.scr import SCR
    from rangers.pkg import PKG,PKG_RAW,PKG_DIR
    from rangers.std.buffer import IBuffer
    from rangers.std.dataclass import _memo_stack
    assert list(leaves({"Text":["a","b"]})) == [(('Text','[0]'),'a'),(('Text','[1]'),'b')]
    assertions=["installation inventory equals source manifest", "all expected archive scenario payloads have private raw and decoded files", "duplicate DAT parameters retain distinct positional paths"]
    scripts=[];versions=Counter();roundtrips=0;truncations=0
    for p in sorted((a.private_out/"payloads"/"DATA__scripts.pkg").iterdir()):
        payload=p.read_bytes();v=struct.unpack_from("<I",payload)[0]
        schema=legacy_scr_schema(v) if v in {5,6} else SCR
        data=read_schema(schema,payload);versions[v]+=1
        if v in {5,6}:
            assert schema.write_bytes(data)==payload,p.name
            roundtrips+=1
        baseline=len(_memo_stack)
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                read_schema(schema,payload[:-1])
        except Exception:
            truncations+=1
        else:raise AssertionError("truncated SCR unexpectedly accepted")
        assert len(_memo_stack)==baseline,"reader leaked memo stack on error"
        scripts.append(p.name)
    assertions += ["all SCR consume entire payload", "legacy SCR byte-exact roundtrip",
                   "truncated SCR rejected and memo cleaned"]
    # Synthetic Cyrillic archive filename exercises legacy CP1251 decoding.
    archive=PKG('<root>',PKG_DIR,[PKG('test.bin',PKG_RAW,b'fixture')])
    data=bytearray(archive.to_bytes(root=True))
    data[24:87]='ТЕСТ.BIN'.encode('cp1251').ljust(63,b'\0')
    data[87:150]='тест.bin'.encode('cp1251').ljust(63,b'\0')
    class B(IBuffer):
        def read_str(self,length=None):
            assert length is not None
            return self.read(length).decode('cp1251')
    parsed=PKG.from_buffer(B(data),root=True)
    assert parsed.data[0].name=='тест.bin' and parsed.data[0].data==b'fixture'
    assertions.append("synthetic CP1251 PKG preserves name and payload")
    payloads=json.loads((a.export_out/'text-quest-payloads.json').read_text())
    for meta in payloads:
        private=a.private_out/'decoded'/meta['archive'].replace('/','__')/(Path(meta['path']).name+'.json')
        q=json.loads(private.read_text())
        verify_quest_graph(q,meta['path'])
    assertions.append("QMM location IDs unique, declared graph counts match, and jump endpoints exist")
    sources=json.loads((a.export_out/'resource-sources.json').read_text())
    for source in sources:
        assert source['status'] in {'decoded','indexed'},source['source']
        assert file_digest(a.install/source['source'])==source['sha256'],source['source']
    assertions.append("source hashes unchanged after extraction")
    entries=json.loads((a.export_out/'archive-entry-index.json').read_text())
    actual=Counter(x['archive'] for x in entries)
    assert all(s['entries']==actual[s['source']] for s in sources if s['source'].endswith('.pkg'))
    names=json.loads((a.export_out/'location-name-pools.json').read_text())
    assert len({(x['kind'],x['group'],x['id']) for x in names})==len(names)
    assertions += ["every PKG entry reconciles with archive counts", "location pool IDs unique within source group"]
    report={'status':'passed','checks':assertions,'script_versions':dict(versions),'script_payloads':len(scripts),
            'legacy_byte_exact_roundtrips':roundtrips,'rejected_truncated_scripts':truncations,
            'quest_payloads':len(payloads),'quest_graph_anomalies':[],
            'unchanged_source_hashes':len(sources)}
    dump(a.export_out/'resource-verification.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
