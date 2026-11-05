import pathlib,subprocess,json,hashlib,re,ast,sys,os,stat
q=pathlib.Path(__file__).parent;repo=pathlib.Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch');run=pathlib.Path((q/'b-run-root.path').read_text().strip());m=json.loads((run/'manifest.json').read_text());phase=sys.argv[1]
assert m['task']=='ARCH-BE-008' and m['host']=='127.0.0.1' and m['port']==13388 and m['database']=='arch_be008_plan' and m['root']==str(run)
resources={}
for kind,name in [('container','aiis-arch-be008-mysql'),('network','aiis-arch-be008-net'),('volume','aiis-arch-be008-mysql-data')]:
 fmt='{{json .Config.Labels}}' if kind=='container' else '{{json .Labels}}';lab=json.loads(subprocess.check_output(['docker',kind,'inspect','--format',fmt,name],text=True));assert lab['task']=='ARCH-BE-008' and lab['runId']==m['runId'];resources[name]=lab
cid=subprocess.check_output(['docker','container','inspect','--format','{{.Id}}',m['container']],text=True).strip();assert cid==m['containerId']
def sql(query):
 p=subprocess.run(['docker','exec','-i',m['container'],'mysql','--defaults-extra-file=/run/secrets/root_client','--default-character-set=utf8mb4','--batch','--skip-column-names',m['database']],input=query,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert p.returncode==0;return p.stdout
cols=sql("SELECT column_name,column_type,is_nullable,IF(column_default IS NULL,'NULL',column_default),extra FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='plans' ORDER BY ordinal_position;");columns=[line.split('\t') for line in cols.splitlines()]
migration=repo/'backend/alembic/versions/20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py';tree=ast.parse(migration.read_text());create=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='create_table' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='plans');expected=[]
for c in create.args[1:]:
 if not isinstance(c,ast.Call) or not isinstance(c.func,ast.Attribute) or c.func.attr!='Column':continue
 name=c.args[0].value;t=c.args[1];kw={x.arg:ast.literal_eval(x.value) for x in t.keywords};kind=t.func.attr;ty={'Integer':'int','SmallInteger':'smallint','DateTime':'datetime'}.get(kind)
 if kind=='String':ty='varchar('+str(kw['length'])+')'
 if kind=='Numeric':ty='decimal('+str(kw['precision'])+','+str(kw['scale'])+')'
 nullable=next(x.value.value for x in c.keywords if x.arg=='nullable');assert all(x.arg!='server_default' for x in c.keywords);expected.append([name,ty,'YES' if nullable else 'NO','NULL','auto_increment' if name=='id' else ''])
assert columns==expected
fixture=(repo/'backend-dotnet/tests/infra/plans.sql').read_text();fixturecols=re.findall(r'^  `([^`]+)` (\w+(?:\([^)]*\))?)(?: NOT NULL| NULL)',fixture,re.M);assert [(n,t.lower().replace('datetime(0)','datetime')) for n,t in fixturecols]==[(c[0],c[1]) for c in columns]
idx=sql("SELECT index_name,non_unique,column_name FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='plans' ORDER BY index_name;");assert sorted(line.split('\t') for line in idx.splitlines())==sorted([['PRIMARY','0','id'],['ix_plans_coil_no','0','coil_no'],['ix_plans_id','1','id'],['ix_plans_priority','1','priority'],['ix_plans_status','1','status']])
tables=sql('SHOW TABLES;');assert tables.strip()=='plans';versiontime=sql('SELECT VERSION(),@@global.time_zone,@@session.time_zone,TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP,CURRENT_TIMESTAMP);');assert versiontime.strip()=='8.4.6\t+08:00\t+08:00\t28800'
grants=sql("SHOW GRANTS FOR 'arch_be008_app'@'%';");assert 'GRANT SELECT, INSERT ON `arch_be008_plan`.*' in grants and all(x not in grants for x in ['ALL PRIVILEGES','DELETE','UPDATE','CREATE'])
rows=sql('SELECT * FROM plans ORDER BY id;');n=int(sql('SELECT COUNT(*) FROM plans;'));schema=re.sub(r' AUTO_INCREMENT=[0-9]+','',sql('SHOW CREATE TABLE plans;'))
if phase=='before':assert n==0
else:assert schema==json.loads((q/'db-before.json').read_text())['normalizedSchema']
for label,data in [('columns',cols),('indexes',idx),('readback',rows)]: (q/('db-'+phase+'-'+label+'.tsv')).write_text(data)
summary={'phase':phase,'task':'ARCH-BE-008','runId':m['runId'],'containerId':cid,'resources':resources,'rootMode':oct(stat.S_IMODE(run.stat().st_mode)),'secretFileModes':{name:oct(stat.S_IMODE((run/name).stat().st_mode)) for name in ['root-password','app-password','fixture-password','app-connection','fixture-connection']},'serverTime':versiontime.strip(),'imageDigest':m['imageDigest'],'imageArchitecture':m['imageArchitecture'],'columnsExactMigrationAndFixture':True,'columns':columns,'indexes':idx.splitlines(),'tables':['plans'],'grants':grants.splitlines(),'rows':n,'rowsSHA256':hashlib.sha256(rows.encode()).hexdigest(),'normalizedSchema':schema};(q/('db-'+phase+'.json')).write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ['phase','runId','rootMode','rows','columnsExactMigrationAndFixture','serverTime','imageDigest','imageArchitecture']}))
