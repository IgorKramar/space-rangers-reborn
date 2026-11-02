#!/usr/bin/env python3
"""Read-only inventory of a locally owned SRHD installation.

Requires a separate denballakh/ranger-tools checkout, pinned in metadata.
Original texts and decoded binaries go ONLY to --private-out outside this repo.
Export contains names, IDs, numeric facts, references, counts and hashes.
SCR6 adaptation follows source/script/aScript.pas (1d1835a, lines 3105–3688).
No game code, scripts, assets, or executables are executed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gc
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

PARSER_COMMIT = "b3c0ce20d1cf61b030f3c33482d09b91500b75c6"
SAFE_FIELDS = set("Access Dif Genre Group Image Length Map Race ShipType Equipments Priority Owner Cost Size Year Probability Level Type Kind Status GovernmentAward InThisSystem PlanetRace ShipRace FromRace ToRace ShipType Weapon Artefact Radar Scaner Droid Hook Forsage Def Name Name2".split())
NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def leaves(value, parts=()):
    """Preserve duplicate parameters as positional list occurrences."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from leaves(v, (*parts, k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from leaves(v, (*parts, f"[{i}]"))
    else:
        yield parts, value


def safe_facts(v):
    if not isinstance(v, dict):
        return {}
    return {k: x for k, x in v.items() if isinstance(x, str) and
            (NUMBER.fullmatch(x) or k in SAFE_FIELDS)}


def at(tree, path, default=None):
    try:
        for k in path.split("."):
            tree = tree[k]
        return tree
    except (KeyError, TypeError):
        return default


def read_schema(schema, payload):
    # Upstream read_with_memo does not pop on exception. Always clean the stack.
    from rangers.std.buffer import IBuffer
    from rangers.std.dataclass import Memo, push_memo, pop_memo
    buf = IBuffer(payload)
    push_memo(Memo())
    try:
        result = schema.read(buf)
    finally:
        pop_memo()
    if buf.pos != len(buf):
        raise ValueError(f"Unread bytes: {len(buf) - buf.pos}")
    return result


def legacy_scr_schema(version=6):
    """Layout adapter; retain unknown pre-v7 fields and never run script text."""
    from rangers import scr as s
    from rangers.std.dataclass import (NamedSequence as N, List as L,
        Sequence as S, UInt32 as U, Int32 as I, Bool as B, Float as F,
        WStr as W, AnyOf, DNone)
    ship = N(count=I, owner=U, type=U, is_player=B, speed=s.MinMax,
             weapon=I, cargohook=I, emptyspace=I, legacy_before_status=S(I,I),
             status=s.Status, legacy_after_status=S(I,I), strength=S(F,F), ruins=W)
    link = N(end_star=I, legacy_1=I, distance=s.MinMax,
             legacy_2=S(I,I,I), is_hole=B)
    star = N(name=W, constellation=I, legacy_flag=B, no_kling=B,
             no_come_kling=B, starlinks=L(link), planets=L(s.Planet), ships=L(ship))
    group = N(name=W, planet=W, state=I, owner=U, type=U, count=s.MinMax,
              speed=s.MinMax, weapon=I, cargohook=I, emptyspace=I,
              legacy_before_player=I, add_player=B, legacy_before_status=S(I,I,I,I),
              status=s.Status, search_distance=I, dialog=W, strength=S(F,F), ruins=W)
    return N(version=AnyOf(U,{version}), localvars_offset=U, globalvars=L(s.Var),
             globalcode=W, localvars=L(s.Var), constellations=I, stars=L(star),
             places=L(s.Place), items=L(s.Item), groups=L(group),
             grouplinks=L(s.GroupLink), initcode=W, turncode=W, dialogbegincode=W if version>5 else DNone,
             states=L(s.State), dialogs=L(s.Dialog), dialog_messages=L(s.DialogMsg),
             dialog_answers=L(s.DialogAnswer))


def write_catalogs(out, ru, en, main, cache, robots=None):
    counts = {}
    def emit(name, rows):
        dump(out / (name + ".json"), rows)
        counts[name] = len(rows)
    def ref(path):
        return {"source": "CFG/Rus/Lang.dat", "block": path}
    def named(path, subtype="definition"):
        block = at(ru,path,{})
        rows = []
        for key, value in block.items():
            if isinstance(value,dict) and isinstance(value.get("Name"),str):
                p=path+"."+key
                rows.append({"id":key,"name_ru":value["Name"],
                             "name_en":at(en,p+".Name"),"kind":subtype,
                             "facts":safe_facts(value),**ref(p)})
        return rows
    names=[]
    for kind,path in [("star","Star"),("planet","PlanetName"),("station","RuinName")]:
        for parts,value in leaves(at(ru,path)):
            if not isinstance(value,str): continue
            p=".".join((path,*parts)); english=at(en,p)
            name,sep,style=value.partition(",") if kind=="star" else (value,"","")
            names.append({"kind":kind,"group":parts[0] if len(parts)>1 else "Star",
                          "id":parts[-1],"name_ru":name,
                          "name_en":english.partition(",")[0] if kind=="star" and isinstance(english,str) else english,
                          "resource_suffix":style,"classification":"localized_name_pool",
                          **ref(p)})
    emit("location-name-pools",names)
    with (out/"location-name-pools.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(names[0]));writer.writeheader();writer.writerows(names)
    md=["# Названия звёзд, планет и станций из ресурсов игры","",
        "Это полные русские пулы установленной базовой локализации, а не карта конкретной партии. "
        "Индекс — ключ ресурса. Наличие названия не доказывает появление объекта в каждой игре. "
        "Группа Solar содержит девять названий; генератор исходной ревизии использует семь планет. "
        "Сюжетные псевдонимы и названия текстовых квестов учитываются отдельно.",""]
    for kind in ["star","planet","station"]:
        for group in sorted({r["group"] for r in names if r["kind"]==kind}):
            rows=[r for r in names if r["kind"]==kind and r["group"]==group]
            md += [f"## {kind} / {group} — {len(rows)}", "", "| ID | Название |", "|---|---|"]
            md += [f"| {r['id']} | {r['name_ru'].replace('|',' / ')} |" for r in rows]
            md += [""]
    (out/"location-name-pools.md").write_text("\n".join(md),encoding="utf-8")
    for name,path in [("hull-types","HullType"),("micromodules","MicroModuls"),
                      ("artifacts","Artefacts"),("quest-and-special-items","UselessItems"),
                      ("text-quest-cards","PlanetQuest.List"),("rts-map-cards","RobotsMap"),
                      ("arcade-map-cards","ABMap")]:
        rows=named(path)
        if path=="PlanetQuest.List":
            for row in rows:row["resource"]=at(ru,"PlanetQuest.PlanetQuest."+row["id"])
        emit(name,rows)
    rows=[]
    for section in ["Goods","Weapon"]:
        path=f"Items.{section}.Name"
        for key,value in at(ru,path).items():
            rows.append({"id":key,"category":section,"name_ru":value,
                         "name_en":at(en,path+"."+key),**ref(path+"."+key)})
    for section,values in ru["Items"].items():
        if isinstance(values,dict) and isinstance(values.get("Type"),dict):
            for key,value in values["Type"].items():
                path=f"Items.{section}.Type.{key}"
                rows.append({"id":key,"category":section,"name_ru":value,
                             "name_en":at(en,path),"name_template":values.get("Name"),**ref(path)})
    rows.extend({**row,"category":"Satellite"} for row in named("Items.Satellite"))
    emit("equipment-goods-and-weapons",rows)
    character=[]
    for parts,v in leaves(ru["ShipName"]):
        p="ShipName."+".".join(parts)
        character.append({"id":".".join(parts),"name_ru":v,"name_en":at(en,p),**ref(p)})
    emit("captain-name-pools",character)
    scripts=[]
    for key,value in ru["Script"].items():
        scripts.append({"id":key,"resource":at(cache,"Script."+key),
                        "activation":at(main,"Data.Script."+key),
                        "localized_parameters":sum(1 for _ in leaves(value)),**ref("Script."+key)})
    emit("script-registry",scripts)
    # Every base localization section is indexed without reproducing narrative text.
    sections=[]
    for k,v in ru.items():
        sections.append({"id":k,"children":len(v) if isinstance(v,(dict,list)) else 0,
                         "leaf_parameters":sum(1 for _ in leaves(v)),**ref(k)})
    emit("localization-sections",sections)
    # Retain enum values and names; long dialogue/news/quest prose stays private.
    enumerations=[]
    for section in ["Race","Economy","Goverment","Rank","RankPirate","Reward",
                    "Achievements","Illness","Programms","Skills","ShipType",
                    "ShipCharacter","ShipCharacterFemale","Relations","Month"]:
        for parts,v in leaves(ru.get(section,{})):
            key=parts[-1] if parts else ""
            if isinstance(v,str) and len(v)<100 and (len(parts)==1 or key in {"Name","Name2","Title"} or parts[0]=="Name"):
                p=".".join((section,*parts))
                enumerations.append({"category":section,"id":".".join(parts),
                                     "name_ru":v,"name_en":at(en,p),**ref(p)})
    emit("social-ranks-programs-and-enums",enumerations)
    for name,path in [("ranger-ranks","Rank"),("pirate-ranks","RankPirate"),
                      ("medals","Reward"),("achievement-definitions","Achievements"),
                      ("diseases","Illness.Illness"),("extra-diseases","Illness.ExtraIllness"),
                      ("stimulants","Illness.Stimulant"),("anti-dominator-programs","Programms"),
                      ("skills","Skills")]:
        emit(name,named(path))
    missions=[]
    for kind in ["DefShip","DefSystem","KillShip","SendLetter"]:
        for key,v in ru["Quest"][kind].items():
            if not key.isdecimal() or not isinstance(v,dict):continue
            path=f"Quest.{kind}.{key}"
            missions.append({"id":key,"family":kind,"facts":safe_facts(v),
                             "parameters":sum(1 for _ in leaves(v)),**ref(path)})
    emit("government-mission-templates",missions)
    narrative=[]
    for family in ["GalaxyNews","Talk","GovGreetings","ShipGreetings","PlanetCongratulations",
                   "Script","Quest","FormGov","FormRuins","FormRuinsRC","FormRuinsSB"]:
        for parts,v in leaves(ru.get(family,{})):
            path=".".join((family,*parts))
            narrative.append({"family":family,"id":".".join(parts),"characters":len(str(v)),
                              "substitutions":sorted(set(re.findall(r"<([A-Za-z][A-Za-z0-9_]*)>",str(v)))),**ref(path)})
    emit("narrative-template-index",narrative)
    if robots:
        rows=[]
        for section in ["AIRobotType","Chars","Models","Price","Weapons","RobotSpawn","Side"]:
            for parts,v in leaves(robots["da"].get(section,{})):
                if isinstance(v,str) and (NUMBER.fullmatch(v) or section in {"AIRobotType","Side"} or v.startswith("WEAPON_")):
                    rows.append({"category":section,"id":".".join(parts),"value":v,
                                 "source":"CFG/Rus/robots.dat","block":"da."+section+"."+".".join(parts)})
        emit("rts-mechanical-parameters",rows)
        rows=[]
        for section in ["Buildings","Items","RobotNames","Turrets"]:
            for parts,v in leaves(robots["da"]["AllLabels"].get(section,{})):
                if isinstance(v,str) and len(v)<=100:
                    rows.append({"category":section,"id":".".join(parts),"name_ru":v,
                                 "source":"CFG/Rus/robots.dat","block":"da.AllLabels."+section+"."+".".join(parts)})
        emit("rts-name-labels",rows)
    return counts


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--install",type=Path,required=True)
    ap.add_argument("--ranger-tools",type=Path,required=True)
    ap.add_argument("--rangers-utils",type=Path,required=True)
    ap.add_argument("--private-out",type=Path,required=True)
    ap.add_argument("--export-out",type=Path,required=True)
    args=ap.parse_args()
    install=args.install.resolve(); private=args.private_out.resolve(); out=args.export_out.resolve()
    project=Path(__file__).resolve().parents[1]
    for path in (private,out):
        if path.is_relative_to(install) or install.is_relative_to(path):
            ap.error("Output must not overlap the installation")
    if private.is_relative_to(out) or out.is_relative_to(private):
        ap.error("Private and export output directories must not overlap")
    if private.is_relative_to(project):ap.error("Private original data must stay outside the project")
    parser=args.ranger_tools.resolve()
    pin=subprocess.check_output(["git","-C",str(parser),"rev-parse","HEAD"],text=True).strip()
    if pin!=PARSER_COMMIT:ap.error(f"Expected ranger-tools {PARSER_COMMIT}, got {pin}")
    sys.path.insert(0,str(parser))
    from rangers.dat import DAT
    from rangers.pkg import PKG
    from rangers.qm import QuestObj
    from rangers.scr import SCR
    private.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    sources=[]; dat_index=[]; dat_data={}; errors=[]
    for path in sorted(install.rglob("*.dat")):
        rel=path.relative_to(install).as_posix();before=path.stat()
        record={"source":rel,"bytes":before.st_size,"sha256":file_digest(path),"scope":"base" if not rel.startswith("Mods/") else "optional_mod"}
        try:
            if path.read_bytes()[:4]==b"STRG":
                result=subprocess.run([sys.executable,str(Path(__file__).with_name("catalog_rts_storage.py")),
                                       "--rangers-utils",str(args.rangers_utils.resolve()),"--file",str(path)],
                                      check=True,capture_output=True,text=True)
                data=json.loads(result.stdout);fmt="STRG1/ZL03"
            else:
                decoded=DAT.from_dat(path);data=decoded.to_dict();fmt=decoded.fmt
            dat_data[rel]=data
            dump(private/"dat"/(rel.replace("/","__")+".json"),data)
            raw=[]
            for parts,value in leaves(data):
                p=".".join(parts);raw.append({"path":p,"value":value})
                dat_index.append({"source":rel,"path":p,"type":type(value).__name__,
                                  "characters":len(str(value)),"value_sha256":digest(str(value).encode())})
            dump(private/"dat-flat"/(rel.replace("/","__")+".json"),raw)
            record.update(status="decoded",format=fmt,top_blocks=list(data),leaf_parameters=len(raw))
        except Exception as exc:
            record.update(status="failed",error=f"{type(exc).__name__}: {exc}")
            errors.append({"source":rel,"stage":"dat","error":record["error"]})
        record["unchanged_stat"]=before.st_size==path.stat().st_size and before.st_mtime_ns==path.stat().st_mtime_ns
        sources.append(record)
    dump(out/"dat-parameter-index.json",dat_index)
    counts=write_catalogs(out,dat_data["CFG/Rus/Lang.dat"],dat_data["CFG/Eng/Lang.dat"],dat_data["CFG/Main.dat"],dat_data["CFG/CacheData.dat"],dat_data.get("CFG/Rus/robots.dat"))
    archive_entries=[]; quest_meta=[]; script_meta=[]; legacy={v:legacy_scr_schema(v) for v in (5,6)}
    def walk(node,parts=()):
        if node.type==3:
            for child in node.data:yield from walk(child,parts if node.name=="<root>" else (*parts,node.name))
        else:yield "/".join((*parts,node.name)),node
    for path in sorted(install.rglob("*.pkg")):
        rel=path.relative_to(install).as_posix();before=path.stat()
        record={"source":rel,"bytes":before.st_size,"sha256":file_digest(path),"scope":"base" if not rel.startswith("Mods/") else "optional_mod"}
        try:
            try:
                archive=PKG.from_file(path);record["filename_encoding"]="utf-8"
            except UnicodeDecodeError:
                # PKG names in this legacy archive include Cyrillic CP1251 bytes.
                from rangers.std.buffer import IBuffer
                class CP1251Buffer(IBuffer):
                    def read_str(self,length=None):
                        if length is None:raise ValueError("Only fixed PKG names supported")
                        return self.read(length).decode("cp1251")
                archive=PKG.from_buffer(CP1251Buffer(path.read_bytes()),root=True)
                record["filename_encoding"]="cp1251"
            n=0; extensions=Counter()
            for internal,node in walk(archive):
                n+=1;ext=Path(internal).suffix.lower();extensions[ext]+=1
                entry={"archive":rel,"path":internal,"type":node.type,"stored_bytes":len(node.data),
                       "unpacked_bytes":node.decompressed_size(),"stored_sha256":digest(node.data),"scope":record["scope"]}
                archive_entries.append(entry)
                if ext not in {".qm",".qmm",".scr"}:continue
                node.decompress();payload=node.data
                # Never trust archive paths as filesystem destinations.
                stem=Path(internal).name
                rawpath=private/"payloads"/rel.replace("/","__")/stem
                rawpath.parent.mkdir(parents=True,exist_ok=True);rawpath.write_bytes(payload)
                meta={"archive":rel,"path":internal,"sha256":digest(payload),"bytes":len(payload),"scope":record["scope"]}
                try:
                    if ext==".scr":
                        version=struct.unpack_from("<I",payload)[0]
                        meta["version"]=version
                        data=read_schema(legacy.get(version,SCR),payload)
                        meta.update(status="decoded",counts={k:len(v) for k,v in data.items() if isinstance(v,list)})
                        meta["bindings"]={k:[{a:b for a,b in x.items() if a in {"name","constellation","star","planet","place","type","kind","owner","useless","level","size"}} for x in data[k]] for k in ["stars","places","items","groups"]}
                        meta["star_planet_bindings"]=[{"star_alias":x["name"],"planets":[{a:b for a,b in p.items() if a!="dialog"} for p in x["planets"]]} for x in data["stars"]]
                    else:
                        data=read_schema(QuestObj,payload)
                        meta.update(status="decoded",version=data["version"],header={k:v for k,v in data["header"].items() if k!="changelog"},
                                    parameters=len(data["parameters"]),locations=len(data["locations"]),jumps=len(data["jumps"]))
                        meta["scenario_placeholders"]={k:data[k] for k in ["tostar","toplanet","fromstar","fromplanet"]}
                    dump(private/"decoded"/rel.replace("/","__")/(stem+".json"),data)
                except Exception as exc:
                    meta.update(status="failed",error=f"{type(exc).__name__}: {exc}")
                    errors.append({"source":rel+":"+internal,"stage":"payload","error":meta["error"]})
                (script_meta if ext==".scr" else quest_meta).append(meta)
            record.update(status="indexed",entries=n,extensions=dict(extensions))
            del archive;gc.collect()
        except Exception as exc:
            record.update(status="failed",error=f"{type(exc).__name__}: {exc}")
            errors.append({"source":rel,"stage":"pkg","error":record["error"]})
        record["unchanged_stat"]=before.st_size==path.stat().st_size and before.st_mtime_ns==path.stat().st_mtime_ns
        sources.append(record)
        print(f"{rel}: {record['status']} ({record.get('entries',0)} files)",flush=True)
    dump(out/"archive-entry-index.json",archive_entries)
    dump(out/"text-quest-payloads.json",quest_meta)
    dump(out/"script-payloads.json",script_meta)
    dump(out/"resource-sources.json",sources)
    report={"parser_repository":"https://github.com/denballakh/ranger-tools","parser_commit":pin, "storage_parser_repository":"https://github.com/murgesku/rangers-utils",
            "storage_parser_commit":"c37e2f292cb335400d244eaba82b6c32dc19b281",
            "originals_location":"private output outside public repository", "catalog_counts":counts,
            "dat_files":sum(s["source"].endswith(".dat") for s in sources),
            "pkg_files":sum(s["source"].endswith(".pkg") for s in sources),
            "archive_files":len(archive_entries),"quest_payloads":len(quest_meta),"script_payloads":len(script_meta),
            "successful_quests":sum(r["status"]=="decoded" for r in quest_meta),
            "successful_scripts":sum(r["status"]=="decoded" for r in script_meta),
            "all_source_stats_unchanged":all(r["unchanged_stat"] for r in sources),"errors":errors,
            "count_notes":{
                "hull_types":"90 named definitions; 92 children minus CountHullType=150 and SeriesName UI template. Declared 150 is not actual definition count.",
                "micromodules":"274 named definitions; 276 children minus AddToItem confirmation and Name category label.",
                "artifacts":"32 named definitions; 36 children minus empty CustomArtefacts, NumericValues and 2 interface strings.",
                "equipment":"96 rows = 8 goods + 18 weapon names + 64 technology tier labels (8 categories × 8) + 6 probes. Not 96 finished item instances.",
                "text_quests":"320 payloads = 80 Russian + 80 English base + 160 optional German/Spanish translations or fallback English. Translation variants are not unique quests.",
                "archive_vs_cards":"Map/scenario cards are localization entries; asset presence does not establish gameplay reachability.",
                "captains":"1803 pool parameters, not 1803 persistent people in a campaign."},
            "limitations":["Resource name pools are not generated campaign objects", "Optional mod files are indexed separately; not assumed active",
                "Names and numeric definitions are cataloged, complete original prose is private", "Asset payloads (images/audio/maps) are indexed, not all semantically decoded",
                "Successful binary decoding is not complete narrative analysis or proof of reachability", "No saves loaded and no game launched",
                "SCR bindings are script aliases, not necessarily displayed world names", "QMM placeholder names are quest-local context, not guaranteed galaxy systems"]}
    dump(out/"resource-extraction-coverage.json",report)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
